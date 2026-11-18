"""
train_model.py
---------------
Trains the scam-detection model:
    TF-IDF (word n-grams) + handcrafted red-flag features -> Logistic Regression
      (a RandomForest variant is also trained and the better one on the
      held-out test set is kept)

Run from the backend/ directory:
    python train_model.py

Produces (in model_artifacts/):
    tfidf_vectorizer.joblib
    scaler.joblib
    scam_classifier.joblib
    metrics.json
"""

import json
import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report,
                              f1_score, precision_score, recall_score)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))
from app.utils import clean_text, handcrafted_vector  # noqa: E402

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")
ARTIFACT_DIR = os.path.join(BASE_DIR, "model_artifacts")
os.makedirs(ARTIFACT_DIR, exist_ok=True)


def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"{DATA_PATH} not found. Run `python data/generate_dataset.py` "
            "from the backend/ directory first (or supply your own dataset.csv)."
        )

    df = pd.read_csv(DATA_PATH)
    df["clean_text"] = df["text"].apply(clean_text)

    X_train_text, X_test_text, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )

    # --- TF-IDF features -----------------------------------------------
    vectorizer = TfidfVectorizer(
        preprocessor=clean_text,
        ngram_range=(1, 2),
        max_features=3000,
        min_df=1,
    )
    X_train_tfidf = vectorizer.fit_transform(X_train_text)
    X_test_tfidf = vectorizer.transform(X_test_text)

    # --- Handcrafted features -------------------------------------------
    X_train_hc = np.array([handcrafted_vector(t) for t in X_train_text])
    X_test_hc = np.array([handcrafted_vector(t) for t in X_test_text])

    scaler = StandardScaler()
    X_train_hc_scaled = scaler.fit_transform(X_train_hc)
    X_test_hc_scaled = scaler.transform(X_test_hc)

    # --- Combine ---------------------------------------------------------
    from scipy.sparse import hstack
    X_train = hstack([X_train_tfidf, X_train_hc_scaled])
    X_test = hstack([X_test_tfidf, X_test_hc_scaled])

    candidates = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(
            n_estimators=200, max_depth=12, random_state=42, class_weight="balanced"
        ),
    }

    best_name, best_model, best_f1 = None, None, -1
    metrics_report = {}

    for name, model in candidates.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        f1 = f1_score(y_test, preds)
        metrics_report[name] = {
            "accuracy": accuracy_score(y_test, preds),
            "precision": precision_score(y_test, preds, zero_division=0),
            "recall": recall_score(y_test, preds, zero_division=0),
            "f1_score": f1,
        }
        print(f"\n=== {name} ===")
        print(classification_report(y_test, preds, target_names=["legit", "scam"]))
        if f1 > best_f1:
            best_f1, best_name, best_model = f1, name, model

    print(f"\nBest model: {best_name} (F1={best_f1:.3f})")

    joblib.dump(vectorizer, os.path.join(ARTIFACT_DIR, "tfidf_vectorizer.joblib"))
    joblib.dump(scaler, os.path.join(ARTIFACT_DIR, "scaler.joblib"))
    joblib.dump(best_model, os.path.join(ARTIFACT_DIR, "scam_classifier.joblib"))

    with open(os.path.join(ARTIFACT_DIR, "metrics.json"), "w") as f:
        json.dump({"best_model": best_name, "results": metrics_report}, f, indent=2)

    print(f"\nSaved model artifacts to {ARTIFACT_DIR}/")


if __name__ == "__main__":
    main()
