import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

def train_crop_model():
    print("Loading dataset...")
    try:
        df = pd.read_csv('crop_recommendation.csv')
    except FileNotFoundError:
        print("Error: crop_recommendation.csv not found.")
        return

    X = df[['N', 'P', 'K', 'pH', 'temperature', 'humidity', 'rainfall', 'region']]
    y = df['label']

    # Preprocessing
    # 'region' needs OneHotEncoding. Others are numerical.
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['region'])
        ],
        remainder='passthrough' # Keep N, P, K, pH etc as is
    )

    # Pipeline
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train
    print("Training Random Forest Classifier...")
    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Training Complete.")
    print(f"Accuracy: {accuracy * 100:.2f}%")

    # Save
    with open('crop_model.pkl', 'wb') as f:
        pickle.dump(pipeline, f)
    print("Model saved to crop_model.pkl")

if __name__ == "__main__":
    train_crop_model()
