import asyncio
import os
from app.core.database import engine
from app.models.models import Base
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import User
from app.core.database import AsyncSessionLocal

async def init_db():
    print("Creating tables...")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Tables created")
    
    # Create demo user if it doesn't exist
    async with AsyncSessionLocal() as session:
        # Check if demo user exists
        result = await session.execute(select(User).where(User.email == "demo@rewear.com"))
        user = result.scalar_one_or_none()
        
        if not user:
            print("Creating demo user...")
            demo_user = User(
                email="demo@rewear.com",
                username="demouser",
                password=get_password_hash("demopassword"),
                role="user",
                points_balance=500
            )
            session.add(demo_user)
            await session.commit()
            print("Demo user created")
        else:
            print("Demo user already exists")

if __name__ == "__main__":
    asyncio.run(init_db())
