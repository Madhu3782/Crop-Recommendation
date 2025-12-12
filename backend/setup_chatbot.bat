@echo off
echo ==========================================
echo    Farmer Chatbot Pro - Setup Script
echo ==========================================
echo.
echo Installing dependencies...
pip install spacy transformers torch sentence-transformers faiss-cpu scikit-learn pandas sentencepiece
if %errorlevel% neq 0 (
    echo Error installing pip libraries. Please check your python installation.
    pause
    exit /b
)

echo.
echo Downloading Spacy English Model...
python -m spacy download en_core_web_sm
if %errorlevel% neq 0 (
    echo Error downloading Spacy model.
    pause
    exit /b
)

echo.
echo Training Intent Model...
python train_intent_model.py
if %errorlevel% neq 0 (
    echo Error training intent model.
    pause
    exit /b
)

echo.
echo Building Knowledge Index...
python build_chatbot_index.py

echo.
echo ==========================================
echo    Setup Complete! You can now run:
echo    python app.py
echo ==========================================
pause
