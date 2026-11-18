"""
main.py
-------
FastAPI application exposing the scam-detection model as a REST API, plus
an in-memory scan history used to power the dashboard's stats/analytics
view.

Run (from backend/ directory):
    uvicorn app.main:app --reload --port 8000

Interactive API docs will be available at http://localhost:8000/docs
"""

from collections import Counter
from datetime import datetime, timezone
from itertools import count
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import model
from .schemas import (HealthResponse, HistoryItem, PredictRequest,
                       PredictResponse, StatsResponse)

app = FastAPI(
    title="AI Scam Detection System",
    description="Detects phishing emails, SMS, and UPI scam messages using ML/NLP.",
    version="1.0.0",
)

# Allow the React dev server (and any origin, for demo purposes) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-memory scan history (swap for a real DB in production) -----------
_history: List[dict] = []
_id_counter = count(1)


@app.on_event("startup")
def _startup():
    model.load_model()


@app.get("/", tags=["Health"])
def root():
    return {"message": "AI Scam Detection API is running. See /docs for usage."}


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health():
    return HealthResponse(
        status="ok",
        model_loaded=model.is_loaded(),
        model_name=model.get_model_name(),
    )


@app.post("/api/predict", response_model=PredictResponse, tags=["Detection"])
def predict_scam(payload: PredictRequest):
    if not model.is_loaded():
        raise HTTPException(status_code=503, detail="Model is not loaded yet.")

    result = model.predict(payload.text, payload.channel)

    _history.append({
        "id": next(_id_counter),
        "text": result["text"],
        "channel": result["channel"],
        "is_scam": result["is_scam"],
        "risk_level": result["risk_level"],
        "scam_probability": result["scam_probability"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    # Cap history size for the demo
    if len(_history) > 500:
        del _history[0]

    return result


@app.get("/api/stats", response_model=StatsResponse, tags=["Dashboard"])
def get_stats():
    total = len(_history)
    scams = sum(1 for h in _history if h["is_scam"])
    legit = total - scams

    by_channel = dict(Counter(h["channel"] for h in _history))
    by_risk = dict(Counter(h["risk_level"] for h in _history))

    recent = list(reversed(_history[-20:]))

    return StatsResponse(
        total_scanned=total,
        total_scams_detected=scams,
        total_legit=legit,
        scam_rate=round(scams / total, 4) if total else 0.0,
        by_channel=by_channel,
        by_risk_level=by_risk,
        recent_history=[HistoryItem(**h) for h in recent],
    )


@app.delete("/api/history", tags=["Dashboard"])
def clear_history():
    _history.clear()
    return {"message": "History cleared."}
