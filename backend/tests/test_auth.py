import pytest
from httpx import AsyncClient
from fastapi import status

from app.core.security import create_user_token

@pytest.mark.asyncio
async def test_register_user(client):
    """Test user registration."""
    # Create new user
    response = await client.post("/api/auth/register", json={
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "password" not in data
    assert data["role"] == "user"

@pytest.mark.asyncio
async def test_register_duplicate_email(client, test_user):
    """Test registration with duplicate email."""
    response = await client.post("/api/auth/register", json={
        "email": "test@example.com",  # Same as test_user
        "username": "uniqueusername",
        "password": "password123"
    })
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login(client, test_user):
    """Test user login."""
    response = await client.post("/api/auth/login", data={
        "username": "test@example.com",  # OAuth2 uses username field for email
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = await client.post("/api/auth/login", data={
        "username": "wrong@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user(client, test_user):
    """Test getting current user info."""
    token = create_user_token(user_id=test_user.id, username=test_user.username, role=test_user.role)
    
    response = await client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["username"] == test_user.username
