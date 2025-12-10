# train_crop_model.py
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

    df = pd.read_csv('crop_recommendation.csv')
    df = df.dropna()

    # X features (you added region column yourself)
    X = df[['N', 'P', 'K', 'pH', 'temperature', 'humidity', 'rainfall', 'region']]
    # y = crop name (multi-class)
    y = df['label']

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['region'])
        ],
        remainder='passthrough'
    )

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(
            n_estimators=350,
            max_depth=20,
            random_state=42
        ))
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print("Training model...")
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Training Complete. Accuracy: {accuracy * 100:.2f}%")

    with open('crop_model.pkl', 'wb') as f:
        pickle.dump(pipeline, f)

    print("Model saved as crop_model.pkl")

if __name__ == "__main__":
    train_crop_model()





# import pandas as pd
# import pickle
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.preprocessing import OneHotEncoder
# from sklearn.compose import ColumnTransformer
# from sklearn.pipeline import Pipeline
# from sklearn.metrics import accuracy_score

# def train_crop_model():
#     print("Loading dataset...")

#     df = pd.read_csv('crop_recommendation.csv')

#     # IMPORTANT: Drop rows where any inputs are missing
#     df = df.dropna()

#     # ===== Features and Target =====
#     X = df[['N', 'P', 'K', 'pH', 'temperature', 'humidity', 'rainfall', 'region']]
#     y = df['label']   # 1 = suitable, 0 = not suitable

#     # ===== Encoding for region =====
#     preprocessor = ColumnTransformer(
#         transformers=[
#             ('cat', OneHotEncoder(handle_unknown='ignore'), ['region'])
#         ],
#         remainder='passthrough'
#     )

#     # ===== ML Pipeline =====
#     pipeline = Pipeline(steps=[
#         ('preprocessor', preprocessor),
#         ('classifier', RandomForestClassifier(
#             n_estimators=350,
#             max_depth=20,
#             random_state=42
#         ))
#     ])

#     # ===== Train/Test Split =====
#     X_train, X_test, y_train, y_test = train_test_split(
#         X, y,
#         test_size=0.2,
#         random_state=42,
#         stratify=y
#     )

#     print("Training model...")
#     pipeline.fit(X_train, y_train)

#     # ===== Evaluation =====
#     y_pred = pipeline.predict(X_test)
#     accuracy = accuracy_score(y_test, y_pred)

#     print(f"Training Complete.")
#     print(f"Suitability Model Accuracy: {accuracy * 100:.2f}%")

#     # ===== Save the ML Model =====
#     with open('crop_suitability_model.pkl', 'wb') as f:
#         pickle.dump(pipeline, f)

#     print("Model saved as crop_suitability_model.pkl")

# if __name__ == "__main__":
#     train_crop_model()
