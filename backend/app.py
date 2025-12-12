from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import pandas as pd
import numpy as np
import atexit
import alerts_db
import notification_service
import os
import requests
import threading
import notification_service
import os
import requests
import threading
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from chatbot_brain import brain as chatbot # Import Chatbot Brain Instance

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# --- Load Models ---
model_price = None
model_crop = None

# 1. Load Price Model (Old)
try:
    with open('model.pkl', 'rb') as f:
        model_price = pickle.load(f)
    print("Price Model loaded successfully.")
except FileNotFoundError:
    print("Warning: model.pkl (Price Model) not found.")

# 2. Load Crop Recommendation Model (New)
try:
    with open('crop_model.pkl', 'rb') as f:
        model_crop = pickle.load(f)
    print("Crop Model loaded successfully.")
except FileNotFoundError:
    print("Warning: crop_model.pkl (Crop Model) not found. Run train_crop_model.py.")

# Initialize Database
try:
    alerts_db.init_db()
    print("Alerts Database Initialized.")
except Exception as e:
    print(f"Error initializing DB: {e}")

# 3. Load Pest Prediction Model
model_pest = None
le_crop_pest = None
le_region_pest = None

try:
    with open('pest_model.pkl', 'rb') as f:
        artifacts = pickle.load(f)
        model_pest = artifacts['model']
        le_crop_pest = artifacts['le_crop']
        le_region_pest = artifacts['le_region']
    print("Pest Model loaded successfully.")
except Exception as e:
    print(f"Warning: pest_model.pkl not found or error loading ({e}). Using fallback logic.")

# --- Register Models with Brain ---
chatbot.register_models(model_price, model_crop, model_pest)


# --- Configuration ---
OPENWEATHERMAP_API_KEY = "576ae4521e15eb503d6be233a2aa1381"

# --- Knowledge Base for Suitability Checks ---
# (Ideal ranges for suitability verification)
SUITABILITY_DICT = {
    'Rice': {'min_rain': 150, 'max_rain': 300, 'min_temp': 20, 'max_temp': 35},
    'Maize': {'min_rain': 60, 'max_rain': 110, 'min_temp': 18, 'max_temp': 30},
    'Cotton': {'min_rain': 50, 'max_rain': 110, 'min_temp': 20, 'max_temp': 30},
    'Kidneybeans': {'min_rain': 60, 'max_rain': 150, 'min_temp': 15, 'max_temp': 25},
    'Pigeonpeas': {'min_rain': 80, 'max_rain': 150, 'min_temp': 20, 'max_temp': 35},
    'Mothbeans': {'min_rain': 30, 'max_rain': 80, 'min_temp': 20, 'max_temp': 35},
    'Mungbean': {'min_rain': 35, 'max_rain': 75, 'min_temp': 25, 'max_temp': 35},
    'Blackgram': {'min_rain': 50, 'max_rain': 90, 'min_temp': 20, 'max_temp': 35},
    'Lentil': {'min_rain': 30, 'max_rain': 60, 'min_temp': 15, 'max_temp': 32},
    'Pomegranate': {'min_rain': 90, 'max_rain': 130, 'min_temp': 15, 'max_temp': 30},
    'Banana': {'min_rain': 90, 'max_rain': 140, 'min_temp': 20, 'max_temp': 35},
    'Mango': {'min_rain': 80, 'max_rain': 110, 'min_temp': 20, 'max_temp': 38},
    'Grapes': {'min_rain': 50, 'max_rain': 90, 'min_temp': 10, 'max_temp': 35},
    'Watermelon': {'min_rain': 30, 'max_rain': 70, 'min_temp': 20, 'max_temp': 30},
    'Muskmelon': {'min_rain': 30, 'max_rain': 70, 'min_temp': 22, 'max_temp': 30},
    'Apple': {'min_rain': 90, 'max_rain': 130, 'min_temp': 15, 'max_temp': 25},
    'Orange': {'min_rain': 90, 'max_rain': 130, 'min_temp': 10, 'max_temp': 35},
    'Papaya': {'min_rain': 140, 'max_rain': 260, 'min_temp': 20, 'max_temp': 40},
    'Coconut': {'min_rain': 140, 'max_rain': 260, 'min_temp': 23, 'max_temp': 32},
    'Jute': {'min_rain': 140, 'max_rain': 210, 'min_temp': 22, 'max_temp': 28},
    'Coffee': {'min_rain': 110, 'max_rain': 210, 'min_temp': 20, 'max_temp': 30},
    'Chickpea': {'min_rain': 35, 'max_rain': 70, 'min_temp': 15, 'max_temp': 28}
}

