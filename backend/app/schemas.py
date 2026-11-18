"""
schemas.py
----------
Pydantic models defining the request/response contracts for the API.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw message content to analyze")
    channel: str = Field(
        default="email",
        description="Source channel of the message",
        pattern="^(email|sms|upi)$",
    )


class RedFlags(BaseModel):
    has_url: bool
    has_money_mention: bool
    urgency_keywords: int
    sensitive_data_requests: int
    reward_bait_keywords: int
    excessive_punctuation: bool


class PredictResponse(BaseModel):
    text: str
    channel: str
    is_scam: bool
    risk_level: str  # "Low", "Medium", "High"
    scam_probability: float
    legit_probability: float
    red_flags: RedFlags
    explanation: str


class HistoryItem(BaseModel):
    id: int
    text: str
    channel: str
    is_scam: bool
    risk_level: str
    scam_probability: float
    timestamp: str


class StatsResponse(BaseModel):
    total_scanned: int
    total_scams_detected: int
    total_legit: int
    scam_rate: float
    by_channel: dict
    by_risk_level: dict
    recent_history: List[HistoryItem]


class HealthResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    status: str
    model_loaded: bool
    model_name: Optional[str] = None
