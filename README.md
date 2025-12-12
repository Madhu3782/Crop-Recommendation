# AI-Powered Smart Agriculture Assistant 🌾

A comprehensive full-stack application empowering farmers with AI-driven insights, including Crop Price Prediction, Pest Disease Risk Analysis, Automated Crop Recommendations, and a Multilingual Smart Chatbot.

## 📂 Project Structure

```
d:/project/frontend/
├── backend/
│   ├── app.py                 # Main Flask API
│   ├── chatbot_brain.py       # AI Chatbot Logic (RAG + LLM)
│   ├── chatbot_engine.py      # Chatbot Core Engine
│   ├── train_pest_model.py    # Pest Risk Model Training
│   ├── train_crop_model.py    # Crop Recommendation Model Training
│   ├── build_chatbot_index.py # FAISS Index Builder
│   ├── alerts_db.py           # Alert System Database Management
│   ├── pest_dataset.csv       # Synthetic Pest Data
│   ├── crop_prices.csv        # Market Price Data
│   └── models/                # Saved PKL models (model.pkl, pest_model.pkl, etc.)
├── src/
│   ├── components/
│   │   ├── Navbar.jsx         # Navigation
│   ├── pages/
│   │   ├── Dashboard.jsx      # Price Prediction Dashboard
│   │   ├── Chatbot.jsx        # AI Assistant Interface
│   │   ├── PestAlert.jsx      # Pest Risk Analysis
│   │   ├── Recommend.jsx      # Crop Suitability Recommender
│   │   ├── Analytics.jsx      # Market Trend Analytics
│   │   ├── Alerts.jsx         # Price Alert Configuration
│   │   ├── Login.jsx / Register.jsx
│   ├── App.js                 # Routing & Layout
│   └── index.css              # Global Enriched Styles
├── package.json
└── README.md
```

## 🌟 Key Features

### 1. 🤖 Pro AI Chatbot
- **RAG-Powered:** Uses FAISS and Sentence-Transformers to retrieve accurate agricultural knowledge.
- **Multilingual Support:** Auto-translates queries and responses (e.g., Hindi <-> English) to assist farmers in their native language.
- **Intent Detection:** Smartly routes queries (Price, Pest, General Advice).
- **LLM Integration:** Connects with OpenAI (GPT-4o) or Groq (Llama-3) for natural conversations.

### 2. 🐛 Pest & Disease Risk Alert
- **Real-time Risk Analysis:** Calculates pest outbreak probability based on current temperature, humidity, and rainfall.
- **Machine Learning:** Uses a Random Forest Regressor trained on regional weather patterns.

### 3. 🌱 Smart Crop Recommendation
- **Suitability Engine:** Suggests the best crops to grow based on soil type (N, P, K, pH) and climatic conditions.
- **Ranked Results:** Prioritizes crops by potential market value/suitability.

### 4. 📈 Market Analytics & Prediction
- **Price Forecasting:** Predicts future crop prices using Linear Regression.
- **Visual Analytics:** Interactive charts for price trends and historical data comparison.

### 5. 🔔 Alert System
- **Custom Thresholds:** Farmers can set price alerts (e.g., "Notify me if Wheat > ₹2500").
- **Notifications:** Dashboard alerts when criteria are met.

## 🚀 Setup & Run Instructions

### Prerequisites
- Node.js & npm
- Python 3.8+
- OpenAI API Key (or Groq Key) for Chatbot

### 1. Backend Setup (Python)

Navigate to the backend:
```bash
cd backend
```

Install Dependencies:
```bash
pip install flask flask-cors pandas scikit-learn numpy
pip install sentence-transformers faiss-cpu spacy python-dotenv openai
```

Install Language Model for NLP:
```bash
python -m spacy download en_core_web_sm
```

**Configuration:**
Create a `.env` file in the `backend/` folder and add your API key:
```env
OPENAI_API_KEY=your_key_here
# OR
# OPENAI_API_KEY=gsk_... (for Groq)
```

**Initialize Models & Database:**
Run the training and setup scripts to generate necessary artifacts (`.pkl` and `.faiss` files):
```bash
# 1. Generate Synthetic Data (if missing)
python data_generation.py

# 2. Train Prediction Models
python model_training.py
python train_pest_model.py
python train_crop_model.py

# 3. Build Chatbot Knowledge Base
python build_chatbot_index.py
```

Start the API Server:
```bash
python app.py
```
*Server runs at `http://localhost:5000`*

### 2. Frontend Setup (React)

Open a new terminal in the project root (`d:/project/frontend`):

```bash
npm install
# Ensure you have new packages if added
npm install axios recharts react-router-dom lucide-react
```

Start the App:
```bash
npm start
```
*App opens at `http://localhost:3000`*

## 🤖 Tech Stack

| Component | Technologies |
|-----------|--------------|
| **Frontend** | React.js, Tailwind/CSS, Recharts, Lucide Icons, Axios |
| **Backend** | Flask (Python), REST API |
| **AI/ML** | Scikit-Learn (RandomForest, LinearReg), Pandas, NumPy |
| **NLP & LLM** | Sentence-Transformers, FAISS (Vector DB), SpaCy, OpenAI/Groq API |
| **Database** | SQLite (for Alerts), CSV (Datasets) |
