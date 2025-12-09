import pandas as pd
import numpy as np
import random

def generate_data(num_samples=2000):
    # Crops and their general "ideal" conditions (very rough approximations for synthetic relationships)
    # This ensures the model has patterns to learn.
    crops_profile = {
        'Rice': {'N': (60, 90), 'P': (35, 60), 'K': (35, 45), 'pH': (6.0, 7.5), 'Temp': (20, 35), 'Hum': (70, 90), 'Rain': (150, 300)},
        'Maize': {'N': (60, 90), 'P': (40, 60), 'K': (19, 25), 'pH': (5.5, 7.0), 'Temp': (18, 27), 'Hum': (50, 70), 'Rain': (60, 100)},
        'Chickpea': {'N': (20, 40), 'P': (55, 80), 'K': (35, 45), 'pH': (6.0, 7.5), 'Temp': (17, 25), 'Hum': (15, 30), 'Rain': (40, 60)},
        'Kidneybeans': {'N': (15, 25), 'P': (55, 70), 'K': (15, 25), 'pH': (5.5, 6.0), 'Temp': (15, 25), 'Hum': (15, 25), 'Rain': (60, 150)},
        'Pigeonpeas': {'N': (20, 40), 'P': (55, 75), 'K': (20, 30), 'pH': (5.0, 7.0), 'Temp': (25, 35), 'Hum': (15, 30), 'Rain': (80, 150)},
        'Mothbeans': {'N': (15, 25), 'P': (35, 55), 'K': (15, 25), 'pH': (4.0, 9.0), 'Temp': (24, 32), 'Hum': (30, 60), 'Rain': (30, 70)},
        'Mungbean': {'N': (15, 25), 'P': (35, 55), 'K': (15, 25), 'pH': (6.2, 7.2), 'Temp': (27, 30), 'Hum': (60, 70), 'Rain': (40, 60)},
        'Blackgram': {'N': (35, 45), 'P': (55, 70), 'K': (15, 25), 'pH': (6.5, 7.5), 'Temp': (25, 35), 'Hum': (60, 70), 'Rain': (60, 80)},
        'Lentil': {'N': (15, 25), 'P': (55, 70), 'K': (15, 25), 'pH': (6.0, 7.5), 'Temp': (18, 30), 'Hum': (15, 30), 'Rain': (35, 50)},
        'Pomegranate': {'N': (15, 25), 'P': (15, 35), 'K': (35, 45), 'pH': (5.5, 7.0), 'Temp': (18, 25), 'Hum': (80, 95), 'Rain': (100, 120)},
        'Banana': {'N': (90, 110), 'P': (70, 95), 'K': (45, 55), 'pH': (5.5, 6.5), 'Temp': (25, 30), 'Hum': (75, 85), 'Rain': (90, 120)},
        'Mango': {'N': (15, 30), 'P': (15, 30), 'K': (25, 35), 'pH': (5.0, 6.5), 'Temp': (27, 35), 'Hum': (45, 55), 'Rain': (90, 100)},
        'Grapes': {'N': (15, 30), 'P': (125, 140), 'K': (195, 205), 'pH': (5.5, 6.5), 'Temp': (10, 35), 'Hum': (75, 85), 'Rain': (60, 80)},
        'Watermelon': {'N': (90, 110), 'P': (10, 30), 'K': (45, 55), 'pH': (6.0, 7.0), 'Temp': (24, 28), 'Hum': (80, 90), 'Rain': (40, 60)},
        'Muskmelon': {'N': (90, 120), 'P': (10, 30), 'K': (45, 55), 'pH': (6.0, 6.8), 'Temp': (27, 30), 'Hum': (80, 90), 'Rain': (40, 60)},
        'Apple': {'N': (15, 40), 'P': (125, 140), 'K': (195, 205), 'pH': (5.5, 6.5), 'Temp': (21, 24), 'Hum': (90, 95), 'Rain': (100, 120)},
        'Orange': {'N': (15, 30), 'P': (10, 30), 'K': (5, 15), 'pH': (6.0, 7.5), 'Temp': (10, 35), 'Hum': (90, 95), 'Rain': (100, 120)},
        'Papaya': {'N': (40, 60), 'P': (30, 60), 'K': (45, 55), 'pH': (6.5, 7.0), 'Temp': (25, 40), 'Hum': (90, 95), 'Rain': (150, 250)},
        'Coconut': {'N': (15, 30), 'P': (10, 30), 'K': (25, 35), 'pH': (5.0, 6.0), 'Temp': (25, 29), 'Hum': (80, 95), 'Rain': (150, 250)},
        'Cotton': {'N': (110, 130), 'P': (40, 60), 'K': (15, 25), 'pH': (6.0, 8.0), 'Temp': (22, 28), 'Hum': (50, 70), 'Rain': (60, 100)},
        'Jute': {'N': (70, 90), 'P': (40, 60), 'K': (35, 45), 'pH': (6.0, 7.4), 'Temp': (23, 26), 'Hum': (70, 90), 'Rain': (150, 200)},
        'Coffee': {'N': (90, 110), 'P': (15, 30), 'K': (25, 35), 'pH': (6.0, 7.0), 'Temp': (23, 28), 'Hum': (50, 70), 'Rain': (120, 200)}
    }

    districts = ['Davanagere', 'Belagavi', 'Shivamogga', 'Tumakuru', 'Mysuru', 
                 'Mandya', 'Hassan', 'Chitradurga', 'Ballari', 'Vijayapura']
    
    data = []
    
    for _ in range(num_samples):
        # Pick a random crop
        crop = random.choice(list(crops_profile.keys()))
        profile = crops_profile[crop]
        
        # Generate features with some noise around the ideal
        row = {
            'N': int(random.uniform(profile['N'][0]-5, profile['N'][1]+5)),
            'P': int(random.uniform(profile['P'][0]-5, profile['P'][1]+5)),
            'K': int(random.uniform(profile['K'][0]-5, profile['K'][1]+5)),
            'pH': round(random.uniform(profile['pH'][0]-0.2, profile['pH'][1]+0.2), 1),
            'temperature': round(random.uniform(profile['Temp'][0]-2, profile['Temp'][1]+2), 1),
            'humidity': round(random.uniform(profile['Hum'][0]-5, profile['Hum'][1]+5), 1),
            'rainfall': round(random.uniform(profile['Rain'][0]-20, profile['Rain'][1]+20), 1),
            'region': random.choice(districts),
            'label': crop
        }
        data.append(row)
        
    df = pd.DataFrame(data)
    df.to_csv('crop_recommendation.csv', index=False)
    print(f"Generated {num_samples} samples in crop_recommendation.csv")

if __name__ == "__main__":
    generate_data()
