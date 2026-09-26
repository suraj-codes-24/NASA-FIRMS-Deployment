from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Optional
from datetime import date, datetime

from app.database import get_db
from app.models.spatial import Hotspot, Alert, MLClassificationEnum
from app.schemas.spatial import AnalyticsSummaryResponse, ClassificationCount, TimelineDataPoint

router = APIRouter()

@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    ml_label: Optional[MLClassificationEnum] = Query(None),
    min_confidence: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    base_query = select(func.count(Hotspot.id))
    
    if date_from:
        base_query = base_query.where(Hotspot.acq_date >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        base_query = base_query.where(Hotspot.acq_date <= datetime.combine(date_to, datetime.max.time()))
    if ml_label:
        base_query = base_query.where(Hotspot.ml_label == ml_label)
    if min_confidence is not None:
        base_query = base_query.where(Hotspot.confidence >= min_confidence)

    # Total hotspots
    total_query = await db.execute(base_query)
    total_hotspots = total_query.scalar() or 0
    
    # Active industrial fires
    industrial_query = await db.execute(
        base_query.where(Hotspot.ml_label == MLClassificationEnum.INDUSTRIAL_FIRE)
    )
    active_industrial_fires = industrial_query.scalar() or 0
    
    # High severity alerts
    alerts_query = select(func.count(Alert.id)).where(Alert.severity.in_(["HIGH", "CRITICAL"])).where(Alert.status != "RESOLVED")
    if date_from or date_to or ml_label or min_confidence is not None:
        alerts_query = alerts_query.join(Hotspot, Alert.hotspot_id == Hotspot.id)
        if date_from:
            alerts_query = alerts_query.where(Hotspot.acq_date >= datetime.combine(date_from, datetime.min.time()))
        if date_to:
            alerts_query = alerts_query.where(Hotspot.acq_date <= datetime.combine(date_to, datetime.max.time()))
        if ml_label:
            alerts_query = alerts_query.where(Hotspot.ml_label == ml_label)
        if min_confidence is not None:
            alerts_query = alerts_query.where(Hotspot.confidence >= min_confidence)
            
    high_alerts_result = await db.execute(alerts_query)
    high_severity_alerts = high_alerts_result.scalar() or 0
    
    # Unverified classifications
    unverified_query = await db.execute(
        base_query.where(Hotspot.is_user_verified == False).where(Hotspot.ml_label != MLClassificationEnum.UNCLASSIFIED)
    )
    unverified_classifications = unverified_query.scalar() or 0

    return AnalyticsSummaryResponse(
        total_hotspots=total_hotspots,
        active_industrial_fires=active_industrial_fires,
        high_severity_alerts=high_severity_alerts,
        unverified_classifications=unverified_classifications
    )

@router.get("/classification", response_model=List[ClassificationCount])
async def get_classification_breakdown(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    ml_label: Optional[MLClassificationEnum] = Query(None),
    min_confidence: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(Hotspot.ml_label, func.count(Hotspot.id))
    
    if date_from:
        query = query.where(Hotspot.acq_date >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.where(Hotspot.acq_date <= datetime.combine(date_to, datetime.max.time()))
    if ml_label:
        query = query.where(Hotspot.ml_label == ml_label)
    if min_confidence is not None:
        query = query.where(Hotspot.confidence >= min_confidence)
        
    query = query.group_by(Hotspot.ml_label)
    
    result = await db.execute(query)
    rows = result.all()
    return [ClassificationCount(label=r[0], count=r[1]) for r in rows]

@router.get("/timeline", response_model=list)
async def get_timeline(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    ml_label: Optional[MLClassificationEnum] = Query(None),
    min_confidence: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    # Group by date and ml_label to allow multi-line charts on the frontend
    query = select(func.date(Hotspot.acq_date).label('date'), Hotspot.ml_label, func.count(Hotspot.id))
    
    if date_from:
        query = query.where(Hotspot.acq_date >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.where(Hotspot.acq_date <= datetime.combine(date_to, datetime.max.time()))
    if ml_label:
        query = query.where(Hotspot.ml_label == ml_label)
    if min_confidence is not None:
        query = query.where(Hotspot.confidence >= min_confidence)
        
    query = query.group_by('date', Hotspot.ml_label).order_by('date')
    
    result = await db.execute(query)
    rows = result.all()
    return [{"date": str(r[0]), "ml_label": r[1], "count": r[2]} for r in rows]

@router.get("/top-states", response_model=list)
async def get_top_states(
    ml_label: MLClassificationEnum = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get states ranked by hotspot count. Requires facility join for state info.
    """
    from app.models.spatial import Facility
    query = (
        select(Facility.state, func.count(Hotspot.id).label("count"))
        .join(Facility, Hotspot.nearest_facility_id == Facility.id)
        .where(Facility.state.isnot(None))
        .group_by(Facility.state)
        .order_by(func.count(Hotspot.id).desc())
        .limit(limit)
    )
    if ml_label:
        query = query.where(Hotspot.ml_label == ml_label)
    
    result = await db.execute(query)
    return [{"state": r[0], "count": r[1]} for r in result.all()]

@router.get("/persistence", response_model=list)
async def get_persistent_sources(
    min_hours: float = 48.0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    Get persistent thermal sources that have been active longer than min_hours.
    """
    query = (
        select(Hotspot)
        .where(Hotspot.persistence_hours >= min_hours)
        .order_by(Hotspot.persistence_hours.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()
