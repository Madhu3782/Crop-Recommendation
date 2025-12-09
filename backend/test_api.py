import requests
import json

url = 'http://localhost:5000/recommend'

def test_soil(soil_type):
    payload = {
        'region': 'Punjab',
        'season': 'Rabi',
        'soil_type': soil_type,
        'temperature': 25,
        'rainfall': 150,
        'humidity': 60
    }
    print(f"Testing Soil Type: {soil_type}")
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            crops = [item['crop'] for item in data['recommendations']]
            print(f"Recommended Crops: {crops}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 30)

if __name__ == "__main__":
    test_soil('Clayey')
    test_soil('Sandy')
    test_soil('Black')
