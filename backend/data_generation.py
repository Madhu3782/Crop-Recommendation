import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_data(num_rows=1000):
    crops = ['Wheat', 'Rice', 'Maize', 'Sugarcane', 'Cotton', 'Onion', 'Tomato', 'Potato']
    regions = ['Punjab', 'Haryana', 'Uttar Pradesh', 'Maharashtra', 'Karnataka', 'Madhya Pradesh']
    seasons = ['Rabi', 'Kharif', 'Zaid']
    
    data = []
    
    start_date = datetime(2023, 1, 1)
    
    for _ in range(num_rows):
        crop = random.choice(crops)
        region = random.choice(regions)
        season = random.choice(seasons)
        
        # Random date within 2 years
        date = start_date + timedelta(days=random.randint(0, 730))
        
        # Simulate weather data
        temperature = round(random.uniform(10, 45), 1)  # Celsius
        rainfall = round(random.uniform(0, 300), 1)     # mm
        humidity = round(random.uniform(20, 90), 1)     # %
        
        # Base price calculation (simple logic for synthetic data)
        base_price = {
            'Wheat': 2000, 'Rice': 2500, 'Maize': 1800, 
            'Sugarcane': 300, 'Cotton': 5000, 
            'Onion': 1500, 'Tomato': 1000, 'Potato': 800
        }
        
        price = base_price.get(crop, 1000)
        
        # Adjust price based on factors
        if season == 'Kharif' and rainfall < 50:
            price *= 1.2 # Drought increase
        
        if region in ['Punjab', 'Haryana'] and crop in ['Wheat', 'Rice']:
            price *= 0.9 # High supply
            
        # Random fluctuation
        price += random.uniform(-200, 200)
        
        data.append({
            'Crop': crop,
            'Region': region,
            'Season': season,
            'Date': date.strftime('%Y-%m-%d'),
            'Temperature': temperature,
            'Rainfall': rainfall,
            'Humidity': humidity,
            'Price': round(price, 2)
        })
        
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    df = generate_data(1000)
    df.to_csv('crop_prices.csv', index=False)
    print("Synthetic dataset 'crop_prices.csv' generated successfully.")
    print(df.head())
