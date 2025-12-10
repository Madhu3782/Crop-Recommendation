# train_crop_model_v2.py - IMPROVED VERSION
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report

# Geographic constraints (same as in app.py)
GEOGRAPHIC_CROP_ZONES = {
    'Jammu and Kashmir': ['Apple', 'Saffron', 'Walnut', 'Cherry', 'Wheat', 'Maize'],
    'Himachal Pradesh': ['Apple', 'Wheat', 'Maize', 'Barley', 'Potato'],
    'Uttarakhand': ['Rice', 'Wheat', 'Sugarcane', 'Apple', 'Potato', 'Tomato'],
    'Punjab': ['Wheat', 'Rice', 'Maize', 'Sugarcane', 'Cotton'],
    'Haryana': ['Wheat', 'Rice', 'Sugarcane', 'Cotton', 'Bajra'],
    'Delhi': ['Wheat', 'Rice', 'Vegetables'],
    'Uttar Pradesh': ['Wheat', 'Rice', 'Sugarcane', 'Potato', 'Mango', 'Chickpea'],
    'Madhya Pradesh': ['Wheat', 'Rice', 'Soybean', 'Cotton', 'Chickpea', 'Maize'],
    'Chhattisgarh': ['Rice', 'Wheat', 'Maize', 'Groundnut'],
    'Rajasthan': ['Wheat', 'Bajra', 'Maize', 'Cotton', 'Mustard', 'Chickpea'],
    'Gujarat': ['Cotton', 'Groundnut', 'Wheat', 'Rice', 'Sugarcane', 'Bajra'],
    'Maharashtra': ['Cotton', 'Sugarcane', 'Soybean', 'Wheat', 'Rice', 'Grapes', 'Pomegranate', 'Orange'],
    'Goa': ['Rice', 'Coconut', 'Cashew', 'Mango'],
    'Bihar': ['Rice', 'Wheat', 'Maize', 'Sugarcane', 'Jute', 'Lentil'],
    'Jharkhand': ['Rice', 'Wheat', 'Maize', 'Pulses'],
    'Odisha': ['Rice', 'Wheat', 'Sugarcane', 'Jute', 'Coconut'],
    'West Bengal': ['Rice', 'Wheat', 'Jute', 'Potato', 'Sugarcane', 'Tea'],
    'Karnataka': ['Rice', 'Sugarcane', 'Cotton', 'Maize', 'Coffee', 'Coconut', 'Mango', 'Banana', 'Grapes'],
    'Andhra Pradesh': ['Rice', 'Cotton', 'Sugarcane', 'Groundnut', 'Maize', 'Mango', 'Banana'],
    'Telangana': ['Rice', 'Cotton', 'Maize', 'Sugarcane', 'Mango'],
    'Tamil Nadu': ['Rice', 'Sugarcane', 'Cotton', 'Groundnut', 'Coconut', 'Banana', 'Mango'],
    'Kerala': ['Rice', 'Coconut', 'Rubber', 'Tea', 'Coffee', 'Banana', 'Pepper', 'Cardamom'],
    'Assam': ['Rice', 'Tea', 'Jute', 'Sugarcane'],
    'Meghalaya': ['Rice', 'Maize', 'Potato', 'Ginger'],
    'Manipur': ['Rice', 'Wheat', 'Maize', 'Pulses'],
    'Mizoram': ['Rice', 'Maize', 'Ginger'],
    'Nagaland': ['Rice', 'Maize', 'Millets'],
    'Tripura': ['Rice', 'Jute', 'Tea', 'Rubber'],
    'Sikkim': ['Rice', 'Maize', 'Wheat', 'Cardamom', 'Ginger'],
    'Arunachal Pradesh': ['Rice', 'Maize', 'Wheat', 'Millets']
}

def is_valid_crop_for_region(crop, region):
    """Check if crop can grow in this region"""
    if region not in GEOGRAPHIC_CROP_ZONES:
        return True  # Unknown region, allow
    
    allowed_crops = [c.lower() for c in GEOGRAPHIC_CROP_ZONES[region]]
    return crop.lower() in allowed_crops

