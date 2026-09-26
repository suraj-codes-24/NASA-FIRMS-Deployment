"""
IGNIS — Reclassify All Hotspots with Real Facility Data

Now that facilities are seeded, recompute dist_to_industry_m for each hotspot
and re-run the ML classification pipeline.

Usage (run inside Docker):
    docker exec ignis-backend python /app/reclassify_hotspots.py
"""

import sys
import os
import logging
import datetime
import math

sys.path.insert(0, "/app")

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("reclassify")

from sqlalchemy import select, func, text
from app.database import SyncSessionLocal
from app.models.spatial import Hotspot, Facility, MLClassificationEnum, ClassificationLog, Alert


def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate haversine distance in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def enrich_hotspots():
    """Enrich all hotspots with real distance-to-industry values."""
    logger.info("Phase 1: Enriching hotspots with facility proximity...")
    
    with SyncSessionLocal() as db:
        hotspots = db.query(Hotspot).all()
        logger.info(f"Total hotspots to enrich: {len(hotspots)}")
        
        # Build a spatial index of facility locations for quick lookup
        facilities = db.query(Facility.id, Facility.facility_type,
                              func.ST_X(Facility.geom).label('lon'),
                              func.ST_Y(Facility.geom).label('lat')).all()
        logger.info(f"Total facilities loaded: {len(facilities)}")
        
        enriched = 0
        for h in hotspots:
            # Find nearest facility using simple coordinate comparison
            # For a proper system we'd use PostGIS ST_Distance, but this is fast enough for ~1400 hotspots
            min_dist = 999999.0
            nearest_fac_id = None
            nearest_fac_type = "unknown"
            
            for fac in facilities:
                # Quick bounding box pre-filter (~1 degree = ~111km)
                if abs(h.latitude - fac.lat) > 1.0 or abs(h.longitude - fac.lon) > 1.0:
                    continue
                
                dist = haversine_km(h.latitude, h.longitude, fac.lat, fac.lon) * 1000  # convert to meters
                if dist < min_dist:
                    min_dist = dist
                    nearest_fac_id = fac.id
                    nearest_fac_type = fac.facility_type
            
            h.dist_to_industry_m = min_dist
            h.nearest_facility_id = nearest_fac_id
            enriched += 1
            
            if enriched % 200 == 0:
                logger.info(f"  ... enriched {enriched}/{len(hotspots)} (nearest: {min_dist:.0f}m, type: {nearest_fac_type})")
        
        db.commit()
        logger.info(f"Enrichment complete: {enriched} hotspots updated.")


