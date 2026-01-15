import requests
import json

api_key = "35f75e25-055" # Example key, I should get the real one from DB

def test_auth(key):
    url = "https://api-ru.iiko.services/api/1/access_token"
    resp = requests.post(url, json={"apiLogin": key})
    print(f"Auth status: {resp.status_code}")
    if resp.status_code == 200:
        token = resp.json().get("token")
        print(f"Token received")
        return token
    else:
        print(f"Auth failed: {resp.text}")
        return None

# I'll need to run this inside the container to get the API key OR just look it up if I can.
