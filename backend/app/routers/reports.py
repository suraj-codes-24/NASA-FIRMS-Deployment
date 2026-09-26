from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Optional
from datetime import date, datetime
import io
import csv

from app.database import get_db
from app.models.spatial import Hotspot, Alert, MLClassificationEnum

router = APIRouter()

@router.post("/generate")
async def generate_report(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    ml_label: Optional[MLClassificationEnum] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a CSV report from real hotspot and alert data.
    Supports filtering by date range and classification type.
    """
    query = select(Hotspot).order_by(Hotspot.acq_date.desc())
    
    if date_from:
        query = query.filter(Hotspot.acq_date >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.filter(Hotspot.acq_date <= datetime.combine(date_to, datetime.max.time()))
    if ml_label:
        query = query.filter(Hotspot.ml_label == ml_label)
    
    query = query.limit(5000)  # Safety cap
    result = await db.execute(query)
    hotspots = result.scalars().all()
    
    # Build CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "id", "latitude", "longitude", "classification", "confidence",
        "frp_mw", "brightness", "satellite", "daynight",
        "dist_to_industry_m", "persistence_hours", "acq_date",
        "is_verified"
    ])
    
    # Data rows
    for h in hotspots:
        writer.writerow([
            h.id,
            round(h.latitude, 6),
            round(h.longitude, 6),
            h.ml_label.value if h.ml_label else "Unclassified",
            round(h.classification_confidence or 0, 2),
            round(h.frp or 0, 2),
            round(h.brightness or 0, 2),
            h.satellite or "Unknown",
            h.daynight or "D",
            round(h.dist_to_industry_m or 0, 1),
            round(h.persistence_hours or 0, 1),
            h.acq_date.isoformat() if h.acq_date else "",
            h.is_user_verified
        ])
    
    output.seek(0)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"ignis_report_{timestamp}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/summary")
async def report_summary(db: AsyncSession = Depends(get_db)):
    """
    Quick summary stats for report generation UI.
    """
    total_q = await db.execute(select(func.count(Hotspot.id)))
    total = total_q.scalar() or 0
    
    industrial_q = await db.execute(
        select(func.count(Hotspot.id))
        .where(Hotspot.ml_label == MLClassificationEnum.INDUSTRIAL_FIRE)
    )
    industrial = industrial_q.scalar() or 0
    
    alerts_q = await db.execute(
        select(func.count(Alert.id)).where(Alert.status == "NEW")
    )
    open_alerts = alerts_q.scalar() or 0
    
    return {
        "total_hotspots": total,
        "industrial_fires": industrial,
        "open_alerts": open_alerts,
        "report_available": total > 0
    }
