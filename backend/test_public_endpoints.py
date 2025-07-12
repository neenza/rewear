import requests

def test_items_endpoint():
    """Test that the items endpoint works without authentication"""
    try:
        # Test get all items (no auth)
        response = requests.get("http://localhost:8000/api/items?limit=10")
        if response.status_code == 200:
            items_data = response.json()
            items = items_data.get("items", [])
            total = items_data.get("total", 0)
            print(f"✅ GET /api/items successful! Retrieved {len(items)} items out of {total} total")
            
            if len(items) > 0:
                item_id = items[0]["id"]
                # Test get single item (no auth)
                response = requests.get(f"http://localhost:8000/api/items/{item_id}")
                if response.status_code == 200:
                    item = response.json()
                    print(f"✅ GET /api/items/{item_id} successful! Retrieved item: {item['title']}")
                else:
                    print(f"❌ GET /api/items/{item_id} failed with status code {response.status_code}")
                    print(f"Error: {response.text}")
            else:
                print("ℹ️ No items found to test individual item endpoint")
        else:
            print(f"❌ GET /api/items failed with status code {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")

if __name__ == "__main__":
    test_items_endpoint()
