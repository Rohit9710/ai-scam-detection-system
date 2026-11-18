import React, { useEffect, useState, useCallback } from "react";
import ScanForm from "./components/ScanForm.jsx";
import ResultCard from "./components/ResultCard.jsx";
import StatsPanel from "./components/StatsPanel.jsx";
import { checkHealth, predictScam, fetchStats, clearHistory } from "./api.js";

const STEPS = [
  { icon: "📥", title: "Paste", text: "Drop in any email, SMS or UPI message." },
  { icon: "🧠", title: "Analyze", text: "NLP + ML scan for scam patterns in milliseconds." },
  { icon: "🛡️", title: "Decide", text: "Get a risk score and the exact red flags." },
];
const TIPS = [
  "Banks never ask for your OTP, PIN or CVV.",
  "A UPI collect request never means you receive money.",
  "Urgency + a link is the classic scam combo.",
  "Check the domain: 'acc0unt-verify.in' is not your bank.",
];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export default function App() {
  const [apiOnline, setApiOnline] = useState(null);
  const [modelName, setModelName] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [tip, setTip] = useState(0);

  const loadStats = useCallback(async () => {
    try { setStats(await fetchStats()); } catch (e) { console.error(e); }
  }, []);

  useEffect(() => {
    checkHealth().then((h) => { setApiOnline(true); setModelName(h.model_name); }).catch(() => setApiOnline(false));
    loadStats();
    const t = setInterval(() => setTip((n) => (n + 1) % TIPS.length), 4000);
    return () => clearInterval(t);
  }, [loadStats]);

  async function handleScan(text, channel) {
    setIsScanning(true); setError(null); setResult(null);
    try {
      const [data] = await Promise.all([predictScam(text, channel), sleep(1100)]);
      setResult(data); loadStats();
    } catch (err) {
      setError(err.message || "Could not reach the server. It may be waking up — try again in a few seconds.");
    } finally { setIsScanning(false); }
  }

  async function handleClear() { await clearHistory(); setStats(null); loadStats(); }

  return (
    <div className="app">
      <div className="bg-grid" /><div className="bg-glow" />
      <header className="app-header">
        <div className="brand"><span className="brand-mark">◈</span><h1>SentryNet</h1></div>
        <div className={`status-pill ${apiOnline ? "online" : apiOnline === false ? "offline" : "pending"}`}>
          <span className="status-dot" />
          {apiOnline === null ? "Connecting…" : apiOnline ? `Live · ${modelName}` : "API offline / waking up"}
        </div>
      </header>

      <section className="hero">
        <h2>Spot the scam <span className="grad">before it spots you.</span></h2>
        <p>AI that detects phishing emails, fake SMS and UPI fraud in real time.</p>
        <div className="steps">
          {STEPS.map((s) => (
            <div className="step" key={s.title}><span className="step-icon">{s.icon}</span><b>{s.title}</b><small>{s.text}</small></div>
          ))}
        </div>
      </section>

      <main className="app-main">
        <section className="panel">
          <h3 className="section-title">Threat scanner</h3>
          <ScanForm onScan={handleScan} isScanning={isScanning} />
          {error && <div className="error-banner">{error}</div>}
          {result && <ResultCard result={result} />}
        </section>
        <section className="panel"><StatsPanel stats={stats} onClear={handleClear} /></section>
      </main>

      <div className="tip-bar" key={tip}>💡 <span>{TIPS[tip]}</span></div>
      <footer className="app-footer">Python · Scikit-learn · FastAPI · React — educational scam-detection demo</footer>
    </div>
  );
}
