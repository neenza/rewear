"""
Test script to verify the functionality of the items API endpoint.
"""
import asyncio
import aiohttp
import sys
import json
from pathlib import Path

# Add the backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def test_get_items():
    """Test the GET /api/items endpoint"""
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/api/items") as response:
            print(f"GET /api/items status: {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"Total items: {data.get('total', 'N/A')}")
                print(f"Items returned: {len(data.get('items', []))}")
                for item in data.get('items', [])[:3]:  # Show first 3 items only
                    print(f"Item: {item['title']}, ID: {item['id']}")
                    if item.get('images'):
                        print(f"  Image URL: {item['images'][0]['image_url']}")
            else:
                print(f"Error: {await response.text()}")

async def test_create_item():
    """Test the POST /api/items endpoint with authentication"""
    # First, login to get a token
    login_data = {
        "username": "demo@example.com",
        "password": "demo1234"
    }
    
    async with aiohttp.ClientSession() as session:
        # Login
        async with session.post("http://localhost:8000/api/auth/login", json=login_data) as response:
            if response.status == 200:
                token_data = await response.json()
                token = token_data.get("access_token")
                print(f"Login successful, got token")
                
                # Now create an item with the token
                # Prepare item data
                item_data = {
                    "title": "Test Item",
                    "description": "This is a test item created by the test script",
                    "category": "tops",
                    "type": "t-shirt",
                    "size": "m",
                    "condition": "like_new",
                    "point_value": 50,
                    "tags": ["test", "script"]
                }
                
                # Create a test image file
                with open("test_image.jpg", "wb") as f:
                    f.write(b"dummy image content")
                
                # Create form data
                data = aiohttp.FormData()
                data.add_field('item_in', json.dumps(item_data))
                data.add_field('images', 
                              open('test_image.jpg', 'rb'),
                              filename='test_image.jpg',
                              content_type='image/jpeg')
                
                # Make request
                headers = {"Authorization": f"Bearer {token}"}
                async with session.post("http://localhost:8000/api/items", 
                                      data=data, 
                                      headers=headers) as item_response:
                    print(f"POST /api/items status: {item_response.status}")
                    if item_response.status == 200:
                        item_result = await item_response.json()
                        print(f"Created item: {item_result['title']}, ID: {item_result['id']}")
                    else:
                        print(f"Error: {await item_response.text()}")
                        
                # Clean up
                import os
                if os.path.exists("test_image.jpg"):
                    os.remove("test_image.jpg")
            else:
                print(f"Login failed: {await response.text()}")

async def main():
    """Run tests"""
    print("Testing GET /api/items endpoint...")
    await test_get_items()
    
    # Uncomment to test item creation
    # print("\nTesting POST /api/items endpoint...")
    # await test_create_item()

if __name__ == "__main__":
    asyncio.run(main())
