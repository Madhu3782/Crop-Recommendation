import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np
import os

def build_index():
    print("Building FAISS Index from unified_knowledge_base.csv...")
    
    # Load Unified Data
    csv_file = 'unified_knowledge_base.csv'
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found. Please run merge_knowledge.py first.")
        return

    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} records.")
    
    # Load Model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Create Embeddings
    sentences = df['Question'].tolist()
    embeddings = model.encode(sentences)
    
    # Create FAISS Index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    
    # Save Metadata (Questions & Answers for retrieval)
    metadata = {
        'questions': sentences,
        'answers': df['Answer'].tolist(),
        'intents': df['Intent'].tolist(),
        'topics': df['Topic'].tolist()
    }
    
    # Save Index and Metadata
    faiss.write_index(index, 'chatbot_index.faiss')
    with open('chatbot_metadata.pkl', 'wb') as f:
        pickle.dump(metadata, f)
        
    print("Index built and saved successfully to 'chatbot_index.faiss' and 'chatbot_metadata.pkl'.")

if __name__ == "__main__":
    build_index()