# --- Helper to get Current Price (Simulated) ---
def get_current_price(crop, region="Uttar Pradesh"): 
    if not model_price:
        return 0
    
    input_data = pd.DataFrame([{
        'Crop': crop,
        'Region': region,
        'Season': 'Rabi',
        'Temperature': 25.0,
        'Rainfall': 100.0,
        'Humidity': 50.0
    }])
    try:
        price = model_price.predict(input_data)[0]
        # Add some random fluctuation to make it interesting
        import random
        fluctuation = random.uniform(-50, 50)
        return round(price + fluctuation, 2)
    except:
        return 0

# --- Helper to get Weather Data ---
def get_weather_data(district):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={district}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()
        
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        
        rain = 0
        if 'rain' in data and '1h' in data['rain']:
            rain = data['rain']['1h'] * 24 # Crude approximation to daily rainfall
        
        # If no rain reported but high humidity, assume some minimal moisture
        if rain == 0 and humidity > 80:
            rain = 5.0 
            
        return {'temperature': temp, 'humidity': humidity, 'rainfall': round(rain, 2)}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather for {district}: {e}")
        return None
    except KeyError as e:
        print(f"Key error in weather data for {district}: {e}. Response: {data}")
        return None

# --- Helper: Calculate Match Score (Rule-based) ---
def calculate_match_score(crop, inputs):
    # Returns a score 0-100 based on how well inputs match ideal conditions
    if crop not in SUITABILITY_DICT:
        return 50 # Neutral if unknown
        
    ideal = SUITABILITY_DICT[crop]
    score = 100
    penalties = 0
    
    # Rainfall Check
    if inputs['rainfall'] < ideal['min_rain']:
        # Penalize proportional to deviation
        diff = ideal['min_rain'] - inputs['rainfall']
        penalties += min(40, diff * 0.5) 
    elif inputs['rainfall'] > ideal['max_rain']:
        diff = inputs['rainfall'] - ideal['max_rain']
        penalties += min(40, diff * 0.5)
        
    # Temp Check
    if inputs['temperature'] < ideal['min_temp']:
        diff = ideal['min_temp'] - inputs['temperature']
        penalties += min(30, diff * 2)
    elif inputs['temperature'] > ideal['max_temp']:
        diff = inputs['temperature'] - ideal['max_temp']
        penalties += min(30, diff * 2)

    # NPK and pH checks (new additions)
    if 'min_N' in ideal and inputs['N'] < ideal['min_N']:
        penalties += 5
    if 'max_N' in ideal and inputs['N'] > ideal['max_N']:
        penalties += 5
    if 'min_P' in ideal and inputs['P'] < ideal['min_P']:
        penalties += 5
    if 'max_P' in ideal and inputs['P'] > ideal['max_P']:
        penalties += 5
    if 'min_K' in ideal and inputs['K'] < ideal['min_K']:
        penalties += 5
    if 'max_K' in ideal and inputs['K'] > ideal['max_K']:
        penalties += 5
    if 'min_pH' in ideal and inputs['pH'] < ideal['min_pH']:
        penalties += 5
    if 'max_pH' in ideal and inputs['pH'] > ideal['max_pH']:
        penalties += 5
        
    return max(0, score - penalties)

# --- Background Job: Check Alerts ---
def check_price_alerts():
    # Run forever in a separate thread
    while True:
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

# --- NEW: Weather Fetch Endpoint ---
@app.route('/fetch_weather', methods=['GET'])
def fetch_weather():
    state = request.args.get('state')
    district = request.args.get('district')
    
    if not district:
        return jsonify({'error': 'District is required'}), 400
        
    # OpenWeatherMap API Call
    # Note: OWM usually works with City, Country code. We will try passing district name directly.
    url = f"http://api.openweathermap.org/data/2.5/weather?q={district}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant fields
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            
            # Rainfall: 'rain' object might be missing if no rain
            rain = 0
            if 'rain' in data:
                rain = data['rain'].get('1h', 0) * 24 # Crude approximation to daily/periodic if needed
            
            # Since ML needs average rainfall (mm) and API gives current snapshot,
            # we will set a minimal default if it's 0 to avoid rejection by suitability checks for water-loving crops in dry weather.
            # This is a limitation of using real-time weather for long-term crop planning.
            if rain == 0 and humidity > 80:
                rain = 5.0 # Light rain assumed if very humid
            
            return jsonify({
                'temperature': temp,
                'humidity': humidity,
                'rainfall': round(rain, 2)
            })
        else:
             return jsonify({'error': 'Weather data not available for this district.'}), 404
             
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# These below this helps for the crop recommendation system for the ML Model like getClimate and get season also
# the are the helper function
    
