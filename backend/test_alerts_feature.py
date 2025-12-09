import json
import pytest
from app import app, alerts_db

# Reset DB for testing
def setup_module(module):
    print("Setting up test DB...")
    alerts_db.init_db()

def test_market_status():
    client = app.test_client()
    response = client.get('/market-status')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert 'trend' in data[0]

def test_create_alert():
    client = app.test_client()
    payload = {
        'crop': 'Wheat',
        'target_price': 1500,
        'condition': 'Above',
        'contact': 'test@example.com'
    }
    response = client.post('/alerts', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'id' in data

def test_get_alerts():
    client = app.test_client()
    response = client.get('/alerts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert data[0]['crop'] == 'Wheat'

def test_delete_alert():
    client = app.test_client()
    # First get ID
    response = client.get('/alerts')
    data = json.loads(response.data)
    alert_id = data[0]['id']
    
    # Delete
    del_response = client.delete(f'/alerts/{alert_id}')
    assert del_response.status_code == 200
    
    # Verify gone
    response = client.get('/alerts')
    data = json.loads(response.data)
    assert len(data) == 0

if __name__ == "__main__":
    # Manual run if pytest not present
    setup_module(None)
    try:
        test_market_status()
        print("test_market_status PASSED")
        test_create_alert()
        print("test_create_alert PASSED")
        test_get_alerts()
        print("test_get_alerts PASSED")
        test_delete_alert()
        print("test_delete_alert PASSED")
        print("ALL TESTS PASSED")
    except Exception as e:
        print(f"TEST FAILED: {e}")
