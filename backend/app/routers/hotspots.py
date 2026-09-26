from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload
from typing import List, Optional
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_DWithin, ST_X, ST_Y
from datetime import datetime, date

from app.database import get_db
from app.models.spatial import Hotspot, Facility, MLClassificationEnum, VerificationLog
from app.schemas.spatial import HotspotIngest, HotspotResponse, FacilityResponse, HotspotVerifyRequest, VerificationLogResponse, HeatmapPoint
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/hotspots", tags=["Hotspots"])

@router.post("/ingest", status_code=202)
async def ingest_hotspots(
    hotspots: List[HotspotIngest],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest a batch of hotspots. Enqueues them for background ML processing via Celery.
    """
    db_hotspots = []
    for h in hotspots:
        point = f"POINT({h.longitude} {h.latitude})"
        hotspot = Hotspot(
            latitude=h.latitude,
            longitude=h.longitude,
            geom=WKTElement(point, srid=4326),
            brightness=h.brightness,
            bright_t31=h.bright_t31,
            frp=h.frp,
            confidence=h.confidence,
            satellite=h.satellite,
            instrument=h.instrument,
            daynight=h.daynight,
            scan=h.scan,
            track=h.track,
            pixel_area=h.pixel_area,
            acq_date=h.acq_date,
            ml_label=MLClassificationEnum.UNCLASSIFIED
        )
        db.add(hotspot)
        db_hotspots.append(hotspot)
    
    await db.commit()
    
    hotspot_ids = [h.id for h in db_hotspots]
    
    from app.tasks.ml_tasks import process_hotspots_batch
    process_hotspots_batch.delay(hotspot_ids)
    
    return {"message": f"Ingested {len(hotspot_ids)} hotspots for processing.", "ids": hotspot_ids}

@router.post("/trigger-ingestion", status_code=202)
async def trigger_nasa_firms_ingestion():
    """
    Manually trigger the NASA FIRMS data ingestion celery task.
    """
    from app.tasks.nasa_tasks import fetch_nasa_firms_data
    fetch_nasa_firms_data.delay()
    return {"message": "NASA FIRMS ingestion task triggered in background."}

@router.get("", response_model=List[HotspotResponse])
async def get_hotspots(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    ml_label: Optional[MLClassificationEnum] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    confidence_min: Optional[float] = Query(None, ge=0, le=100),
    state: Optional[str] = Query(None),
    bbox: Optional[str] = Query(None, description="min_lon,min_lat,max_lon,max_lat"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve hotspots with filtering. Supports date range, classification type,
    confidence threshold, bounding box, and pagination.
    """
    query = select(Hotspot).options(joinedload(Hotspot.nearest_facility)).order_by(Hotspot.acq_date.desc())
    
    if ml_label:
        query = query.filter(Hotspot.ml_label == ml_label)
    if date_from:
        query = query.filter(Hotspot.acq_date >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.filter(Hotspot.acq_date <= datetime.combine(date_to, datetime.max.time()))
    if confidence_min is not None:
        query = query.filter(Hotspot.confidence >= confidence_min)
    if bbox:
        try:
            parts = [float(x.strip()) for x in bbox.split(",")]
            min_lon, min_lat, max_lon, max_lat = parts
            query = query.filter(
                and_(
                    Hotspot.latitude >= min_lat,
                    Hotspot.latitude <= max_lat,
                    Hotspot.longitude >= min_lon,
                    Hotspot.longitude <= max_lon
                )
            )
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="Invalid bbox format. Use: min_lon,min_lat,max_lon,max_lat")
    
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/latest", response_model=List[HotspotResponse])
async def get_latest_hotspots(
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the most recently ingested hotspots.
    """
    query = select(Hotspot).options(joinedload(Hotspot.nearest_facility)).order_by(Hotspot.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/heatmap", response_model=List[HeatmapPoint])
async def get_heatmap_data(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    ml_label: Optional[MLClassificationEnum] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get heatmap data points (lat, lon, weight=FRP) for density visualization.
    """
    query = select(Hotspot.latitude, Hotspot.longitude, Hotspot.frp)
    
    if date_from:
        query = query.filter(Hotspot.acq_date >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.filter(Hotspot.acq_date <= datetime.combine(date_to, datetime.max.time()))
    if ml_label:
        query = query.filter(Hotspot.ml_label == ml_label)
    
    query = query.limit(5000)
    result = await db.execute(query)
    rows = result.all()
    return [HeatmapPoint(latitude=r[0], longitude=r[1], weight=r[2] or 1.0) for r in rows]

@router.get("/{hotspot_id}", response_model=HotspotResponse)
async def get_hotspot(
    hotspot_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get full details of a single hotspot by ID.
    """
    query = select(Hotspot).options(joinedload(Hotspot.nearest_facility)).filter(Hotspot.id == hotspot_id)
    result = await db.execute(query)
    hotspot = result.scalar_one_or_none()
    if not hotspot:
        raise HTTPException(status_code=404, detail="Hotspot not found")
    return hotspot

@router.get("/{hotspot_id}/history", response_model=List[HotspotResponse])
async def get_hotspot_history(
    hotspot_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical hotspots at approximately the same location (within ~1km grid).
    """
    hotspot = await db.get(Hotspot, hotspot_id)
    if not hotspot:
        raise HTTPException(status_code=404, detail="Hotspot not found")
    
    # Find nearby hotspots within ~0.01 degree (~1km) over the time window
    query = select(Hotspot).filter(
        and_(
            Hotspot.latitude.between(hotspot.latitude - 0.01, hotspot.latitude + 0.01),
            Hotspot.longitude.between(hotspot.longitude - 0.01, hotspot.longitude + 0.01),
            Hotspot.acq_date >= func.now() - func.cast(f'{days} days', type_=None.__class__)
        )
    ).order_by(Hotspot.acq_date.desc()).limit(200)
    
    # Simplified approach: just filter by coordinate proximity
    query = select(Hotspot).options(joinedload(Hotspot.nearest_facility)).filter(
        and_(
            Hotspot.latitude.between(hotspot.latitude - 0.01, hotspot.latitude + 0.01),
            Hotspot.longitude.between(hotspot.longitude - 0.01, hotspot.longitude + 0.01),
        )
    ).order_by(Hotspot.acq_date.desc()).limit(200)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{hotspot_id}/nearest-facilities", response_model=List[FacilityResponse])
async def get_nearest_facilities(
    hotspot_id: int,
    limit: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the nearest industrial facilities to a given hotspot.
    """
    hotspot = await db.get(Hotspot, hotspot_id)
    if not hotspot:
        raise HTTPException(status_code=404, detail="Hotspot not found")
        
    query = select(Facility).order_by(
        Facility.geom.distance_centroid(hotspot.geom)
    ).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/{hotspot_id}/verify", response_model=VerificationLogResponse)
async def verify_hotspot_classification(
    hotspot_id: int,
    request: HotspotVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Field agents or experts use this to verify or correct the ML classification.
    """
    hotspot = await db.get(Hotspot, hotspot_id)
    if not hotspot:
        raise HTTPException(status_code=404, detail="Hotspot not found")
        
    original_label = hotspot.ml_label
    
    log = VerificationLog(
        hotspot_id=hotspot_id,
        original_label=original_label,
        verified_label=request.verified_label,
        user_id=request.user_id,
        notes=request.notes
    )
    db.add(log)
    
    hotspot.ml_label = request.verified_label
    hotspot.is_user_verified = True
    
    await db.commit()
    await db.refresh(log)
    
    return log