def get_climate_zone(region):
    climate_zones = {
        'Cold/Temperate': ['Jammu and Kashmir', 'Himachal Pradesh', 'Uttarakhand', 'Sikkim'],
        'Tropical': ['Kerala', 'Tamil Nadu', 'Goa'],
        'Subtropical': ['Karnataka', 'Andhra Pradesh', 'Telangana', 'Maharashtra'],
        'Semi-Arid': ['Rajasthan', 'Gujarat'],
        'Humid': ['West Bengal', 'Assam', 'Meghalaya', 'Mizoram'],
        'Continental': ['Punjab', 'Haryana', 'Delhi', 'Uttar Pradesh']
    }
    for zone, states in climate_zones.items():
        if region in states:
            return zone
    return 'Continental'  # fallback
def get_season(temp):
    if temp < 15:
        return 'Winter'
    elif temp < 25:
        return 'Spring/Autumn'
    elif temp < 35:
        return 'Summer'
    else:
        return 'Extreme_Summer'
    
def get_altitude(region):
    default = 600
    return {
        'Karnataka': 700,
        'Kerala': 1000,
        'Jammu and Kashmir': 1600,
        'Himachal Pradesh': 1800
    }.get(region, default)

def get_terrain(region):
    return {
        'Karnataka': 'Plain',
        'Kerala': 'Mountain',
        'Himachal Pradesh': 'Hilly',
        'Jammu and Kashmir': 'Mountain'
    }.get(region, 'Plain')


    
    

# --- NEW: Crop Recommendation + Suitability Check Endpoint ---
@app.route('/predict', methods=['POST'])
def predict_crop():
    """
    Two modes:

    A) If 'crop' is NOT sent in body  -> return TOP 3 best crops (recommendation mode)
    B) If 'crop' IS sent              -> return if THAT crop is suitable or not (yes/no mode)
    """
    if not model_crop:
        return jsonify({'error': 'Crop Model not loaded'}), 500

    try:
        data = request.get_json()

        region = data.get('region')
        try:
           inputs = {
    'N': float(data.get('N')),
    'P': float(data.get('P')),
    'K': float(data.get('K')),
    'pH': float(data.get('pH')),
    'temperature': float(data.get('temperature')),
    'humidity': float(data.get('humidity')),
    'rainfall': float(data.get('rainfall')),
    'altitude': float(data.get('altitude')),
    'terrain': data.get('terrain')
}

        except (ValueError, TypeError):
            return jsonify({'result': "Error: Please enter valid numerical values for all fields."})

        # Build input row for ML model
        climate_zone = get_climate_zone(region)
        altitude = get_altitude(region)
        terrain = get_terrain(region)
        season_indicator = get_season(inputs['temperature'])


        input_df = pd.DataFrame([{
    'N': inputs['N'],
    'P': inputs['P'],
    'K': inputs['K'],
    'pH': inputs['pH'],
    'temperature': inputs['temperature'],
    'humidity': inputs['humidity'],
    'rainfall': inputs['rainfall'],

    'region': region,
    'climate_zone': climate_zone,
    'season_indicator': season_indicator,

    'altitude': inputs['altitude'],
    'terrain': inputs['terrain']
}])


        # Get probabilities for all crops from ML model
        probs = model_crop.predict_proba(input_df)[0]   # e.g. [0.1, 0.5, ...]
        classes = model_crop.classes_                   # crop names from training

        # ---------- MODE B: Single crop suitability check ----------
        target_crop_raw = data.get('crop', '').strip()
        if target_crop_raw:
            # Case-insensitive match between user input and model classes
            class_lookup = {c.lower(): c for c in classes}
            key = target_crop_raw.lower()

            if key not in class_lookup:
                return jsonify({'result': f"❌ Crop '{target_crop_raw}' not recognized by the model."}), 400

            crop_name = class_lookup[key]                  # canonical name from model
            idx = list(classes).index(crop_name)
            ml_conf = probs[idx] * 100                     # 0–100%

            # Agro rule-based score (from SUITABILITY_DICT) – uses temp, rain, NPK, pH
            agro_score = calculate_match_score(crop_name.title(), inputs)
            # If crop is not in SUITABILITY_DICT, calculate_match_score returns 50

            # Final combined score
            final_score = (agro_score * 0.6) + (ml_conf * 0.4)

            suitable = final_score >= 50  # threshold; tune if needed
            # ---- Improved Suitability Check for Realistic Output ----
            suitable = True

