"""
IGNIS — Classification Service

Thin wrapper around the ML model module that provides a clean
interface for classifying a batch of Hotspot ORM objects.
"""

import logging
import pandas as pd

from app.ml.model import load_model, predict, LABEL_TO_ENUM
from app.ml.features import build_feature_matrix
from app.models.spatial import MLClassificationEnum

logger = logging.getLogger("ignis.services.classification")


def classify_hotspots(hotspots, db_session=None):
    """
    Classify a list of Hotspot ORM objects in-place.
    Sets ml_label and classification_confidence on each hotspot.

    Returns list of (hotspot, label, confidence) tuples.
    """
    if not hotspots:
        return []

    records = []
    for h in hotspots:
        records.append({
            "brightness": h.brightness or 0.0,
            "frp": h.frp or 0.0,
            "confidence": h.confidence or 50.0,
            "pixel_area": h.pixel_area or 1.0,
            "dist_to_industry_m": h.dist_to_industry_m or 99999.0,
            "persistence_hours": h.persistence_hours or 0.0,
            "recurrence_count": 1,
            "spatial_cluster_size": h.spatial_cluster_size or 1,
            "spread_rate": 0.0,
            "month": h.acq_date.month if h.acq_date else 1,
            "hour": h.acq_date.hour if h.acq_date else 12,
            "bright_t31": h.bright_t31 or 0.0,
            "brightness_ratio": (
                (h.brightness / h.bright_t31) if h.bright_t31 else 1.0
            ),
            "daynight": h.daynight or "D",
            "industrial_type": "unknown",
            "land_cover_class": h.land_cover_class or "Unknown",
        })

    df = pd.DataFrame(records)
    labels, confidences, _ = predict(df)

    results = []
    for h, label, conf in zip(hotspots, labels, confidences):
        h.ml_label = label
        h.classification_confidence = conf
        results.append((h, label, conf))

    return results
