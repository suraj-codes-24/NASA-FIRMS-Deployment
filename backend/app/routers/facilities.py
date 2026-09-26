from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.spatial import Facility
from app.schemas.spatial import FacilityResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/facilities", tags=["Facilities"])

@router.get("", response_model=List[FacilityResponse])
async def get_facilities(
    limit: int = Query(100, ge=1, le=1000),
    facility_type: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve industrial facilities.
    """
    query = select(Facility).limit(limit)
    if facility_type:
        query = query.filter(Facility.facility_type == facility_type)
        
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{facility_id}", response_model=FacilityResponse)
async def get_facility(
    facility_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific industrial facility by ID.
    """
    facility = await db.get(Facility, facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
        
    return facility

@router.get("/{facility_id}/hotspots")
async def get_facility_hotspots(
    facility_id: int,
    radius_km: float = Query(2.0, ge=0.1, le=50.0),
    days: int = Query(7, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all hotspots within radius_km of a given facility.
    """
    from app.models.spatial import Hotspot
    from app.schemas.spatial import HotspotResponse
    
    facility = await db.get(Facility, facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    # Use coordinate-based proximity filter (radius_km ~= degrees * 111)
    delta = radius_km / 111.0
    query = (
        select(Hotspot)
        .filter(
            Hotspot.latitude.between(facility.geom.ST_Y() - delta, facility.geom.ST_Y() + delta),
            Hotspot.longitude.between(facility.geom.ST_X() - delta, facility.geom.ST_X() + delta),
        )
        .order_by(Hotspot.acq_date.desc())
        .limit(200)
    )
    
    result = await db.execute(query)
    return result.scalars().all()
