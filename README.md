# AI Scam Detection System

An AI-powered system that detects phishing emails, SMS, and UPI scam messages
using Machine Learning and NLP, exposed through a REST API and visualized in
a real-time threat-analysis dashboard.

**Tech stack:** Python · Scikit-learn · Pandas · FastAPI · React.js

---

## 1. What this project does

- Classifies a message (email, SMS, or UPI payment notification) as **scam**
  or **legitimate**, with a probability score and risk level (Low / Medium /
  High).
- Combines **TF-IDF text features** with **handcrafted red-flag features**
  (suspicious links, urgency language, requests for OTP/PIN/KYC, reward/
  cashback bait, money amounts, excessive punctuation) feeding a Logistic
  Regression / Random Forest classifier — whichever scores better on the
  held-out test set is used automatically.
- Serves predictions through a **FastAPI REST API** (`/api/predict`,
  `/api/stats`, `/api/health`).
- A **React dashboard** lets you paste a message, see the verdict with an
  explanation and a live risk gauge, and tracks aggregate analytics (scam
  rate, breakdown by channel and risk level, recent scan history).

## 2. Project structure

```
scam-detection-system/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app & REST endpoints
│   │   ├── model.py         # Model loading + inference logic
│   │   ├── schemas.py       # Pydantic request/response models
│   │   └── utils.py         # Text cleaning + red-flag feature extraction
│   ├── data/
│   │   ├── generate_dataset.py   # Builds the synthetic labeled dataset
│   │   └── dataset.csv           # Training data (email/sms/upi, scam/legit)
│   ├── model_artifacts/     # Saved TF-IDF vectorizer, scaler, classifier
│   ├── train_model.py       # Trains and saves the model
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ScanForm.jsx     # Message input + channel selector
    │   │   ├── ResultCard.jsx   # Verdict, red flags, explanation
    │   │   ├── RiskGauge.jsx    # Animated arc gauge for scam probability
    │   │   └── StatsPanel.jsx   # Charts + recent scan history
    │   ├── api.js            # Fetch wrapper around the backend API
    │   ├── App.jsx
    │   └── index.css
    ├── package.json
    └── vite.config.js
```

## 3. How it works (for your resume / viva explanation)

1. **Dataset** — `generate_dataset.py` builds a labeled dataset of scam and
   legitimate messages across three channels using realistic templates
   (phishing links, fake KYC alerts, lottery scams, UPI collect-request
   fraud, etc., alongside normal transactional/personal messages). Swap this
   for a real dataset (e.g. Kaggle SMS Spam Collection, PhishTank) if you
   want to extend the project.
2. **Feature engineering** (`app/utils.py`) — each message is cleaned
   (lowercased, URLs/amounts normalized) and turned into TF-IDF n-gram
   features, plus 8 handcrafted numeric red-flag features.
3. **Training** (`train_model.py`) — trains Logistic Regression and Random
   Forest on the combined feature set, evaluates both with
   precision/recall/F1 on a held-out test split, and saves whichever
   performs better.
4. **Serving** (`app/main.py`) — FastAPI loads the saved model once at
   startup and exposes `/api/predict` for real-time scoring, plus
   `/api/stats` for the dashboard's analytics (kept in an in-memory list for
   this demo — swap for a real database for production use).
5. **Dashboard** (`frontend/`) — a React + Vite single-page app that calls
   the API, shows the verdict with a risk gauge and plain-English
   explanation of *why* a message was flagged, and visualizes aggregate
   stats with `recharts`.

## 4. Running the project

### Prerequisites
- Python 3.9+
- Node.js 18+ and npm

### Step 1 — Backend (FastAPI + ML model)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

# (Re)generate the dataset and (re)train the model — artifacts are already
# included in model_artifacts/, so this step is optional unless you want to
# retrain or modify the dataset.
python data/generate_dataset.py
python train_model.py

# Start the API
uvicorn app.main:app --reload --port 8000
```

The API is now running at `http://localhost:8000`. Interactive Swagger docs
are available at `http://localhost:8000/docs` — useful for demoing the
project without the frontend.

### Step 2 — Frontend (React dashboard)

In a **new terminal**:

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (typically `http://localhost:5173`). The dashboard
will show "API online" once it can reach the backend.

By default the frontend calls `http://localhost:8000`. To point it at a
different backend URL, copy `.env.example` to `.env` and edit `VITE_API_URL`.

### Step 3 — Try it out
Use the "Load sample" button to auto-fill a known scam message for each
channel, or paste your own text, then click **Scan for threats**.

## 5. Example API usage

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "URGENT: Your bank account will be locked in 24 hours. Update your KYC now at http://secure-kyc-update.com/1234", "channel": "sms"}'
```

## 6. Notes for extending this project

- Replace the synthetic dataset with a real, larger labeled dataset for a
  stronger model and more credible metrics in your resume/report.
- Swap the in-memory history in `main.py` for SQLite/PostgreSQL if you want
  scans to persist across restarts.
- Add authentication (API keys / JWT) before deploying the API publicly.
- Consider adding a browser extension or SMS-forwarding integration as a
  stretch goal to make the "real-time" framing more literal.
