import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_create_item(client, test_user):
    """Test item creation."""
    # Create token for authentication
    from app.core.security import create_user_token
    token = create_user_token(user_id=test_user.id, username=test_user.username, role=test_user.role)
    
    # Mock file upload
    import io
    from fastapi import UploadFile
    test_file = io.BytesIO(b"file content")
    
    # Create item data
    item_data = {
        "title": "New Item",
        "description": "A brand new item",
        "category": "Clothing",
        "type": "Pants",
        "size": "L",
        "condition": "like_new",
        "point_value": 150,
        "tags": ["jeans", "denim"]
    }
    
    # This test would normally involve file uploads, but for simplicity in testing,
    # we're going to mock it by patching the s3_service.upload_file method
    import unittest.mock
    from app.services.s3 import s3_service
    
    with unittest.mock.patch.object(s3_service, "upload_file", return_value="https://example.com/test-image.jpg"):
        files = {
            "images": ("test.jpg", test_file, "image/jpeg")
        }
        response = await client.post(
            "/api/items",
            files=files,
            data={"item_in": str(item_data)},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Item"
    assert data["description"] == "A brand new item"
    assert data["user_id"] == test_user.id
    assert data["status"] == "pending"
    assert not data["is_approved"]

@pytest.mark.asyncio
async def test_get_items(client, test_item):
    """Test getting item list."""
    response = await client.get("/api/items")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["id"] == test_item.id
    assert data[0]["title"] == test_item.title

@pytest.mark.asyncio
async def test_get_item_detail(client, test_item):
    """Test getting item detail."""
    response = await client.get(f"/api/items/{test_item.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_item.id
    assert data["title"] == test_item.title
    assert data["description"] == test_item.description

@pytest.mark.asyncio
async def test_update_item(client, test_user, test_item):
    """Test updating an item."""
    # Create token for authentication
    from app.core.security import create_user_token
    token = create_user_token(user_id=test_user.id, username=test_user.username, role=test_user.role)
    
    update_data = {
        "title": "Updated Item",
        "description": "This item has been updated"
    }
    
    response = await client.put(
        f"/api/items/{test_item.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Item"
    assert data["description"] == "This item has been updated"

@pytest.mark.asyncio
async def test_delete_item(client, test_user, test_item):
    """Test deleting an item."""
    # Create token for authentication
    from app.core.security import create_user_token
    token = create_user_token(user_id=test_user.id, username=test_user.username, role=test_user.role)
    
    response = await client.delete(
        f"/api/items/{test_item.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    
    # Verify item is deleted
    response = await client.get(f"/api/items/{test_item.id}")
    assert response.status_code == 404
