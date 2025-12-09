from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import pandas as pd
import numpy as np
import atexit
# from apscheduler.schedulers.background import BackgroundScheduler # Removed
import alerts_db
import notification_service
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the model
try:
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    print("Model loaded successfully.")
except FileNotFoundError:
    print("Error: model.pkl not found. Make sure to run model_training.py first.")
    model = None

# Initialize Database
try:
    alerts_db.init_db()
    print("Alerts Database Initialized.")
except Exception as e:
    print(f"Error initializing DB: {e}")

# --- Helper to get Current Price (Simulated) ---
def get_current_price(crop, region="Uttar Pradesh"): # Default region for now
    # in a real app, fetch from live API. Here, use model or random fluctuation around model
    # Let's use the model with "current" weather (mocked)
    if not model:
        return 0
    
    # Mock current conditions
    input_data = pd.DataFrame([{
        'Crop': crop,
        'Region': region,
        'Season': 'Rabi', # Mock
        'Temperature': 25.0,
        'Rainfall': 100.0,
        'Humidity': 50.0
    }])
    try:
        price = model.predict(input_data)[0]
        # Add some random fluctuation to make it interesting
        import random
        fluctuation = random.uniform(-50, 50)
        return round(price + fluctuation, 2)
    except:
        return 0

import threading
import time

# --- Background Job: Check Alerts ---
def check_price_alerts():
    # Run forever in a separate thread
    while True:
        print("Running Background Alert Check...", flush=True)
        try:
             # Re-connect to DB in thread if needed, but get_alerts handles it
            alerts = alerts_db.get_alerts()
            for alert in alerts:
                current_price = get_current_price(alert['crop'])
                triggered = False
                if alert['condition'] == 'Above' and current_price > alert['target_price']:
                    triggered = True
                elif alert['condition'] == 'Below' and current_price < alert['target_price']:
                    triggered = True
                    
                if triggered:
                    msg = f"PRICE ALERT: {alert['crop']} is now {current_price} ({alert['condition']} {alert['target_price']})"
                    notification_service.send_alert(alert['contact'], msg)
        except Exception as e:
            print(f"Error in background job: {e}")
            
        time.sleep(60) # Wait 60 seconds

# Start Background Thread
alert_thread = threading.Thread(target=check_price_alerts, daemon=True)
alert_thread.start()

# Constant data for Market Status (Mock Trends)
MARKET_CROPS = ['Wheat', 'Rice', 'Tomato', 'Potato', 'Onion', 'Cotton']

