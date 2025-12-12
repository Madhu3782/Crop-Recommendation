import os
import pickle
import pandas as pd
import numpy as np
import traceback
from dotenv import load_dotenv

# Load env variables (API Key)
load_dotenv()

# --- 1. Import Libraries ---
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    ML_AVAILABLE = True
except Exception as e:
    ML_AVAILABLE = False
    print(f"Brain: Vector Search Libs missing ({e}).")

try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        nlp = None
        print("Brain: spacy model 'en_core_web_sm' not found. Using basic fallback.")
except Exception as e:
    nlp = None
    print(f"Brain: Spacy missing. Basic fallback active.")

# --- 2. OpenAI / Groq Configuration ---
try:
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key.startswith("gsk_"):
        # Groq Configuration
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        print("Brain: Detected Groq API Key. Switched to Groq Endpoint.")
        # Groq supported models: llama3-8b-8192, mixtral-8x7b-32768, etc.
        # "llama-3.1-8b-instant" is often safe, or "llama3-70b-8192"
        MODEL_NAME = "llama-3.1-8b-instant" 
    else:
        # Standard OpenAI Configuration
        client = OpenAI(api_key=api_key)
        MODEL_NAME = "gpt-4o-mini"
        
    OPENAI_AVAILABLE = True
except Exception as e:
    OPENAI_AVAILABLE = False
    print(f"Brain: OpenAI Client init failed: {e}")
    MODEL_NAME = "gpt-4o-mini" # Fallback default

