import React, { useState } from "react";

const CHANNELS = [
  { id: "email", label: "✉ Email" },
  { id: "sms", label: "💬 SMS" },
  { id: "upi", label: "₹ UPI" },
];

const SAMPLES = {
  email: [
    { tag: "🚨 Fake bank alert", text: "URGENT: Your bank account will be locked in 24 hours. Update your KYC details now at http://secure-kyc-update.com/8823" },
    { tag: "✅ Meeting note", text: "Hi, just confirming our meeting scheduled for Monday at 11:30 AM. Let me know if that works." },
  ],
  sms: [
    { tag: "🚨 Cashback bait", text: "You won Rs 25000 cashback! Claim now bit.ly/verify-now/4471 Offer valid 30 mins only" },
    { tag: "✅ Delivery update", text: "Your order has been delivered. Thank you for shopping with us." },
  ],
  upi: [
    { tag: "🚨 Collect-request trap", text: "You have received a payment request of Rs 5000 from unknown@upi. Approve to receive money at http://upi-refund-portal.com/9012" },
    { tag: "✅ Real payment", text: "You paid Rs 250 to Local Grocery Store via UPI. Thank you." },
  ],
};

export default function ScanForm({ onScan, isScanning }) {
  const [channel, setChannel] = useState("email");
  const [text, setText] = useState("");

  return (
    <form className="scan-form" onSubmit={(e) => { e.preventDefault(); if (text.trim()) onScan(text.trim(), channel); }}>
      <div className="channel-tabs" role="tablist">
        {CHANNELS.map((c) => (
          <button type="button" key={c.id} role="tab" aria-selected={channel === c.id}
            className={`channel-tab ${channel === c.id ? "active" : ""}`} onClick={() => setChannel(c.id)}>
            {c.label}
          </button>
        ))}
      </div>

      <div className={`textarea-wrap ${isScanning ? "scanning" : ""}`}>
        <textarea className="scan-textarea" rows={6} value={text} maxLength={2000}
          placeholder={`Paste a suspicious ${channel.toUpperCase()} message here…`}
          onChange={(e) => setText(e.target.value)} />
        {isScanning && <div className="scan-line" />}
      </div>

      <div className="sample-row">
        <span className="sample-label">Try one:</span>
        {SAMPLES[channel].map((s) => (
          <button type="button" key={s.tag} className="sample-chip" onClick={() => setText(s.text)}>{s.tag}</button>
        ))}
        <span className="char-count">{text.length}/2000</span>
      </div>

      <button type="submit" className="btn-primary btn-wide" disabled={isScanning || !text.trim()}>
        {isScanning ? "Analyzing patterns…" : "Scan for threats →"}
      </button>
    </form>
  );
}
