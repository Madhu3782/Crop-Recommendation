try:
    import pandas as pd
    import pickle
    import os
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm import SVC
    from sklearn.pipeline import make_pipeline
except ImportError as e:
    print(f"Error: {e}. Please run: pip install scikit-learn pandas")
    exit(1)

def train_intent_model():
    print("Loading Knowledge Base for Intent Training...")
    try:
        df = pd.read_csv('agriculture_knowledge_pro.csv')
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Train a simple but effective TF-IDF + SVM Classifier
    # This is lightweight and works well for small datasets without deep learning overhead
    print("Training Intent Classifier...")
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
    classifier = SVC(kernel='linear', probability=True)
    
    model = make_pipeline(vectorizer, classifier)
    
    # Use questions as features, intents as labels
    X = df['Question']
    y = df['Intent']
    
    model.fit(X, y)
    
    print("Saving Intent Model...")
    with open('intent_model.pkl', 'wb') as f:
        pickle.dump(model, f)
        
    print("Intent Model Trained and Saved to intent_model.pkl")

if __name__ == "__main__":
    train_intent_model()