class ChatbotBrain:
    def __init__(self):
        self.intent_model = None
        self.vector_model = None
        self.index = None
        self.metadata = None
        
        # Load resources
        self.load_resources()

    def load_resources(self):
        print("Brain: Initializing Pro Pipeline (ChatGPT/Groq + RAG)...")
        
        # A. Intent Model
        try:
            with open('intent_model.pkl', 'rb') as f:
                self.intent_model = pickle.load(f)
            print("Brain: Intent model loaded.")
        except:
            print("Brain: Intent model missing.")

        # B. Vector Index (RAG)
        if ML_AVAILABLE:
            try:
                self.vector_model = SentenceTransformer('all-MiniLM-L6-v2')
                if os.path.exists('chatbot_index.faiss'):
                    self.index = faiss.read_index('chatbot_index.faiss')
                    with open('chatbot_metadata.pkl', 'rb') as f:
                        self.metadata = pickle.load(f)
                    print("Brain: FAISS Index & Metadata loaded (Unified).")
                else:
                    print("Brain: FAISS Index not found. Run build_chatbot_index.py")
            except Exception as e:
                print(f"Brain: Vector init failed: {e}")

    def detect_intent(self, query):
        if self.intent_model:
            try:
                return self.intent_model.predict([query])[0]
            except:
                pass
        return "general"

    def extract_entities(self, query):
        entities = {}
        if nlp:
            doc = nlp(query)
            for ent in doc.ents:
                entities[ent.label_] = ent.text
            
            # Custom Rule-based
            crops = ['wheat', 'rice', 'tomato', 'potato', 'cotton', 'maize', 'sugarcane', 'onion', 'brinjal', 'soybean', 'mustard']
            found_crops = [word for word in query.lower().split() if word in crops]
            if found_crops:
                entities['CROP'] = found_crops[0]
                
        return entities

    def retrieve_context(self, query, top_k=3):
        if not self.index or not self.vector_model or not self.metadata:
            return []

        try:
            # Encode Query
            query_vec = self.vector_model.encode([query])
            
            # Search
            D, I = self.index.search(np.array(query_vec).astype('float32'), top_k)
            
            results = []
            for i in range(top_k):
                idx = I[0][i]
                if idx < len(self.metadata['answers']):
                    ans = self.metadata['answers'][idx]
                    q_matched = self.metadata['questions'][idx]
                    cat = self.metadata['topics'][idx]
                    # Format: [Category] Q: ... A: ...
                    results.append(f"[{cat}] Q: {q_matched} | A: {ans}")
                    
            return results
        except Exception as e:
            print(f"Brain: Retrieval Error: {e}")
            return []

    def ask_chatgpt(self, query, context_list, intent, entities, ml_insights=None):
        if not OPENAI_AVAILABLE or not client.api_key:
            return "Brain: OpenAI API Key missing or library not installed."

        # Construct System Prompt
        system_prompt = (
            "You are an advanced Agriculture Expert AI assisting farmers. "
            "Your goal is to provide accurate, practical, and farmer-friendly advice.\n"
            "Rules:\n"
            "1. Use the provided Context and ML Insights to answer.\n"
            "2. If the context has the answer, paraphrase it clearly.\n"
            "3. If ML Insights (Price/Pest/Crop) are provided, interpret them for the farmer.\n"
            "4. If uncertainty exists, ask clarifying questions. DO NOT Hallucinate.\n"
            "5. Format output with clear sections (Diagnosis, Action, Dosage, Warning) if applicable.\n"
            "6. Keep tone helpful and encouraging."
        )

        # Construct User Content
        context_text = "\n".join(context_list) if context_list else "No knowledge base context found."
        
        ml_text = ""
        if ml_insights:
            ml_text = "ML Model Predictions:\n"
            for k, v in ml_insights.items():
                ml_text += f"- {k}: {v}\n"
        
        user_prompt = (
            f"User Query: {query}\n\n"
            f"Detected Intent: {intent}\n"
            f"Entities: {entities}\n\n"
            f"--- Knowledge Base Context ---\n{context_text}\n\n"
            f"--- Real-time Data ---\n{ml_text}\n\n"
            "Please provide a detailed response:"
        )

        # Debug Print
        print("\n--- CHATGPT PROMPT DEBUG ---")
        try:
            print(f"System: {system_prompt[:50]}...")
            print(f"User: {user_prompt.encode('ascii', 'ignore').decode('ascii')}")
        except:
            print("User prompt contains special characters (omitted from log).")
        print("----------------------------\n")

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            return response.choices[0].message.content
        except Exception as e:
            # Fallback: Return context directly if API fails
            print(f"Brain: API Error ({e}). Using Fallback.")
            if context_list:
                best_match = context_list[0]
                try:
                    answer_part = best_match.split("| A:")[1].strip()
                    return f"**Fallback (API Unreachable):** {answer_part}"
                except:
                   return f"**Fallback (API Unreachable):** {best_match}"
            else:
                return "I'm having trouble connecting to my brain right now. Please try again later."

    def register_models(self, price_model, crop_model, pest_model, config=None):
        """Receive loaded ML models from app.py"""
        self.ml_models = {
            'price': price_model,
            'crop': crop_model,
            'pest': pest_model
        }
        self.config = config or {}
        print("Brain: ML Models registered.")

    def get_ml_insights(self, query, intent, entities):
        """Generate ML predictions based on query entities"""
        insights = {}
        if not hasattr(self, 'ml_models'):
            return insights

        try:
            # 1. Price Prediction
            if 'price' in intent or 'market' in intent or 'sell' in query.lower():
                crop = entities.get('CROP')
                if crop and self.ml_models['price']:
                    insights['Price Forecast'] = f"Estimated market price for {crop} is currently stable/high (Model access limited without full weather inputs)."
            
            # 2. Pest Prediction
            if 'pest' in intent or 'disease' in intent:
                insights['Pest Risk'] = "Check the 'Pest Risk' tab for real-time risk analysis based on current weather."

        except Exception as e:
            print(f"Brain: ML insight error: {e}")
        
        return insights

    def translate_text(self, text, target_lang):
        """Generic translation helper using Llama-3"""
        if not OPENAI_AVAILABLE or not client.api_key:
            return text 

        # Simplified prompt for query translation vs response translation
        # Detect if it's a short query or long response? 
        # Actually same strict prompt works well for both usually.
        
        prompt = (
            f"Translate the following text into {target_lang}. \n"
            f"Rules:\n"
            f"1. Accurately preserve meaning.\n"
            f"2. Keep it natural.\n"
            f"3. Return ONLY the translation, no intro/outro.\n"
            f"Text:\n{text}"
        )
        
        try:
             response = client.chat.completions.create(
                model=MODEL_NAME, 
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3, 
                max_tokens=1000
            )
             return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Brain: Translation Error to {target_lang} ({e})")
            return text 

    def generate_response(self, query, ml_data=None, language='English'):
        print(f"Brain: Processing '{query}' in {language}...")
        
        english_query = query
        
        # 1. Translate Query to English (if needed) for better RAG/Intent
        if language and language.lower() != 'english':
             print(f"Brain: Translating Input to English...")
             english_query = self.translate_text(query, "English")
             print(f"Brain: English Query: {english_query}")

        # 2. Pipeline (Using English Query)
        intent = self.detect_intent(english_query)
        entities = self.extract_entities(english_query)
        context = self.retrieve_context(english_query)
        
        # 3. Get ML Insights
        internal_ml = self.get_ml_insights(english_query, intent, entities)
        if ml_data:
            internal_ml.update(ml_data)

        # 4. ChatGPT Generation (English)
        answer_en = self.ask_chatgpt(english_query, context, intent, entities, internal_ml)
        
        # 5. Translate Response (if needed)
        answer_translated = answer_en
        if language and language.lower() != 'english':
             print(f"Brain: Translating Response to {language}...")
             answer_translated = self.translate_text(answer_en, language)
        
        # Return structured response
        return {
            "answer_en": answer_en,
            "answer_translated": answer_translated,
            "language": language
        }


# Singleton
brain = ChatbotBrain()