# Rule 1: ML confidence too low = reject
            if ml_conf < 25:
                suitable = False

# Rule 2: Agro match too low = reject
            if agro_score < 30:
                suitable = False

# Rule 3: Final score too low = reject
            if final_score < 50:
                suitable = False


            if suitable:
                response_text = (
                    f"✔ {crop_name} is SUITABLE for {region}.\n"
                    f"Overall Suitability Score: {int(final_score)}%\n"
                    f"ML confidence: {ml_conf:.1f}% | Agro suitability: {int(agro_score)}%\n"
                    f"Reason: Temperature ({inputs['temperature']}°C), "
                    f"Humidity ({inputs['humidity']}%), and Rainfall ({inputs['rainfall']}mm) "
                    f"are within acceptable range for {crop_name}."
                )
            else:
                # Suggest top 3 alternative crops as backup
                ranked = []
                for i, c in enumerate(classes):
                    ml_c = probs[i] * 100
                    agro_c = calculate_match_score(c.title(), inputs)
                    final_c = (agro_c * 0.6) + (ml_c * 0.4)
                    ranked.append((c, final_c))

                ranked.sort(key=lambda x: x[1], reverse=True)
                alternatives = [c for c, s in ranked if c != crop_name][:3]
                alt_str = ', '.join(alternatives) if alternatives else 'No strong alternatives found'

                response_text = (
                    f"❌ {crop_name} is NOT suitable for {region}.\n"
                    f"Overall Suitability Score: {int(final_score)}%\n"
                    f"ML confidence: {ml_conf:.1f}% | Agro suitability: {int(agro_score)}%\n"
                    f"Suggested Alternatives: {alt_str}."
                )

            return jsonify({'result': response_text})

        # ---------- MODE A: General recommendation (no crop provided) ----------
        ranked_crops = []
        for i, crop_name in enumerate(classes):
            ml_confidence = probs[i] * 100        # 0–100
            if ml_confidence < 2:
                continue

            agro_score = calculate_match_score(crop_name.title(), inputs)
            final_score = (agro_score * 0.6) + (ml_confidence * 0.4)

            if final_score > 30:
                ranked_crops.append({
                    'crop': crop_name,
                    'score': round(final_score),
                    'agro_score': agro_score,
                    'ml_score': round(ml_confidence, 1)
                })

        ranked_crops.sort(key=lambda x: x['score'], reverse=True)
        top_crops = ranked_crops[:3]

        if not top_crops:
            response_text = (
                "❌ No major crop found suitable for these specific conditions.\n"
                "Reason: Rainfall or Nutrients might be too extreme for standard crops.\n"
                "Try improving irrigation or soil amendments."
            )
        else:
            list_str = ""
            for i, item in enumerate(top_crops):
                list_str += f"{i+1}) {item['crop']} — Suitability: {int(item['score'])}%\n"

            best = top_crops[0]
            response_text = (
                f"🌾 Best Crops for your conditions:\n"
                f"{list_str}\n"
                f"Reason:\nTemperature ({inputs['temperature']}°C), "
                f"Humidity ({inputs['humidity']}%), and Rainfall ({inputs['rainfall']}mm) "
                f"match ideal conditions for {best['crop']}."
            )

        return jsonify({'result': response_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 400


# --- Currently Runnig  Price Prediction (Renamed) ---
@app.route('/predict-price', methods=['POST'])
def predict_price():
    if not model_price:
        return jsonify({'error': 'Price Model not loaded'}), 500

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
        prediction = model_price.predict(input_data)[0]
        
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
    
# Analytics

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


# Recommendations Endpoint (Original implementation - kept for compatibility)
@app.route('/recommend-crops-by-price', methods=['POST'])
def recommend_by_price():
    if not model_price:
        return jsonify({'error': 'Model not loaded'}), 500

    try:
        data = request.get_json()
        
        region = data.get('region')
        season = data.get('season')
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
                pred_price = model_price.predict(input_data)[0]
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
def get_all_alerts_route():
    try:
        alerts = alerts_db.get_alerts()
        return jsonify(alerts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/alerts', methods=['POST'])
def create_alert_route():
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
def remove_alert_route(alert_id):
    try:
        alerts_db.delete_alert(alert_id)
        return jsonify({'message': 'Alert deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/market-status', methods=['GET'])
def market_status_route():
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

# State and district route
@app.route('/states', methods=['GET'])
def get_states():
    try:
        res = requests.get("https://cdn-api.co-vin.in/api/v2/admin/location/states")
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)})
@app.route('/districts/<state_id>', methods=['GET'])
def get_districts(state_id):
    try:
        res = requests.get(f"https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state_id}")
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)})

