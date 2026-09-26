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

