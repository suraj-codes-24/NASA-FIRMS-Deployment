import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.users import User
from app.database import Base, async_engine, AsyncSessionLocal
from app.utils.security import get_password_hash

async def seed_admin():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # Check if admin exists
        from sqlalchemy import select
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
            await session.commit()
            print("Admin user seeded successfully!")
        else:
            print("Admin user already exists.")

if __name__ == "__main__":
    asyncio.run(seed_admin())
