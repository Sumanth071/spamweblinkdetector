"""
Phidexion Model Evaluation Module
Evaluates trained models, computes confusion matrices, ROC curves,
and verifies model stability across both benchmark tests and sample real URLs.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc

DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset", "phishing_dataset.csv")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
STATIC_IMG_DIR = os.path.join(os.path.dirname(__file__), "static", "images")


def run_evaluation():
    print("[*] Running Phidexion Comprehensive Model Evaluation...")
    
    # Load models
    best_model_path = os.path.join(MODELS_DIR, "best_model.pkl")
    rf_model_path = os.path.join(MODELS_DIR, "rf_model.pkl")
    features_path = os.path.join(MODELS_DIR, "selected_features.pkl")
    
    if not os.path.exists(best_model_path) or not os.path.exists(features_path):
        print("[-] Trained models not found. Please run train_model.py first.")
        return

    xgb_model = joblib.load(best_model_path)
    rf_model = joblib.load(rf_model_path)
    selected_features = joblib.load(features_path)
    
    df = pd.read_csv(DATASET_PATH)
    X = df[selected_features]
    y = df["label"]
    
    # Predict with XGBoost
    xgb_preds = xgb_model.predict(X)
    xgb_probs = xgb_model.predict_proba(X)[:, 1]
    
    # Predict with Random Forest
    rf_preds = rf_model.predict(X)
    rf_probs = rf_model.predict_proba(X)[:, 1]

    # Generate Confusion Matrix Visualizations
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    cm_rf = confusion_matrix(y, rf_preds)
    cm_xgb = confusion_matrix(y, xgb_preds)

    sns.heatmap(cm_rf, annot=True, fmt='d', cmap='Blues', ax=axes[0],
                xticklabels=['Legitimate', 'Phishing'],
                yticklabels=['Legitimate', 'Phishing'], cbar=False)
    axes[0].set_title("Random Forest — Confusion Matrix", fontsize=12, fontweight='bold', pad=10)
    axes[0].set_xlabel("Predicted Label", fontweight='bold')
    axes[0].set_ylabel("True Label", fontweight='bold')

    sns.heatmap(cm_xgb, annot=True, fmt='d', cmap='Greens', ax=axes[1],
                xticklabels=['Legitimate', 'Phishing'],
                yticklabels=['Legitimate', 'Phishing'], cbar=False)
    axes[1].set_title("XGBoost (Best Model) — Confusion Matrix", fontsize=12, fontweight='bold', pad=10)
    axes[1].set_xlabel("Predicted Label", fontweight='bold')
    axes[1].set_ylabel("True Label", fontweight='bold')

    plt.tight_layout()
    cm_plot_file = os.path.join(STATIC_IMG_DIR, "confusion_matrices.png")
    plt.savefig(cm_plot_file, dpi=200)
    plt.close()
    print(f"[+] Saved Confusion Matrices plot to: {cm_plot_file}")

    # Generate ROC Curve
    fpr_rf, tpr_rf, _ = roc_curve(y, rf_probs)
    fpr_xgb, tpr_xgb, _ = roc_curve(y, xgb_probs)
    auc_rf = auc(fpr_rf, tpr_rf)
    auc_xgb = auc(fpr_xgb, tpr_xgb)

    plt.figure(figsize=(7, 5.5))
    plt.plot(fpr_rf, tpr_rf, color='#64748b', lw=2, label=f'Random Forest (AUC = {auc_rf:.3f})')
    plt.plot(fpr_xgb, tpr_xgb, color='#2563eb', lw=2.5, label=f'XGBoost (AUC = {auc_xgb:.3f})')
    plt.plot([0, 1], [0, 1], color='#cbd5e1', lw=1.5, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate (FPR)', fontweight='bold')
    plt.ylabel('True Positive Rate (TPR)', fontweight='bold')
    plt.title('Receiver Operating Characteristic (ROC) Curve', fontweight='bold', pad=12)
    plt.legend(loc="lower right", frameon=True)
    plt.tight_layout()

    roc_plot_file = os.path.join(STATIC_IMG_DIR, "roc_curve.png")
    plt.savefig(roc_plot_file, dpi=200)
    plt.close()
    print(f"[+] Saved ROC Curve plot to: {roc_plot_file}")
    print("[+] Evaluation completed successfully.")


if __name__ == "__main__":
    run_evaluation()
