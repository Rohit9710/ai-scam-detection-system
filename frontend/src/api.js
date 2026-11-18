/**
 * api.js
 * Thin wrapper around the backend REST API.
 * Set VITE_API_URL in a .env file to point at a deployed backend;
 * defaults to the local FastAPI dev server.
 */

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function handle(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed with status ${res.status}`);
  }
  return res.json();
}

export async function checkHealth() {
  const res = await fetch(`${API_URL}/api/health`);
  return handle(res);
}

export async function predictScam(text, channel) {
  const res = await fetch(`${API_URL}/api/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, channel }),
  });
  return handle(res);
}

export async function fetchStats() {
  const res = await fetch(`${API_URL}/api/stats`);
  return handle(res);
}

export async function clearHistory() {
  const res = await fetch(`${API_URL}/api/history`, { method: "DELETE" });
  return handle(res);
}