# --- Pest Attack Prediction Endpoint ---
@app.route('/predict_pest_risk', methods=['POST'])
def predict_pest_risk():
    try:
        data = request.get_json()
        crop = data.get('crop', 'Wheat')
        region = data.get('region', 'Punjab')
        temp = float(data.get('temperature', 25))
        humidity = float(data.get('humidity', 60))
        rainfall = float(data.get('rainfall', 0))

        # 1. Map Crop to Likely Pest (Simple Knowledge Base)
        pest_map = {
            'Wheat': 'Yellow Rust',
            'Rice': 'Stem Borer',
            'Maize': 'Fall Armyworm',
            'Sugarcane': 'Woolly Aphid',
            'Cotton': 'Pink Bollworm',
            'Tomato': 'Late Blight',
            'Potato': 'Early Blight'
        }
        pest_name = pest_map.get(crop, 'General Pest')

        # 2. Simulate 7-Day Forecast (Mocking API data for future days based on current)
        next_7_days_risk = []
        
        # Base input encoders
        crop_enc = 0
        region_enc = 0
        
        if model_pest and le_crop_pest:
            try:
                crop_enc = le_crop_pest.transform([crop])[0]
                region_enc = le_region_pest.transform([region])[0]
            except:
                pass 

        current_risk_score = 0
        
        for day in range(7):
            # Simulate weather fluctuation
            sim_temp = temp + np.random.uniform(-2, 3)
            sim_hum = humidity + np.random.uniform(-5, 5)
            sim_rain = max(0, rainfall + np.random.uniform(-10, 10))
            
            risk = 0
            if model_pest:
                # Predict using ML model
                input_vector = pd.DataFrame([{
                    'Crop': crop_enc, 
                    'Region': region_enc, 
                    'Temperature': sim_temp, 
                    'Humidity': sim_hum, 
                    'Rainfall': sim_rain
                }])
                try:
                    risk = model_pest.predict(input_vector)[0]
                except:
                    risk = 50 # Model error fallback
            else:
                # Fallback Logic (if training failed/model missing)
                risk = 20 # Base
                if sim_hum > 80: risk += 40
                if sim_temp > 28 and sim_temp < 35: risk += 20
                if sim_rain > 50: risk += 10
                
            risk = max(0, min(100, risk))
            next_7_days_risk.append(int(risk))

        # Current Risk (Day 0)
        current_risk_score = next_7_days_risk[0]
        
        # Risk Level
        risk_level = "Low"
        if current_risk_score > 60: risk_level = "High"
        elif current_risk_score > 30: risk_level = "Medium"

        # Recommended Spray Day
        max_risk = max(next_7_days_risk)
        spray_day = next_7_days_risk.index(max_risk) + 1 

        return jsonify({
            'pest_name': pest_name,
            'risk_score': current_risk_score,
            'risk_level': risk_level,
            'next_7_days': next_7_days_risk,
            'recommended_spray_day': spray_day
        })

    except Exception as e:
        print(f"Error in pest prediction: {e}")
        return jsonify({'error': str(e)}), 500


# --- Chatbot Endpoint ---
@app.route('/chatbot', methods=['POST'])
def chatbot_endpoint():
    try:
        data = request.get_json()
        question = data.get('question')
        language = data.get('language', 'English')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
            
        # Use brain to generate response
        # Returns dict: {'answer_en': ..., 'answer_translated': ..., 'language': ...}
        response_data = chatbot.generate_response(question, language=language)
        
        return jsonify({
            'answer': response_data['answer_translated'], # Main display answer
            'answer_en': response_data['answer_en'],      # Original Reference
            'language': response_data['language']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Shut down scheduler when app exits
# atexit.register(lambda: scheduler.shutdown()) # Removed

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False) # use_reloader=False to prevent double scheduler triggers