def clean_and_filter_data(df):
    """
    Filter out impossible crop-region combinations from training data
    This ensures model only learns realistic patterns
    """
    print(f"Original dataset size: {len(df)} rows")
    
    # Create a boolean mask for valid combinations
    valid_mask = df.apply(
        lambda row: is_valid_crop_for_region(row['label'], row['region']),
        axis=1
    )
    
    df_filtered = df[valid_mask].copy()
    removed = len(df) - len(df_filtered)
    
    print(f"Removed {removed} impossible crop-region combinations")
    print(f"Cleaned dataset size: {len(df_filtered)} rows")
    
    return df_filtered

def add_geographic_features(df):
    """
    Add derived features that help model understand climate zones
    """
    # Climate zone classification based on region
    climate_zones = {
        'Cold/Temperate': ['Jammu and Kashmir', 'Himachal Pradesh', 'Uttarakhand', 'Sikkim'],
        'Tropical': ['Kerala', 'Tamil Nadu', 'Goa', 'Andaman and Nicobar Islands'],
        'Subtropical': ['Karnataka', 'Andhra Pradesh', 'Telangana', 'Maharashtra'],
        'Semi-Arid': ['Rajasthan', 'Gujarat', 'parts of Maharashtra'],
        'Humid': ['West Bengal', 'Assam', 'Meghalaya', 'Mizoram'],
        'Continental': ['Punjab', 'Haryana', 'Delhi', 'Uttar Pradesh']
    }
    
    def get_climate_zone(region):
        for zone, states in climate_zones.items():
            if any(state in region for state in states):
                return zone
        return 'Continental'  # Default
    
    df['climate_zone'] = df['region'].apply(get_climate_zone)
    
    # Add season indicator based on temperature
    def get_season(temp):
        if temp < 15:
            return 'Winter'
        elif temp < 25:
            return 'Spring/Autumn'
        elif temp < 35:
            return 'Summer'
        else:
            return 'Extreme_Summer'
    
    df['season_indicator'] = df['temperature'].apply(get_season)
    
    return df

def train_crop_model_enhanced():
    print("=" * 60)
    print("ENHANCED CROP RECOMMENDATION MODEL TRAINING")
    print("=" * 60)
    print("\nLoading dataset...")

    df = pd.read_csv('crop_recommendation.csv')
    df = df.dropna()
    
    print(f"Loaded {len(df)} records with {len(df['label'].unique())} crop types")
    
    # STEP 1: Filter out impossible combinations
    df_clean = clean_and_filter_data(df)
    
    # STEP 2: Add geographic features
    df_enhanced = add_geographic_features(df_clean)
    
    # Features (now including climate_zone and season_indicator)
    X = df_enhanced[['N', 'P', 'K', 'pH', 'temperature', 'humidity', 
                     'rainfall', 'region', 'climate_zone', 'season_indicator']]
    y = df_enhanced['label']
    
    # Enhanced preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), 
             ['region', 'climate_zone', 'season_indicator'])
        ],
        remainder='passthrough'
    )
    
    # Enhanced model with better hyperparameters
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(
            n_estimators=500,           # More trees
            max_depth=25,               # Deeper trees
            min_samples_split=5,        # Prevent overfitting
            min_samples_leaf=2,
            max_features='sqrt',        # Better generalization
            random_state=42,
            n_jobs=-1,                  # Use all CPU cores
            class_weight='balanced'     # Handle imbalanced classes
        ))
    ])
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
    
    print("\n" + "=" * 60)
    print("Training enhanced model...")
    print("=" * 60)
    pipeline.fit(X_train, y_train)
    
    # Evaluation
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("\n" + "=" * 60)
    print("TRAINING RESULTS")
    print("=" * 60)
    print(f"✅ Overall Accuracy: {accuracy * 100:.2f}%")
    
    # Detailed classification report
    print("\nDetailed Performance by Crop:")
    print("-" * 60)
    report = classification_report(y_test, y_pred, output_dict=True)
    
    # Show per-crop accuracy
    for crop in sorted(report.keys()):
        if crop not in ['accuracy', 'macro avg', 'weighted avg']:
            precision = report[crop]['precision']
            recall = report[crop]['recall']
            f1 = report[crop]['f1-score']
            print(f"{crop:20s} | Precision: {precision:.2f} | Recall: {recall:.2f} | F1: {f1:.2f}")
    
    # Feature importance (if needed for debugging)
    feature_names = (
        list(pipeline.named_steps['preprocessor']
             .named_transformers_['cat']
             .get_feature_names_out(['region', 'climate_zone', 'season_indicator'])) +
        ['N', 'P', 'K', 'pH', 'temperature', 'humidity', 'rainfall']
    )
    
    importances = pipeline.named_steps['classifier'].feature_importances_
    top_features = sorted(zip(feature_names, importances), 
                          key=lambda x: x[1], reverse=True)[:10]
    
    print("\nTop 10 Most Important Features:")
    print("-" * 60)
    for feature, importance in top_features:
        print(f"{feature:40s} | {importance:.4f}")
    
    # Save model
    print("\n" + "=" * 60)
    with open('crop_model_enhanced.pkl', 'wb') as f:
        pickle.dump(pipeline, f)
    print("✅ Model saved as 'crop_model_enhanced.pkl'")
    print("=" * 60)
    
    # Save also as regular name for compatibility
    with open('crop_model.pkl', 'wb') as f:
        pickle.dump(pipeline, f)
    print("✅ Also saved as 'crop_model.pkl' (overwrites old model)")
    
    return pipeline

