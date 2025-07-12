from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the DATABASE_URL, default to SQLite if not set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./rewear.db")

# Set connect_args for SQLite to handle concurrency
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    future=True,
    connect_args=connect_args
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False
)

# Base class for all models
Base = declarative_base()

# Dependency to get DB session
async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()