def reclassify():
    """Re-run ML classification on all hotspots."""
    logger.info("Phase 2: Re-running ML classification pipeline...")
    
    # Import the ML task function directly (not via Celery)
    import numpy as np
    import pandas as pd
    import joblib
    
    MODEL_PATH = "/data/models/classifier_v1.joblib"
    
    logger.info(f"Loading ML model from {MODEL_PATH}...")
    model_artifact = joblib.load(MODEL_PATH)
    
    ensemble = model_artifact["ensemble"]
    feature_names = model_artifact["feature_names"]
    label_encoders = model_artifact["label_encoders"]
    target_encoder = model_artifact["target_encoder"]
    
    enum_map = {
        0: MLClassificationEnum.INDUSTRIAL_FIRE,
        1: MLClassificationEnum.FOREST_FIRE,
        2: MLClassificationEnum.GAS_FLARE,
        3: MLClassificationEnum.AGRICULTURAL_BURN,
        4: MLClassificationEnum.MINING_THERMAL,
        5: MLClassificationEnum.UNCLASSIFIED
    }
    
    with SyncSessionLocal() as db:
        hotspots = db.query(Hotspot).all()
        logger.info(f"Classifying {len(hotspots)} hotspots...")
        
        # Build features
        features_list = []
        for h in hotspots:
            # Get the nearest facility type
            industrial_type = "unknown"
            if h.nearest_facility_id:
                fac = db.query(Facility).filter(Facility.id == h.nearest_facility_id).first()
                if fac:
                    industrial_type = fac.facility_type or "unknown"
            
            feat = {
                "brightness": h.brightness or 300.0,
                "frp": h.frp or 1.0,
                "confidence": h.confidence or 50.0,
                "pixel_area": h.pixel_area or 1.0,
                "dist_to_industry_m": h.dist_to_industry_m or 99999.0,
                "persistence_hours": h.persistence_hours or 0.0,
                "recurrence_count": h.recurrence_count or 1,
                "spatial_cluster_size": h.spatial_cluster_size or 1,
                "spread_rate": h.spread_rate or 0.0,
                "month": h.acq_date.month if h.acq_date else 1,
                "hour": h.acq_date.hour if h.acq_date else 12,
                "bright_t31": h.bright_t31 or 290.0,
                "brightness_ratio": (h.brightness / h.bright_t31) if (h.bright_t31 and h.bright_t31 > 0) else 1.0,
                "daynight": h.daynight or "D",
                "industrial_type": industrial_type,
                "land_cover_class": h.land_cover_class or "Unknown"
            }
            features_list.append(feat)
        
        df = pd.DataFrame(features_list)
        
        # Encode categoricals
        for col, le in label_encoders.items():
            if col in df.columns:
                df[col] = df[col].astype(str).fillna("unknown")
                known_classes = set(le.classes_)
                df[col] = df[col].apply(lambda x: x if x in known_classes else "unknown")
                if "unknown" not in le.classes_:
                    le.classes_ = np.append(le.classes_, "unknown")
                df[col + "_encoded"] = le.transform(df[col])
        
        # Build feature matrix
        X = df[feature_names].values.astype(np.float32)
        
        # Predict
        probs = np.zeros((len(X), len(target_encoder.classes_)))
        for est in ensemble.estimators_:
            probs += est.predict_proba(X)
        probs /= len(ensemble.estimators_)
        
        y_pred_enc = np.argmax(probs, axis=1)
        max_probs = np.max(probs, axis=1)
        y_pred = target_encoder.inverse_transform(y_pred_enc)
        
        # Update hotspots
        alert_count = 0
        for i, h in enumerate(hotspots):
            label_id = int(y_pred[i])
            ml_enum_val = enum_map.get(label_id, MLClassificationEnum.UNCLASSIFIED)
            h.ml_label = ml_enum_val
            h.classification_confidence = float(max_probs[i]) * 100.0
            
            # Create alerts for Industrial Fires with high FRP
            if ml_enum_val == MLClassificationEnum.INDUSTRIAL_FIRE and (h.frp or 0) > 50.0:
                # Check if alert already exists
                existing_alert = db.query(Alert).filter(Alert.hotspot_id == h.id).first()
                if not existing_alert:
                    severity = "CRITICAL" if h.frp > 200 else "HIGH" if h.frp > 100 else "MEDIUM"
                    alert = Alert(
                        hotspot_id=h.id,
                        alert_type="HIGH_FRP_INDUSTRIAL_FIRE",
                        severity=severity,
                        status="NEW"
                    )
                    db.add(alert)
                    alert_count += 1
        
        db.commit()
        
        # Print distribution
        logger.info("\n" + "=" * 50)
        logger.info("CLASSIFICATION RESULTS:")
        logger.info("=" * 50)
        
        from collections import Counter
        label_counts = Counter(enum_map.get(int(y_pred[i]), MLClassificationEnum.UNCLASSIFIED).value for i in range(len(y_pred)))
        for label, count in label_counts.most_common():
            logger.info(f"  {label:25s}: {count:5d}")
        
        logger.info(f"\n  Alerts generated: {alert_count}")
        logger.info("=" * 50)


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("IGNIS — Hotspot Reclassification Pipeline")
    logger.info("=" * 60)
    
    enrich_hotspots()
    reclassify()
    
    logger.info("\nAll done! Hotspots are now enriched and reclassified with real data.")
