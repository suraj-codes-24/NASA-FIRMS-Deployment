"""
IGNIS — Report Generation Service

Generates CSV and PDF reports of classified hotspot data
for download by dashboard users.
"""

import logging
import io
import csv
from datetime import datetime

from sqlalchemy.orm import Session
from app.models.spatial import Hotspot

logger = logging.getLogger("ignis.services.report")


def generate_csv_report(db: Session, days: int = 7) -> str:
    """
    Generate a CSV string containing classified hotspot data
    from the last `days` days.
    """
    from datetime import timedelta

    cutoff = datetime.utcnow() - timedelta(days=days)
    hotspots = (
        db.query(Hotspot)
        .filter(Hotspot.acq_date >= cutoff)
        .order_by(Hotspot.acq_date.desc())
        .limit(5000)
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "latitude", "longitude", "brightness", "bright_t31",
        "frp", "confidence", "satellite", "instrument", "daynight",
        "acq_date", "ml_label", "classification_confidence",
        "dist_to_industry_m", "is_user_verified",
    ])
    for h in hotspots:
        writer.writerow([
            h.id, h.latitude, h.longitude, h.brightness, h.bright_t31,
            h.frp, h.confidence, h.satellite, h.instrument, h.daynight,
            h.acq_date.isoformat() if h.acq_date else "",
            h.ml_label.value if h.ml_label else "Unclassified",
            h.classification_confidence,
            h.dist_to_industry_m, h.is_user_verified,
        ])

    return output.getvalue()


def generate_summary_stats(db: Session) -> dict:
    """Return summary statistics for the report header."""
    from sqlalchemy import func
    from app.models.spatial import MLClassificationEnum

    total = db.query(func.count(Hotspot.id)).scalar() or 0
    industrial = (
        db.query(func.count(Hotspot.id))
        .filter(Hotspot.ml_label == MLClassificationEnum.INDUSTRIAL_FIRE)
        .scalar() or 0
    )
    verified = (
        db.query(func.count(Hotspot.id))
        .filter(Hotspot.is_user_verified == True)
        .scalar() or 0
    )

    return {
        "total_hotspots": total,
        "industrial_fires": industrial,
        "verified_count": verified,
        "generated_at": datetime.utcnow().isoformat(),
    }
