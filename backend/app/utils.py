"""
utils.py
--------
Text preprocessing and handcrafted feature extraction shared by the
training script and the FastAPI inference service.

Two kinds of signal are combined:
  1. TF-IDF n-gram features over the cleaned message text (captures the
     vocabulary/phrasing typical of scam messages: "verify", "click here",
     "KYC", "blocked", "cashback", etc.)
  2. Handcrafted "red flag" features that are known scam indicators
     (presence of a link, urgency words, money amounts, shortened URLs,
     excessive punctuation/uppercase, requests for OTP/PIN, etc.)
"""

import re
import string

URL_REGEX = re.compile(r"(https?://\S+|www\.\S+|bit\.ly/\S+)", re.IGNORECASE)
MONEY_REGEX = re.compile(r"(rs\.?\s?\d+|₹\s?\d+|\$\d+)", re.IGNORECASE)

URGENCY_WORDS = [
    "urgent", "immediately", "now", "today", "expire", "expiring", "24 hours",
    "final notice", "last warning", "act now", "limited", "hurry", "asap",
    "blocked", "suspended", "deactivat", "locked", "verify", "confirm",
]

SENSITIVE_WORDS = [
    "otp", "pin", "password", "cvv", "kyc", "account number", "upi id",
    "card number", "aadhar", "pan card",
]

REWARD_WORDS = [
    "won", "winner", "lottery", "prize", "cashback", "reward", "free",
    "claim", "refund", "congratulations", "selected",
]


def clean_text(text: str) -> str:
    """Lowercase, strip URLs to a placeholder token, remove extra whitespace."""
    text = text.lower()
    text = URL_REGEX.sub(" __url__ ", text)
    text = MONEY_REGEX.sub(" __money__ ", text)
    text = text.translate(str.maketrans("", "", string.punctuation.replace("_", "")))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_handcrafted_features(raw_text: str) -> dict:
    """Return a dict of numeric red-flag indicators for a raw (unclean) message."""
    text_lower = raw_text.lower()

    has_url = 1 if URL_REGEX.search(raw_text) else 0
    has_money = 1 if MONEY_REGEX.search(raw_text) else 0
    urgency_count = sum(1 for w in URGENCY_WORDS if w in text_lower)
    sensitive_count = sum(1 for w in SENSITIVE_WORDS if w in text_lower)
    reward_count = sum(1 for w in REWARD_WORDS if w in text_lower)

    exclamations = raw_text.count("!")
    uppercase_ratio = (
        sum(1 for c in raw_text if c.isupper()) / max(len(raw_text), 1)
    )
    length = len(raw_text)

    return {
        "has_url": has_url,
        "has_money": has_money,
        "urgency_count": urgency_count,
        "sensitive_count": sensitive_count,
        "reward_count": reward_count,
        "exclamations": exclamations,
        "uppercase_ratio": round(uppercase_ratio, 4),
        "length": length,
    }


HANDCRAFTED_FEATURE_ORDER = [
    "has_url", "has_money", "urgency_count", "sensitive_count",
    "reward_count", "exclamations", "uppercase_ratio", "length",
]


def handcrafted_vector(raw_text: str):
    feats = extract_handcrafted_features(raw_text)
    return [feats[k] for k in HANDCRAFTED_FEATURE_ORDER]
