import logging
import datetime
import json
import asyncio
from sqlalchemy import select

from app.database import SyncSessionLocal
from app.models.spatial import Hotspot, Facility, MLClassificationEnum, ClassificationLog
from app.config import settings

logger = logging.getLogger(__name__)

async def process_hotspots_batch(hotspot_ids: list[int]):
    """
    Process a batch of ingested hotspots:
    1. Spatial enrichment (distance to industry)
    2. ML Classification via HuggingFace Gradio API call
    3. Save results
    """
    start_time = datetime.datetime.utcnow()
    logger.info(f"Processing batch of {len(hotspot_ids)} hotspots via HTTP Inference...")
    
    if not settings.huggingface_inference_url:
        logger.error("Cannot process batch, HUGGINGFACE_INFERENCE_URL not set.")
        return False
        
    enum_map = {
        "Industrial Fire": MLClassificationEnum.INDUSTRIAL_FIRE,
        "Forest Fire": MLClassificationEnum.FOREST_FIRE,
        "Gas Flare": MLClassificationEnum.GAS_FLARE,
        "Agricultural Burn": MLClassificationEnum.AGRICULTURAL_BURN,
        "Mining/Thermal": MLClassificationEnum.MINING_THERMAL,
        "Unclassified": MLClassificationEnum.UNCLASSIFIED
    }

    # --- PHASE 1: Build feature vectors (sync DB) ---
    features_list = []
    hotspot_data = []  # Store (id, index) for later update
    
    with SyncSessionLocal() as db:
        hotspots = db.query(Hotspot).filter(Hotspot.id.in_(hotspot_ids)).all()
        if not hotspots:
            return True
            
        for h in hotspots:
            query = select(Facility).order_by(
                Facility.geom.distance_centroid(h.geom)
            ).limit(1)
            nearest = db.execute(query).scalars().first()
            
            if nearest:
                h.nearest_facility_id = nearest.id
                h.dist_to_industry_m = 0.0
                industrial_type = nearest.facility_type
            else:
                h.dist_to_industry_m = 99999.0
                industrial_type = "unknown"
                
            h.persistence_hours = 0.0
            h.spatial_cluster_size = 1
            h.land_cover_class = "Unknown"
            
            feat = {
                "brightness": h.brightness,
                "frp": h.frp,
                "confidence": h.confidence,
                "pixel_area": h.pixel_area or 1.0,
                "dist_to_industry_m": h.dist_to_industry_m,
                "persistence_hours": h.persistence_hours,
                "recurrence_count": 1,
                "spatial_cluster_size": h.spatial_cluster_size,
                "spread_rate": 0.0,
                "month": h.acq_date.month,
                "hour": h.acq_date.hour,
                "bright_t31": h.bright_t31,
                "brightness_ratio": (h.brightness / h.bright_t31) if h.bright_t31 else 1.0,
                "daynight": h.daynight,
                "industrial_type": industrial_type,
                "land_cover_class": h.land_cover_class
            }
            features_list.append(feat)
            hotspot_data.append(h.id)
            
        db.commit()  # Save the enrichment updates

    # --- PHASE 2: Call HuggingFace (in a thread so we don't block the event loop) ---
    try:
        from gradio_client import Client
        
        base_url = settings.huggingface_inference_url.replace('/api/predict', '').replace('/run/predict', '').replace('/gradio_api', '')
        
        def _run_inference():
            logger.info(f"Connecting to Gradio API at {base_url} ...")
            client = Client(base_url)
            logger.info(f"Sending {len(features_list)} features for prediction...")
            return client.predict(
                features_json=json.dumps(features_list),
                api_name="/predict"
            )
        
        result_json_str = await asyncio.to_thread(_run_inference)
        
        predictions = json.loads(result_json_str).get("predictions", [])
        logger.info(f"Received {len(predictions)} predictions from ML model.")
            
    except Exception as e:
        logger.error(f"Error calling ML inference API: {e}", exc_info=True)
        return False
        
    # --- PHASE 3: Write classification results back to DB (sync, separate session) ---
    end_time = datetime.datetime.utcnow()
    exec_time = (end_time - start_time).total_seconds() * 1000.0
    
    with SyncSessionLocal() as db:
        hotspots = db.query(Hotspot).filter(Hotspot.id.in_(hotspot_data)).all()
        hotspot_map = {h.id: h for h in hotspots}
        
        classified_count = 0
        for i, hid in enumerate(hotspot_data):
            if i < len(predictions):
                h = hotspot_map.get(hid)
                if not h:
                    continue
                    
                pred = predictions[i]
                label_str = pred.get("label", "Unclassified")
                ml_enum_val = enum_map.get(label_str, MLClassificationEnum.UNCLASSIFIED)
                
                h.ml_label = ml_enum_val
                h.classification_confidence = float(pred.get("confidence", 0.0))
                
                if ml_enum_val != MLClassificationEnum.UNCLASSIFIED:
                    classified_count += 1
                
                log = ClassificationLog(
                    hotspot_id=h.id,
                    model_version="v1.0",
                    predicted_label=ml_enum_val,
                    probability_scores=json.dumps(pred.get("probabilities", [])),
                    execution_time_ms=exec_time / len(hotspot_data)
                )
                db.add(log)
                
                from app.services.alert_service import create_alert_if_needed
                create_alert_if_needed(db, h)
                
        db.commit()
        
    logger.info(f"Processed and classified {len(hotspot_ids)} hotspots ({classified_count} non-unclassified).")
    return True
