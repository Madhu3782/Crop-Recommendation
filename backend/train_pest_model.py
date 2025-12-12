import pandas as pd
import numpy as np
import random
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import pickle
import os

# 1. Generate Synthetic Dataset
def generate_pest_data(n_samples=1000):
    crops = ['Wheat', 'Rice', 'Maize', 'Sugarcane', 'Cotton', 'Tomato', 'Potato']
    regions = ['Punjab', 'Haryana', 'Uttar Pradesh', 'Maharashtra', 'Karnataka']
    
    data = []
    
    for _ in range(n_samples):
        crop = random.choice(crops)
        region = random.choice(regions)
        temp = round(random.uniform(15, 40), 1)
        humidity = round(random.uniform(30, 90), 1)
        rainfall = round(random.uniform(0, 150), 1)
        
        # Simple logic for synthetic ground truth (to make model learnable)
        # High temp + High humidity = Higher risk for many pests
        risk_score = 10  # Base risk
        
        if humidity > 70:
            risk_score += 30
        if temp > 25 and temp < 35:
            risk_score += 20
        if rainfall > 50:
            risk_score += 15
        
        # Crop specific adjustments
        if crop == 'Cotton' and humidity > 60:
            risk_score += 10
        if crop == 'Potato' and humidity > 80:
            risk_score += 20
            
        # Random noise
        risk_score += random.randint(-10, 10)
        risk_score = max(0, min(100, risk_score))
        
        data.append([crop, region, temp, humidity, rainfall, risk_score])
        
    df = pd.DataFrame(data, columns=['Crop', 'Region', 'Temperature', 'Humidity', 'Rainfall', 'Pest_Risk_Score'])
    return df

print("Generating synthetic pest dataset...")
df = generate_pest_data(2000)
df.to_csv('pest_dataset.csv', index=False)
print("Dataset saved to pest_dataset.csv")

# 2. Preprocessing
le_crop = LabelEncoder()
le_region = LabelEncoder()

df['Crop'] = le_crop.fit_transform(df['Crop'])
df['Region'] = le_region.fit_transform(df['Region'])

X = df[['Crop', 'Region', 'Temperature', 'Humidity', 'Rainfall']]
y = df['Pest_Risk_Score']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Model Training
print("Training RandomForestRegressor...")
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print(f"Model Score: {model.score(X_test, y_test):.4f}")

# 4. Save Model & Encoders
artifacts = {
    'model': model,
    'le_crop': le_crop,
    'le_region': le_region
}

with open('pest_model.pkl', 'wb') as f:
    pickle.dump(artifacts, f)

print("Model and encoders saved to pest_model.pkl")
