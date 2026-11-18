"""
model.py
--------
Loads the trained TF-IDF vectorizer, scaler, and classifier, and exposes a
single `predict(text, channel)` function used by the API layer.
"""

import json
import os

import joblib
import numpy as np
from scipy.sparse import hstack

from .utils import extract_handcrafted_features, handcrafted_vector

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACT_DIR = os.path.join(BASE_DIR, "model_artifacts")

_vectorizer = None
_scaler = None
_classifier = None
_model_name = None


def load_model():
    """Load model artifacts into memory. Called once at API startup."""
    global _vectorizer, _scaler, _classifier, _model_name

    vec_path = os.path.join(ARTIFACT_DIR, "tfidf_vectorizer.joblib")
    scaler_path = os.path.join(ARTIFACT_DIR, "scaler.joblib")
    clf_path = os.path.join(ARTIFACT_DIR, "scam_classifier.joblib")
    metrics_path = os.path.join(ARTIFACT_DIR, "metrics.json")

    if not (os.path.exists(vec_path) and os.path.exists(clf_path)):
        raise FileNotFoundError(
            "Model artifacts not found. From the backend/ directory run:\n"
            "  python data/generate_dataset.py\n"
            "  python train_model.py\n"
            "before starting the API."
        )

    _vectorizer = joblib.load(vec_path)
    _scaler = joblib.load(scaler_path)
    _classifier = joblib.load(clf_path)

    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            _model_name = json.load(f).get("best_model", "unknown")
    else:
        _model_name = type(_classifier).__name__

    return _model_name


def is_loaded() -> bool:
    return _classifier is not None


def get_model_name():
    return _model_name


def _risk_level(prob: float) -> str:
    if prob >= 0.70:
        return "High"
    if prob >= 0.35:
        return "Medium"
    return "Low"


def _build_explanation(flags: dict, prob: float, channel: str) -> str:
    reasons = []
    if flags["has_url"]:
        reasons.append("contains a suspicious link")
    if flags["sensitive_count"] > 0:
        reasons.append("asks for sensitive information (OTP/PIN/KYC/card details)")
    if flags["urgency_count"] >= 2:
        reasons.append("uses urgency/pressure language")
    if flags["reward_count"] >= 1:
        reasons.append("promises a reward, refund, or cashback")
    if flags["has_money"]:
        reasons.append("references a specific money amount")
    if flags["exclamations"] >= 2:
        reasons.append("uses excessive punctuation")

    if not reasons:
        return "No strong scam indicators were found in this message."

    joined = ", ".join(reasons)
    if prob >= 0.70:
        prefix = f"This {channel} message is very likely a scam because it {joined}."
    elif prob >= 0.35:
        prefix = f"This {channel} message shows some scam indicators: it {joined}."
    else:
        prefix = f"This {channel} message has minor red flags ({joined}) but is likely legitimate."
    return prefix


def predict(text: str, channel: str = "email") -> dict:
    if not is_loaded():
        raise RuntimeError("Model not loaded. Call load_model() first.")

    tfidf_vec = _vectorizer.transform([text])
    hc_vec = np.array([handcrafted_vector(text)])
    hc_vec_scaled = _scaler.transform(hc_vec)
    combined = hstack([tfidf_vec, hc_vec_scaled])

    proba = _classifier.predict_proba(combined)[0]
    # class order follows classifier.classes_, typically [0, 1]
    classes = list(_classifier.classes_)
    scam_idx = classes.index(1)
    legit_idx = classes.index(0)

    scam_prob = float(proba[scam_idx])
    legit_prob = float(proba[legit_idx])

    flags = extract_handcrafted_features(text)
    risk = _risk_level(scam_prob)
    explanation = _build_explanation(flags, scam_prob, channel)

    return {
        "text": text,
        "channel": channel,
        "is_scam": bool(scam_prob >= 0.5),
        "risk_level": risk,
        "scam_probability": round(scam_prob, 4),
        "legit_probability": round(legit_prob, 4),
        "red_flags": {
            "has_url": bool(flags["has_url"]),
            "has_money_mention": bool(flags["has_money"]),
            "urgency_keywords": flags["urgency_count"],
            "sensitive_data_requests": flags["sensitive_count"],
            "reward_bait_keywords": flags["reward_count"],
            "excessive_punctuation": flags["exclamations"] >= 2,
        },
        "explanation": explanation,
    }
