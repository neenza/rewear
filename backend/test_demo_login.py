import requests
import json

def test_demo_login():
    """Test the demo login endpoint and token handling"""
    try:
        # Call demo login endpoint
        login_response = requests.post("http://localhost:8000/api/auth/demo-login")
        
        print(f"Demo Login Status Code: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            token = login_data.get("access_token")
            
            print(f"Got token: {token[:10]}...")
            
            # Test /me endpoint with token
            headers = {"Authorization": f"Bearer {token}"}
            me_response = requests.get("http://localhost:8000/api/auth/me", headers=headers)
            
            print(f"Me Endpoint Status Code: {me_response.status_code}")
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print(f"User data: {json.dumps(user_data, indent=2)}")
            else:
                print(f"Failed to get user data: {me_response.text}")
        else:
            print(f"Demo login failed: {login_response.text}")
    
    except Exception as e:
        print(f"Error during test: {str(e)}")

if __name__ == "__main__":
    test_demo_login()
