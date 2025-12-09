import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import pickle

def train_model():
    # Load dataset
    try:
        df = pd.read_csv('crop_prices.csv')
    except FileNotFoundError:
        print("Dataset not found. Please run data_generation.py first.")
        return

    # Features and Target
    X = df[['Crop', 'Region', 'Season', 'Temperature', 'Rainfall', 'Humidity']]
    y = df['Price']

    # Preprocessing
    numerical_features = ['Temperature', 'Rainfall', 'Humidity']
    categorical_features = ['Crop', 'Region', 'Season']

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])

    # Model Pipeline
    model = Pipeline(steps=[('preprocessor', preprocessor),
                            ('regressor', LinearRegression())])

    # Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Model
    print("Training model...")
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Model Training Complete.")
    print(f"Mean Squared Error: {mse:.2f}")
    print(f"R^2 Score: {r2:.2f}")

    # Save Model
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("Model saved as 'model.pkl'.")

if __name__ == "__main__":
    train_model()
