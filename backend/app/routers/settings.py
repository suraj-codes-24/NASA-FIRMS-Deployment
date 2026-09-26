from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any

from app.database import get_db
from app.models.spatial import SystemSetting
from pydantic import BaseModel

router = APIRouter()

class SettingsUpdate(BaseModel):
    settings: Dict[str, str]

@router.get("/", response_model=Dict[str, str])
async def get_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SystemSetting))
    settings = result.scalars().all()
    return {setting.key: setting.value for setting in settings}

@router.post("/", response_model=Dict[str, str])
async def update_settings(update: SettingsUpdate, db: AsyncSession = Depends(get_db)):
    # Upsert logic
    for key, value in update.settings.items():
        result = await db.execute(select(SystemSetting).where(SystemSetting.key == key))
        setting = result.scalars().first()
        if setting:
            setting.value = str(value)
        else:
            db.add(SystemSetting(key=key, value=str(value)))
    
    await db.commit()
    return update.settings