@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({'error': 'Model not loaded'}), 500

    try:
        data = request.get_json()
        
        # Expected features
        crop = data.get('crop')
        region = data.get('region')
        season = data.get('season')
        temperature = float(data.get('temperature'))
        rainfall = float(data.get('rainfall'))
        humidity = float(data.get('humidity'))
        
        # Create DataFrame for prediction
        input_data = pd.DataFrame([{
            'Crop': crop,
            'Region': region,
            'Season': season,
            'Temperature': temperature,
            'Rainfall': rainfall,
            'Humidity': humidity
        }])
        
        # Predict
        prediction = model.predict(input_data)[0]
        
        # Basic Suggestions based on price (Rule-based simple logic)
        suggestion = "Price seems stable."
        if prediction > 2000:
            suggestion = "Good time to sell! Prices are high."
        elif prediction < 1000:
            suggestion = "Consider holding if possible, prices are low."
            
        trend = "Stable" # Placeholder for trend analysis
        
        return jsonify({
            'predicted_price': round(prediction, 2),
            'suggestion': suggestion,
            'trend': trend
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/analytics', methods=['GET'])
def analytics():
    try:
        if not os.path.exists('crop_prices.csv'):
             # Try absolute path if relative fails (fallback for some envs)
             current_dir = os.path.dirname(os.path.abspath(__file__))
             csv_path = os.path.join(current_dir, 'crop_prices.csv')
             if os.path.exists(csv_path):
                 df = pd.read_csv(csv_path)
             else:
                 return jsonify({'error': 'Data file not found'}), 404
        else:
            df = pd.read_csv('crop_prices.csv')
        
        df = df.dropna() # cleanup

        # 1. Average price per crop
        avg_price = df.groupby('Crop')['Price'].mean().round(2).to_dict()
        
        # 2. Average price per region
        avg_region = df.groupby('Region')['Price'].mean().round(2).to_dict()
        
        # 3. Price trend over time
        trend_data = df[['Date', 'Crop', 'Price']].sort_values('Date').tail(50).to_dict(orient='records')
        
        return jsonify({
            'avg_price_by_crop': avg_price,
            'avg_price_by_region': avg_region,
            'trend_data': trend_data
        })
    except Exception as e:
        print(f"Analytics Error: {e}", flush=True)
        return jsonify({'error': str(e)}), 500

@app.route('/recommend', methods=['POST'])
def recommend():
    if not model:
        return jsonify({'error': 'Model not loaded'}), 500

    try:
        data = request.get_json()
        
        region = data.get('region')
        season = data.get('season')
        # soil_type = data.get('soil_type') # Removed duplicate read
        # rainfall = float(data.get('rainfall')) # Removed duplicate read
        # temperature = float(data.get('temperature')) # Removed duplicate read
        # humidity = float(data.get('humidity')) # Removed duplicate read

        soil_type = data.get('soil_type')
        rainfall = float(data.get('rainfall'))
        temperature = float(data.get('temperature'))
        humidity = float(data.get('humidity'))

        print(f"Received Recommendation Request: {data}", flush=True) # DEBUG LOG

        # 1. Soil Suitability & Rainfall Rules
        suitability = {
            'Clayey': ['Rice', 'Sugarcane', 'Wheat'],
            'Loamy': ['Wheat', 'Maize', 'Sugarcane', 'Cotton', 'Onion', 'Tomato'],
            'Sandy': ['Maize', 'Bajra', 'Potato', 'Onion', 'Groundnut'],
            'Black': ['Cotton', 'Soybean', 'Wheat', 'Sugarcane'],
            'Red': ['Groundnut', 'Tomato', 'Potato', 'Maize']
        }
        
        # Filter 1: Soil Type
        final_candidates = suitability.get(soil_type, [])
        print(f"Soil Type: {soil_type} -> Candidates: {final_candidates}", flush=True)
        
        if not final_candidates:
             print(f"Unknown soil type '{soil_type}', using all crops.", flush=True)
             final_candidates = ['Wheat', 'Rice', 'Maize', 'Sugarcane', 'Cotton', 'Onion', 'Tomato', 'Potato']

        # Filter 2: Rainfall (Simple check)
        filtered_by_rain = []
        for crop in final_candidates:
            if crop == 'Rice' and rainfall < 100:
                continue # Rice needs high water
            if crop == 'Cotton' and rainfall > 250:
                 continue # Cotton sensitive to excess rain
            filtered_by_rain.append(crop)
        
        # If rain filter removes too many, be lenient
        if len(filtered_by_rain) > 0:
            final_candidates = filtered_by_rain
            
        print(f"Candidates after Rain Filter: {final_candidates}", flush=True)

        # 2. Predict Price for each Candidate
        recommendations = []
        for crop in final_candidates:
            # Prepare input vector for model
            input_data = pd.DataFrame([{
                'Crop': crop,
                'Region': region,
                'Season': season,
                'Temperature': temperature,
                'Rainfall': rainfall,
                'Humidity': humidity
            }])
            
            # Predict
            try:
                pred_price = model.predict(input_data)[0]
                recommendations.append({
                    'crop': crop,
                    'predicted_price': round(pred_price, 2)
                })
            except:
                continue # Skip if model encoding fails for some reason
        
        # 3. Sort by Price (High to Low - assuming higher price is better for farmer)
        recommendations = sorted(recommendations, key=lambda x: x['predicted_price'], reverse=True)
        
        return jsonify({
            'recommendations': recommendations,
            'count': len(recommendations),
            'debug_received_soil': soil_type,
            'debug_rainfall': rainfall
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- Alerts API Endpoints ---
@app.route('/alerts', methods=['GET'])
def get_all_alerts():
    try:
        alerts = alerts_db.get_alerts()
        return jsonify(alerts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/alerts', methods=['POST'])
def create_alert():
    try:
        data = request.get_json()
        crop = data.get('crop')
        target_price = float(data.get('target_price'))
        condition = data.get('condition')
        contact = data.get('contact')
        
        if not all([crop, target_price, condition, contact]):
            return jsonify({'error': 'Missing fields'}), 400
            
        alert_id = alerts_db.add_alert(crop, target_price, condition, contact)
        return jsonify({'id': alert_id, 'message': 'Alert created successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/alerts/<int:alert_id>', methods=['DELETE'])
def remove_alert(alert_id):
    try:
        alerts_db.delete_alert(alert_id)
        return jsonify({'message': 'Alert deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/market-status', methods=['GET'])
def market_status():
    status = []
    for crop in MARKET_CROPS:
        price = get_current_price(crop)
        # Mock trend: Randomly assign Up/Down/Stable
        # In real app, compare with previous day's price
        import random
        trend = random.choice(['Up', 'Down', 'Stable']) 
        change = round(random.uniform(0.5, 5.0), 1)
        
        status.append({
            'crop': crop,
            'price': price,
            'trend': trend,
            'change': change
        })
    return jsonify(status)

# Shut down scheduler when app exits
# atexit.register(lambda: scheduler.shutdown()) # Removed

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False) # use_reloader=False to prevent double scheduler triggers
