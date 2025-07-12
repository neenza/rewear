import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
import asyncio
from typing import Any, Generator
from dotenv import load_dotenv

from app.main import app
from app.core.database import get_db, Base
from app.models.models import User, Item, Tag, Image, Swap
from app.core.security import get_password_hash

# Load test environment variables
load_dotenv(".env.test", override=True)

# Configure test database
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/rewear_test")

# Create test engine and session
test_engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session() -> AsyncSession:
    """Create a clean database for each test."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with TestingSessionLocal() as session:
        yield session
        # Clean up
        await session.rollback()
        await session.close()

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> Generator[TestClient, Any, None]:
    """Create a FastAPI test client."""
    # Override get_db dependency
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        password=get_password_hash("password123"),
        role="user"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
async def test_admin(db_session: AsyncSession) -> User:
    """Create a test admin user."""
    admin = User(
        email="admin@example.com",
        username="adminuser",
        password=get_password_hash("admin123"),
        role="admin"
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin

@pytest.fixture(scope="function")
async def test_item(db_session: AsyncSession, test_user: User) -> Item:
    """Create a test item."""
    item = Item(
        title="Test Item",
        description="This is a test item",
        category="Clothing",
        type="Shirt",
        size="M",
        condition="good",
        point_value=100,
        user_id=test_user.id,
        status="available",
        is_approved=True
    )
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)
    return item
