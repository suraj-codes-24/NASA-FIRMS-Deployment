import logging
import datetime
import httpx
import json
from sqlalchemy import select

from app.database import SyncSessionLocal
from app.models.spatial import Hotspot, Facility, MLClassificationEnum, ClassificationLog
from app.config import settings

logger = logging.getLogger(__name__)

async def process_hotspots_batch(hotspot_ids: list[int]):
    """
    Process a batch of ingested hotspots:
    1. Spatial enrichment (distance to industry)
    2. ML Classification via HuggingFace API call
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

    with SyncSessionLocal() as db:
        hotspots = db.query(Hotspot).filter(Hotspot.id.in_(hotspot_ids)).all()
        if not hotspots:
            return True
            
        features_list = []
        
        for h in hotspots:
            query = select(Facility).order_by(
                Facility.geom.distance_centroid(h.geom)
            ).limit(1)
            nearest = db.execute(query).scalars().first()
            
            if nearest:
                h.nearest_facility_id = nearest.id
                h.dist_to_industry_m = 0.0 # Placeholder for haversine
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
            
        # Call HuggingFace Gradio API
        try:
            from gradio_client import Client
            import ast
            import asyncio
            
            # Use the HF URL without any /api/predict suffixes for the client
            base_url = settings.huggingface_inference_url.replace('/api/predict', '').replace('/run/predict', '').replace('/gradio_api', '')
            
            def run_inference():
                client = Client(base_url)
                return client.predict(
                    features_json=json.dumps(features_list),
                    api_name="/predict"
                )
            
            # Run inference synchronously in a threadpool so we don't block FastAPI
            result_json_str = await asyncio.to_thread(run_inference)
            
            # The result is already a JSON string containing {"predictions": [...]}
            predictions = json.loads(result_json_str).get("predictions", [])
                
        except Exception as e:
            logger.error(f"Error calling ML inference API: {e}")
            return False
            
        end_time = datetime.datetime.utcnow()
        exec_time = (end_time - start_time).total_seconds() * 1000.0
        
        for i, h in enumerate(hotspots):
            if i < len(predictions):
                pred = predictions[i]
                label_str = pred.get("label", "Unclassified")
                ml_enum_val = enum_map.get(label_str, MLClassificationEnum.UNCLASSIFIED)
                
                h.ml_label = ml_enum_val
                h.classification_confidence = float(pred.get("confidence", 0.0))
                
                log = ClassificationLog(
                    hotspot_id=h.id,
                    model_version="v1.0",
                    predicted_label=ml_enum_val,
                    probability_scores=json.dumps(pred.get("probabilities", [])),
                    execution_time_ms=exec_time / len(hotspots)
                )
                db.add(log)
                
                from app.services.alert_service import create_alert_if_needed
                create_alert_if_needed(db, h)
                
        db.commit()
        
    logger.info(f"Processed and classified {len(hotspot_ids)} hotspots.")
    return True
