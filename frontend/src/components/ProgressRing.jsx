import React from 'react';

export default function ProgressRing({ value = 0, total = 1, size = 64, label }) {
  const pct = total === 0 ? 0 : Math.round((value / total) * 100);
  const r = (size - 8) / 2;
  const circ = 2 * Math.PI * r;
  const dash = circ - (pct / 100) * circ;

  return (
    <div className="progress-ring-wrap" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={6}
        />
        <circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none"
          stroke="url(#ring-grad)"
          strokeWidth={6}
          strokeDasharray={circ}
          strokeDashoffset={dash}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: 'stroke-dashoffset 0.5s ease' }}
        />
        <defs>
          <linearGradient id="ring-grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="var(--teal)" />
            <stop offset="100%" stopColor="var(--violet)" />
          </linearGradient>
        </defs>
      </svg>
      <div className="ring-center">
        <span className="ring-pct">{pct}%</span>
      </div>
      {label && <div className="ring-label">{label}</div>}
    </div>
  );
}