def test_geographic_constraints(model):
    """
    Test that model respects geographic constraints
    """
    print("\n" + "=" * 60)
    print("TESTING GEOGRAPHIC CONSTRAINTS")
    print("=" * 60)
    
    test_cases = [
        {
            'name': 'Apple in Kashmir (SHOULD work)',
            'data': {'N': 50, 'P': 40, 'K': 30, 'pH': 6.5, 
                    'temperature': 15, 'humidity': 60, 'rainfall': 100, 
                    'region': 'Jammu and Kashmir',
                    'climate_zone': 'Cold/Temperate', 'season_indicator': 'Spring/Autumn'},
            'expected_possible': ['Apple', 'Wheat', 'Maize']
        },
        {
            'name': 'Rice in Karnataka (SHOULD work)',
            'data': {'N': 50, 'P': 40, 'K': 30, 'pH': 6.5, 
                    'temperature': 28, 'humidity': 75, 'rainfall': 150, 
                    'region': 'Karnataka',
                    'climate_zone': 'Subtropical', 'season_indicator': 'Summer'},
            'expected_possible': ['Rice', 'Cotton', 'Maize']
        },
        {
            'name': 'Apple in Karnataka (should NOT be top choice)',
            'data': {'N': 50, 'P': 40, 'K': 30, 'pH': 6.5, 
                    'temperature': 28, 'humidity': 65, 'rainfall': 80, 
                    'region': 'Karnataka',
                    'climate_zone': 'Subtropical', 'season_indicator': 'Summer'},
            'expected_impossible': ['Apple']
        }
    ]
    
    for test in test_cases:
        print(f"\n{test['name']}")
        print("-" * 60)
        
        test_df = pd.DataFrame([test['data']])
        probs = model.predict_proba(test_df)[0]
        classes = model.classes_
        
        # Get top 5 predictions
        top_indices = probs.argsort()[-5:][::-1]
        
        print("Top 5 predictions:")
        for i, idx in enumerate(top_indices, 1):
            print(f"  {i}. {classes[idx]:15s} - {probs[idx]*100:.1f}%")
        
        # Check if expected crops are in top predictions
        if 'expected_possible' in test:
            top_3 = [classes[i] for i in top_indices[:3]]
            matches = [c for c in test['expected_possible'] if c in top_3]
            print(f"✅ Expected crops in top 3: {matches}")
        
        if 'expected_impossible' in test:
            top_5 = [classes[i] for i in top_indices[:5]]
            bad_matches = [c for c in test['expected_impossible'] if c in top_5]
            if bad_matches:
                print(f"⚠️  Warning: Impossible crops in top 5: {bad_matches}")
            else:
                print(f"✅ No impossible crops in top 5")

if __name__ == "__main__":
    # Train the enhanced model
    model = train_crop_model_enhanced()
    
    # Test geographic constraints
    test_geographic_constraints(model)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Update your app.py to load 'crop_model.pkl'")
    print("2. Update input data to include 'climate_zone' and 'season_indicator'")
    print("3. Test with different state-crop combinations")
    print("=" * 60)