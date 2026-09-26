from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from typing import List

from app.database import get_db
from app.models.spatial import Alert, Hotspot
from app.schemas.spatial import AlertResponse, AlertUpdate

router = APIRouter()

@router.get("", response_model=List[AlertResponse])
async def list_alerts(db: AsyncSession = Depends(get_db)):
    query = await db.execute(
        select(Alert)
        .options(joinedload(Alert.hotspot).joinedload(Hotspot.nearest_facility))
        .order_by(Alert.created_at.desc())
    )
    return query.scalars().all()

@router.put("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    alert = await db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.status = "ACKNOWLEDGED"
    alert.is_read = True
    await db.commit()
    await db.refresh(alert)
    return alert

@router.put("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: int,
    request: AlertUpdate,
    db: AsyncSession = Depends(get_db)
):
    alert = await db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.status = "RESOLVED"
    alert.is_read = True
    alert.resolution_note = request.resolution_note
    await db.commit()
    await db.refresh(alert)
    return alert

@router.put("/{alert_id}/notes", response_model=AlertResponse)
async def update_alert_notes(
    alert_id: int,
    request: AlertUpdate,
    db: AsyncSession = Depends(get_db)
):
    alert = await db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.resolution_note = request.resolution_note
    await db.commit()
    await db.refresh(alert)
    return alert
@router.post("/seed-demo")
async def seed_demo_data(db: AsyncSession = Depends(get_db)):
    """Seed demo data for the hackathon presentation."""
    from app.models.spatial import Facility, Hotspot, MLClassificationEnum
    from geoalchemy2.elements import WKTElement
    import datetime
    
    # Check if demo data already exists
    query = await db.execute(select(Facility).where(Facility.name == "Demo Steel Plant"))
    if query.scalars().first():
        return {"message": "Demo data already seeded"}
        
    facility = Facility(
        name="Demo Steel Plant",
        facility_type="metal_smelting",
        geom=WKTElement("POINT(86.2 22.8)", srid=4326),
        state="Jharkhand",
        district="Singhbhum"
    )
    db.add(facility)
    await db.flush()

    hotspot = Hotspot(
        latitude=22.805,
        longitude=86.205,
        geom=WKTElement("POINT(86.205 22.805)", srid=4326),
        brightness=350.5,
        bright_t31=310.0,
        frp=250.0,
        confidence=100.0,
        satellite="Terra",
        instrument="MODIS",
        daynight="D",
        acq_date=datetime.datetime.utcnow(),
        ml_label=MLClassificationEnum.INDUSTRIAL_FIRE,
        classification_confidence=98.5,
        nearest_facility_id=facility.id,
        dist_to_industry_m=500.0
    )
    db.add(hotspot)
    await db.flush()

    alert = Alert(
        hotspot_id=hotspot.id,
        severity="CRITICAL",
        status="NEW",
        description="High-intensity thermal anomaly detected near Demo Steel Plant. Probable unrecorded flare or accident.",
        created_at=datetime.datetime.utcnow()
    )
    db.add(alert)
    
    hotspot2 = Hotspot(
        latitude=23.7,
        longitude=86.4,
        geom=WKTElement("POINT(86.4 23.7)", srid=4326),
        brightness=340.0,
        bright_t31=300.0,
        frp=150.0,
        confidence=90.0,
        satellite="N",
        instrument="VIIRS",
        daynight="N",
        acq_date=datetime.datetime.utcnow(),
        ml_label=MLClassificationEnum.GAS_FLARE,
        classification_confidence=92.0,
        nearest_facility_id=facility.id,
        dist_to_industry_m=2000.0
    )
    db.add(hotspot2)
    await db.flush()

    alert2 = Alert(
        hotspot_id=hotspot2.id,
        severity="HIGH",
        status="INVESTIGATING",
        description="Anomalous night-time thermal signature near industrial zone.",
        created_at=datetime.datetime.utcnow()
    )
    db.add(alert2)

    await db.commit()
    return {"message": "Demo data seeded successfully!"}
