@echo off
title Phidexion - AI Phishing Website Detector
echo ========================================================
echo       PHIDEXION: AI-BASED PHISHING WEBSITE DETECTOR
echo ========================================================
echo [1/2] Activating Python Virtual Environment...
call .venv\Scripts\activate.bat

echo [2/2] Launching Backend ML Service & Web Interface on http://localhost:5000 ...
start http://localhost:5000
python backend\app.py

pause
