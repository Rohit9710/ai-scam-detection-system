import React from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from "recharts";

const RISK_COLORS = { High: "#FF4C61", Medium: "#FFB84C", Low: "#3DDC97" };
const CHANNEL_COLORS = ["#4CC9F0", "#8A6CF0", "#3DDC97"];

export default function StatsPanel({ stats, onClear }) {
  if (!stats) return null;

  const channelData = Object.entries(stats.by_channel).map(([name, value]) => ({
    name: name.toUpperCase(),
    value,
  }));

  const riskData = Object.entries(stats.by_risk_level).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div className="stats-panel">
      <div className="stats-header">
        <h2>Threat Analytics</h2>
        {stats.total_scanned > 0 && (
          <button className="btn-ghost btn-small" onClick={onClear}>
            Clear history
          </button>
        )}
      </div>

      <div className="stats-cards">
        <div className="stat-card">
          <span className="stat-value">{stats.total_scanned}</span>
          <span className="stat-label">Messages scanned</span>
        </div>
        <div className="stat-card">
          <span className="stat-value stat-danger">{stats.total_scams_detected}</span>
          <span className="stat-label">Scams detected</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{Math.round(stats.scam_rate * 100)}%</span>
          <span className="stat-label">Scam rate</span>
        </div>
      </div>

      {stats.total_scanned > 0 ? (
        <div className="charts-row">
          <div className="chart-box">
            <h3>By channel</h3>
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={channelData}>
                <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} />
                <YAxis allowDecimals={false} stroke="var(--text-muted)" fontSize={12} width={24} />
                <Tooltip
                  contentStyle={{ background: "#161C24", border: "1px solid #232B33", fontSize: 12 }}
                />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {channelData.map((_, i) => (
                    <Cell key={i} fill={CHANNEL_COLORS[i % CHANNEL_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-box">
            <h3>By risk level</h3>
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie data={riskData} dataKey="value" nameKey="name" innerRadius={35} outerRadius={60} paddingAngle={3}>
                  {riskData.map((entry, i) => (
                    <Cell key={i} fill={RISK_COLORS[entry.name] || "#666"} />
                  ))}
                </Pie>
                <Legend
                  verticalAlign="middle"
                  align="right"
                  layout="vertical"
                  wrapperStyle={{ fontSize: 12, color: "var(--text-muted)" }}
                />
                <Tooltip contentStyle={{ background: "#161C24", border: "1px solid #232B33", fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : (
        <p className="stats-empty">Scan a message to start building analytics.</p>
      )}

      {stats.recent_history.length > 0 && (
        <div className="history-list">
          <h3>Recent scans</h3>
          <ul>
            {stats.recent_history.map((item) => (
              <li key={item.id} className={`history-item risk-${item.risk_level.toLowerCase()}`}>
                <span className="history-dot" />
                <span className="history-text">{item.text}</span>
                <span className="history-risk">{item.risk_level}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
