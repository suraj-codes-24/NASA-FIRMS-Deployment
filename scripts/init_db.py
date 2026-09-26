"""
IGNIS — Database Initialization Script

Creates all tables defined in the ORM models if they don't exist.
Run this once before first use:
    python scripts/init_db.py
"""

import asyncio
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import engine, Base
from app.models.spatial import Hotspot, Facility, Alert, ClassificationLog, VerificationLog


async def main():
    print("🔥 IGNIS — Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ All tables created successfully.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
