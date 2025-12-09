import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_backend():
    print("--- Testing Backend Endpoints ---")
    
    # Wait for server to be potentially ready if just started, but it should be running.
    
    # 1. Test Fetch Weather
    print("\n[1] Testing /fetch_weather...")
    try:
        response = requests.get(f"{BASE_URL}/fetch_weather", params={"state": "Karnataka", "district": "Davanagere"})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Response:", response.json())
        else:
            print("Error Response:", response.text)
    except Exception as e:
        print(f"Exception contacting {BASE_URL}/fetch_weather: {e}")

    # 2. Test Predict (Crop Recommendation)
    print("\n[2] Testing /predict (Crop Recommendation)...")
    payload = {
        "region": "Davanagere", # Used for suitability message
        "N": 90, "P": 40, "K": 55, "pH": 6.5,
        "temperature": 27, "humidity": 65, "rainfall": 500
    }
    try:
        response = requests.post(f"{BASE_URL}/predict", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Response:", json.dumps(response.json(), indent=2))
        else:
            print("Error Response:", response.text)
    except Exception as e:
         print(f"Exception contacting {BASE_URL}/predict: {e}")

if __name__ == "__main__":
    test_backend()
