import React from "react";

/**
 * RiskGauge
 * A semi-circular arc gauge showing scam probability from 0-100%.
 * The signature visual element of the dashboard: the arc fills and its
 * color transitions from safe-green through amber to alert-red as the
 * scam probability rises.
 */
export default function RiskGauge({ probability = 0, riskLevel = "Low" }) {
  const pct = Math.max(0, Math.min(1, probability));
  const radius = 80;
  const cx = 100;
  const cy = 100;
  const startAngle = 180; // degrees, left side
  const endAngle = 0; // right side (180deg sweep)
  const sweep = 180;

  const angle = startAngle - sweep * pct;
  const toRad = (deg) => (deg * Math.PI) / 180;
  const arcX = cx + radius * Math.cos(toRad(angle));
  const arcY = cy - radius * Math.sin(toRad(angle));

  const largeArc = pct > 0.5 ? 1 : 0;

  const color =
    riskLevel === "High" ? "var(--risk-high)" : riskLevel === "Medium" ? "var(--risk-med)" : "var(--risk-low)";

  const bgPath = `M ${cx - radius} ${cy} A ${radius} ${radius} 0 1 1 ${cx + radius} ${cy}`;
  const fgPath = `M ${cx - radius} ${cy} A ${radius} ${radius} 0 ${largeArc} 1 ${arcX} ${arcY}`;

  return (
    <div className="gauge">
      <svg viewBox="0 0 200 115" width="220" height="128">
        <path d={bgPath} fill="none" stroke="var(--border)" strokeWidth="14" strokeLinecap="round" />
        <path d={fgPath} fill="none" stroke={color} strokeWidth="14" strokeLinecap="round" className="gauge-fg" />
        <text x="100" y="88" textAnchor="middle" className="gauge-value" fill={color}>
          {Math.round(pct * 100)}%
        </text>
        <text x="100" y="106" textAnchor="middle" className="gauge-label">
          scam probability
        </text>
      </svg>
    </div>
  );
}
