# Integration test for login API endpoint
import requests
import json

def test_login_endpoint():
    url = "http://localhost:5000/login"
    data = {"email": "test@gmail.com", "password": "password123"}
    
    response = requests.post(url, json=data)
    result = response.json()
    
    assert response.status_code == 200
    assert result["success"] == True
    assert result["user"] == "test@gmail.com"

if __name__ == "__main__":
    test_login_endpoint()
    print("Integration test passed")
