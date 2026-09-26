import asyncio
import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.database import Base, async_engine, AsyncSessionLocal
from app.models.users import User
from app.models.spatial import SystemSetting
from app.utils.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ignis.seeder")

async def seed_db():
    async with async_engine.begin() as conn:
        logger.info("Ensuring database tables exist...")
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # 1. Seed Admin User
        result = await session.execute(select(User).where(User.email == "admin@ignis.gov"))
        user = result.scalars().first()
        
        if not user:
            hashed_pw = get_password_hash("admin123")
            admin_user = User(
                email="admin@ignis.gov",
                hashed_password=hashed_pw,
                full_name="Admin Analyst",
                role="admin",
                is_active=True
            )
            session.add(admin_user)
            logger.info("Admin user (admin@ignis.gov) seeded successfully.")
        else:
            logger.info("Admin user already exists.")

        # 2. Seed Default Settings (NASA API Key, etc)
        default_settings = [
            ("firms_api_key", "3d9d0e3e3766c65c06e5609967f39b9a"), # Fallback key
            ("settings_ingestion", "3"),
            ("settings_theme_dark", "true"),
            ("settings_notif_ind", "true"),
            ("settings_notif_sound", "true")
        ]

        for key, val in default_settings:
            res = await session.execute(select(SystemSetting).where(SystemSetting.key == key))
            setting = res.scalars().first()
            if not setting:
                session.add(SystemSetting(key=key, value=val))
                logger.info(f"Seeded default setting: {key}={val}")

        await session.commit()
        logger.info("Database seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_db())
