import pandas as pd
import json

try:
    print("Reading CSV...")
    df = pd.read_csv('crop_prices.csv')
    print(f"CSV Loaded. Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # 1. Average price per crop
    avg_price = df.groupby('Crop')['Price'].mean().to_dict()
    print("Avg Price by Crop calculated.")
    
    # 2. Average price per region
    avg_region = df.groupby('Region')['Price'].mean().to_dict()
    print("Avg Price by Region calculated.")
    
    # 3. Trend
    trend_data = df[['Date', 'Crop', 'Price']].sort_values('Date').tail(50).to_dict(orient='records')
    print("Trend Data calculated.")
    
    result = {
        'avg_price_by_crop': avg_price,
        'avg_price_by_region': avg_region,
        'trend_data': trend_data
    }
    
    # Test JSON serialization (often where it fails if NaNs exist)
    json_output = json.dumps(result)
    print("JSON Serialization successful.")
    print("Sample output:", json_output[:200])
    
except Exception as e:
    print(f"ERROR: {e}")
