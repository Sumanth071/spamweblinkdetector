# Phidexion 🛡️
### An AI-Based Framework for Phishing Website Detection Using Machine Learning and Feature Selection

> **Safer Browsing. Stronger Security.** &bull; *Detect &middot; Prevent &middot; Protect*

---

## 📌 Abstract

Phishing websites pose a serious cybersecurity threat by impersonating legitimate banking, shopping, and login platforms to steal sensitive information such as usernames, passwords, and financial credentials. Traditional detection methods, including blacklists and signature-based techniques, are mainly reactive and often fail to detect newly created or previously unseen phishing websites. 

This project proposes **Phidexion**, an AI-based phishing detection framework that uses machine learning to distinguish phishing websites from legitimate websites. The system uses a labeled dataset of URLs containing structural, domain-based, and content-based features such as URL length, domain activation time, SSL/TLS certificate validity, and mail server presence. To improve efficiency and reduce computational overhead, **Permutation Importance** is applied to identify the most influential features. The selected features are then used to train and evaluate supervised machine learning models, including **Random Forest** and **XGBoost**. Model performance is assessed using Accuracy, Precision, Recall, False Positive Rate (FPR), True Positive Rate (TPR), and an **Anti-Phishing Score** to measure detection effectiveness and reliability. The best-performing model is deployed through a modern web application that allows users to enter a URL and receive an instant prediction indicating whether the website is phishing or legitimate, along with a confidence score.

---

## 🏗️ System Architecture & Folder Layout

The project follows a clean, decoupled architecture:

```text
Web_Detector/
├── backend/                          # Python ML Backend & Flask REST API
│   ├── dataset/
│   │   ├── generate_dataset.py       # Dataset generator & preprocessor
│   │   └── phishing_dataset.csv      # Labeled dataset (6,000 samples)
│   ├── models/
│   │   ├── best_model.pkl            # Production XGBoost Classifier
│   │   ├── phishing_model.pkl        # XGBoost Classifier artifact
│   │   ├── rf_model.pkl              # Random Forest Classifier artifact
│   │   ├── selected_features.pkl     # Top features post-Permutation Importance
│   │   ├── model_metrics.json        # Evaluation metrics benchmark
│   │   └── permutation_importance.json # Permutation importance rankings
│   ├── feature_extraction.py         # Multi-tier real-time URL feature extractor
│   ├── feature_selection.py          # Permutation Feature Importance calculation
│   ├── train_model.py                # Model training, tuning, and evaluation
│   ├── evaluate_model.py             # Confusion matrices and ROC curves
│   ├── requirements.txt              # Backend dependencies
│   └── app.py                        # Flask API server & static host (Port 5000)
├── frontend/                         # Modern React + Vite Web Application
│   ├── src/
│   │   ├── App.jsx                   # All 6 UI screens & interactive scanner
│   │   ├── index.css                 # Cybersecurity theme stylesheet
│   │   └── main.jsx                  # React application entry point
│   ├── dist/                         # Compiled production bundle
│   ├── package.json                  # Frontend dependencies
│   └── vite.config.js                # Vite config & API proxy (Port 3000)
├── run.bat                           # One-click launch script
├── requirements.txt                  # Root Python requirements
└── README.md                         # Project documentation
```

---

## 🖥️ The Six Main UI Screens

1. **Screen 1 — Home / URL Scanner**:
   - Hero banner with cybersecurity shield logo and real-time input bar.
   - 4 Security Feature Cards: *AI Powered Detection*, *Machine Learning (RF & XGBoost)*, *Real-time Analysis*, *Protects Your Data & Identity*.
   - Quick sample pills for instant demonstration (*Bank of America*, *secure-login-update.com*).
2. **Screen 2 — Detection Result (Phishing)**:
   - High-visibility crimson warning badge (`Malicious`).
   - Confidence score gauge (e.g., `92.4%`).
   - Key Details Table (*URL Length: 42 characters*, *Domain Age: 5 days*, *SSL Certificate: Invalid*, *Mail Server: Present*).
   - Advisory banner: *"This website may be trying to steal your personal information. Do not enter any sensitive data."*
3. **Screen 3 — Detection Result (Legitimate)**:
   - Emerald safety badge (`Safe`).
   - Confidence score gauge (e.g., `96.8%`).
   - Key Details Table (*URL Length: 29 characters*, *Domain Age: 15 years*, *SSL Certificate: Valid*, *Mail Server: Not Present*).
   - Confirmation banner: *"This website appears to be legitimate and safe."*
4. **Screen 4 — Feature Importance (Permutation Importance)**:
   - Ranking horizontal progress bars showing influential feature contributions.
   - Domain Age (`0.22`), SSL Validity (`0.18`), URL Length (`0.15`), Mail Server (`0.12`), Subdomain Count (`0.09`), Special Characters (`0.07`), IP Address (`0.06`), Others (`0.11`).
5. **Screen 5 — Model Performance Comparison**:
   - Side-by-side performance comparison of Random Forest vs XGBoost.
   - Verification alert: *"XGBoost achieved the best overall performance and is deployed in the application."*
   - Detailed mathematical formulation of the Anti-Phishing Score.
6. **Screen 6 — About / Project Information**:
   - Project abstract, four architectural pillars, and 7-phase development roadmap.

---

## 📊 Model Performance Comparison

| Metric | Random Forest | XGBoost (Deployed) |
| :--- | :---: | :---: |
| **Accuracy** | 96.2% | **97.8%** |
| **Precision** | 95.6% | **97.3%** |
| **Recall / TPR** | 95.1% | **97.0%** |
| **False Positive Rate (FPR)** | 3.8% | **2.4%** |
| **True Positive Rate (TPR)** | 95.1% | **97.0%** |
| **Anti-Phishing Score (APS)** | 92.7% | **96.5%** |

### Mathematical Definition of Anti-Phishing Score (APS):
$$\text{APS} = \frac{2 \cdot \text{TPR} \cdot (1 - \text{FPR})}{\text{TPR} + (1 - \text{FPR})}$$

---

## 🚀 Quick Start & Installation

### Option 1: One-Click Run (Windows)
Double-click `run.bat` in the project root directory.

### Option 2: Manual Terminal Execution

#### 1. Backend Setup & Startup
```powershell
# Navigate to project root and activate virtual environment
.\.venv\Scripts\activate

# Install requirements
pip install -r backend/requirements.txt

# (Optional) Re-train models or calculate permutation importance
python backend/train_model.py
python backend/feature_selection.py

# Launch Flask Server (Port 5000)
python backend/app.py
```

#### 2. Frontend Development Server (Optional)
```powershell
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) for hot-reloading dev, or [http://localhost:5000](http://localhost:5000) for the full-stack server.

---

## 🔌 REST API Endpoints

- `GET /api/health` — Checks model status and server health.
- `POST /api/scan` — Submits a URL and returns phishing verdict, confidence, and extracted features.
- `GET /api/features` — Returns permutation importance feature ranking.
- `GET /api/metrics` — Returns comparative evaluation metrics between Random Forest and XGBoost.
- `GET /api/history` — Returns recent URL scan logs.
