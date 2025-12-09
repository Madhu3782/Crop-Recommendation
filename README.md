# Crop Price Prediction System 🌾

A full-stack application to predict crop prices using Machine Learning (Linear Regression) and a React frontend.

## 📂 Project Structure

```
d:/project/frontend/
├── backend/
│   ├── app.py                 # Flask API
│   ├── data_generation.py     # Synthetic data generator
│   ├── model_training.py      # ML Model training script
│   ├── problem_statement.md   # Project Objectives & Use Cases
│   ├── crop_prices.csv        # Generated dataset
│   └── model.pkl              # Trained model
├── src/
│   ├── components/
│   │   ├── Navbar.jsx         # Navigation bar
│   │   └── Navbar.css
│   ├── pages/
│   │   ├── Login.jsx          # Login Page
│   │   ├── Register.jsx       # Register Page
│   │   ├── Dashboard.jsx      # Main Prediction Dashboard
│   │   └── Dashboard.css
│   ├── App.js                 # Routing
│   └── App.css
├── package.json
└── README.md
```

## 🚀 Setup & Run Instructions

### Prerequisites
- Node.js & npm installed
- Python 3.x installed

### 1. Backend Setup (Python)

Navigate to the backend folder:
```bash
cd backend
```

Install dependencies:
```bash
pip install flask flask-cors pandas scikit-learn
```
*(Note: If you are on Windows and have multiple python versions, you might need to use `py -m pip install ...`)*

Generate Data & Train Model:
```bash
python data_generation.py
python model_training.py
```
*(This will create `crop_prices.csv` and `model.pkl`)*

Start the API Server:
```bash
python app.py
```
The server will start at `http://localhost:5000`.

### 2. Frontend Setup (React)

Open a new terminal and navigate to the project root:
```bash
cd d:/project/frontend
```

Install dependencies:
```bash
npm install axios recharts react-router-dom
```

Start the React App:
```bash
npm start
```
The application will open at `http://localhost:3000`.

## 🌟 Features
- **User Authentication:** Simple Login/Register flow.
- **Price Prediction:** Input crop details (Region, Season, Weather) to get predicted prices.
- **Interactive Graphs:** Visual trend analysis using Recharts.
- **Suggestions:** Basic logic to suggest selling decisions based on price.

## 🤖 Tech Stack
- **Frontend:** React, Recharts, Axios, CSS
- **Backend:** Flask, Python
- **ML:** Scikit-Learn, Pandas
