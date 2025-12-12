import pandas as pd
import pickle
import os
import random

# Global flags
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    ML_AVAILABLE = True
except Exception as e:
    ML_AVAILABLE = False
    print(f"Chatbot: ML Import Error: {e}")

class ChatbotEngine:
    def __init__(self):
        self.model = None
        self.index = None
        self.metadata = None
        self.fallback_data = None
        
        if ML_AVAILABLE:
            self.load_ml_components()
        else:
            print("Chatbot: ML libraries not found. Using Keyword Fallback Mode.")
            self.load_fallback_data()

    def load_ml_components(self):
        try:
            print("Chatbot: Loading ML Model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            if os.path.exists('chatbot_index.faiss') and os.path.exists('chatbot_metadata.pkl'):
                print("Chatbot: Loading Index...")
                self.index = faiss.read_index('chatbot_index.faiss')
                with open('chatbot_metadata.pkl', 'rb') as f:
                    self.metadata = pickle.load(f)
            else:
                print("Chatbot: Index not found. Please run build_chatbot_index.py")
                # Fallback to pure logic if index missing even if ML lib exists
                self.load_fallback_data()
                
        except Exception as e:
            print(f"Chatbot: Error loading ML components: {e}")
            self.load_fallback_data()

    def load_fallback_data(self):
        # Load CSV into memory for simple keyword matching fallback
        try:
            if os.path.exists('agriculture_knowledge.csv'):
                try:
                    self.fallback_data = pd.read_csv('agriculture_knowledge.csv')
                except Exception as e:
                    print(f"Chatbot: CSV Read Error: {e}. Using minimal hardcoded fallback.")
                    raise # Trigger the outer except block
            else:
                 # Minimal fallback if even CSV is missing
                self.fallback_data = pd.DataFrame([
                    {'Question': 'tomato leaf', 'Answer': 'Yellow leaves usually mean nitrogen deficiency.'},
                    {'Question': 'water', 'Answer': 'Most crops need consistent irrigation.'},
                    {'Question': 'price', 'Answer': 'Check market trends in the dashboard.'}
                ])
        except:
             self.fallback_data = pd.DataFrame([
                    {'Question': 'tomato leaf', 'Answer': 'Yellow leaves usually mean nitrogen deficiency.'},
                    {'Question': 'water', 'Answer': 'Most crops need consistent irrigation.'},
                    {'Question': 'price', 'Answer': 'Check market trends in the dashboard.'}
                ])

    def get_response(self, user_query):
        # 1. ML Retrieval Mode
        if self.model and self.index and self.metadata:
            try:
                # Encode Query
                query_vector = self.model.encode([user_query])
                
                # Search
                k = 1 # Top 1 result
                distances, indices = self.index.search(query_vector, k)
                
                idx = indices[0][0]
                distance = distances[0][0]
                
                # Threshold check (if distance is too high, answer might be irrelevant)
                # Lower L2 distance = better match.
                if distance < 1.5: # Tune this threshold
                    answer = self.metadata['answers'][idx]
                    return answer
                else:
                    return "I'm not sure about that. Can you ask in a valid farming context?"
                    
            except Exception as e:
                print(f"Inference Error: {e}")
                return self.keyword_search(user_query)
        
        # 2. Keyword Fallback Mode
        return self.keyword_search(user_query)

    def keyword_search(self, query):
        if self.fallback_data is None:
            return "Knowledge base unavailable."
            
        query = query.lower()
        best_match = None
        max_hits = 0
        
        for _, row in self.fallback_data.iterrows():
            q_text = str(row['Question']).lower()
            a_text = str(row['Answer'])
            
            # Count word overlaps
            hits = sum(1 for word in query.split() if word in q_text)
            
            if hits > max_hits:
                max_hits = hits
                best_match = a_text
        
        if best_match and max_hits > 0:
            return best_match
        else:
            return "I don't have information on that yet. Try asking about crops, diseases, or fertilizers."

# Singleton instance
chatbot = ChatbotEngine()
