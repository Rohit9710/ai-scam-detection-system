import React from "react";
import RiskGauge from "./RiskGauge.jsx";

const FLAG_LABELS = {
  has_url: "Contains link",
  has_money_mention: "Mentions money amount",
  urgency_keywords: "Urgency language",
  sensitive_data_requests: "Requests sensitive data",
  reward_bait_keywords: "Reward / cashback bait",
  excessive_punctuation: "Excessive punctuation",
};

const HIT = /(https?:\/\/\S+|bit\.ly\/\S+|urgent|immediately|verify|kyc|blocked|suspended|locked|otp|pin|password|claim|won|cashback|refund|lottery|free|expire\w*|24 hours|click)/gi;

function Highlighted({ text }) {
  return text.split(HIT).map((part, i) =>
    i % 2 === 1 ? <mark key={i} className="hit">{part}</mark> : <React.Fragment key={i}>{part}</React.Fragment>
  );
}

export default function ResultCard({ result }) {
  if (!result) return null;

  const verdict = result.is_scam ? "SCAM DETECTED" : "LIKELY LEGITIMATE";
  const verdictClass = result.is_scam ? "verdict-bad" : "verdict-good";

  const activeFlags = Object.entries(result.red_flags).filter(([key, val]) =>
    typeof val === "boolean" ? val : val > 0
  );

  return (
    <div className={`result-card risk-${result.risk_level.toLowerCase()}`}>
      <div className="result-top">
        <RiskGauge probability={result.scam_probability} riskLevel={result.risk_level} />
        <div className="result-meta">
          <span className={`verdict-badge ${verdictClass}`}>{verdict}</span>
          <div className="result-channel">
            {result.channel.toUpperCase()} · Risk level:{" "}
            <strong className={`risk-text risk-text-${result.risk_level.toLowerCase()}`}>
              {result.risk_level}
            </strong>
          </div>
        </div>
      </div>

      <p className="result-explanation">{result.explanation}</p>

      {activeFlags.length > 0 && (
        <div className="flag-chips">
          {activeFlags.map(([key]) => (
            <span key={key} className="flag-chip">
              {FLAG_LABELS[key] || key}
            </span>
          ))}
        </div>
      )}

      <div className="result-source">
        <span className="result-source-label">Analyzed message · suspicious words highlighted</span>
        <p className="result-source-text"><Highlighted text={result.text} /></p>
      </div>
    </div>
  );
}
