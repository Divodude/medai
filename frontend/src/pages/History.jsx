import React, { useEffect, useState } from 'react';
import { getAllSessions, getHistory } from '../api/client';
import { Clock, ChevronDown, ChevronUp } from 'lucide-react';

function AnalysisEntry({ a }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="history-entry">
      <div className="history-entry-header" onClick={() => setOpen(!open)}>
        <Clock size={14} />
        <span>{new Date(a.created_at).toLocaleString()}</span>
        <span className="history-condition">{a.condition}</span>
        <span
          className="severity-pill"
          style={{
            background: a.severity === 'HIGH' ? 'var(--red)' :
              a.severity === 'MEDIUM' ? 'var(--amber)' : 'var(--teal)'
          }}
        >
          {a.severity}
        </span>
        {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </div>
      {open && (
        <div className="history-entry-body">
          <p>{a.summary}</p>
          {a.key_findings?.length > 0 && (
            <ul className="findings-list">
              {a.key_findings.map((f, i) => <li key={i}>{f}</li>)}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

export default function History() {
  const [sessions, setSessions] = useState([]);
  const [selected, setSelected] = useState(null);
  const [historyData, setHistoryData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAllSessions().then(setSessions).finally(() => setLoading(false));
  }, []);

  const loadSession = async (id) => {
    setSelected(id);
    const data = await getHistory(id);
    setHistoryData(data);
  };

  return (
    <div className="history-page">
      <h1 className="hero-title" style={{ marginBottom: '2rem' }}>Health History</h1>

      {loading && <p className="empty-hint">Loading sessions…</p>}
      {!loading && sessions.length === 0 && (
        <p className="empty-hint">No sessions yet. Upload a report to get started.</p>
      )}

      <div className="history-layout">
        {/* Session list */}
        <div className="session-list">
          {sessions.map((s) => (
            <button
              key={s.id}
              className={`session-btn ${selected === s.id ? 'session-btn--active' : ''}`}
              onClick={() => loadSession(s.id)}
            >
              <span>{s.patient_name}</span>
              <span className="session-date">{new Date(s.created_at).toLocaleDateString()}</span>
            </button>
          ))}
        </div>

        {/* Detail panel */}
        {historyData && (
          <div className="history-detail">
            <h3 className="section-title">Reports</h3>
            {historyData.analyses.map((a) => <AnalysisEntry key={a.id} a={a} />)}

            <div className="history-stats">
              <div className="stat-box">
                <span className="stat-num">{historyData.diet_logs.length}</span>
                <span className="stat-label">Meals Logged</span>
              </div>
              <div className="stat-box">
                <span className="stat-num">{historyData.exercise_logs.filter((e) => e.completed).length}</span>
                <span className="stat-label">Exercises Done</span>
              </div>
              <div className="stat-box">
                <span className="stat-num">{historyData.doctors.length}</span>
                <span className="stat-label">Doctors Found</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
