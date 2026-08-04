import { useEffect } from 'react';
import { useApp } from '../../context/AppContext.jsx';
import { listSessions, getHistory } from '../../api/api.js';
import SessionItem from './SessionItem.jsx';

export default function SessionSidebar() {
  const { state, dispatch } = useApp();

  // Load sessions on mount
  useEffect(() => {
    listSessions()
      .then((data) => dispatch({ type: 'SET_SESSIONS', payload: data }))
      .catch(() => {});
  }, [state.sessionId]); // refresh when session changes

  async function handleSwitch(session) {
    if (session.id === state.sessionId) return;
    try {
      const history = await getHistory(session.id);
      const latest  = history.analyses?.[0] || null;
      dispatch({
        type: 'SWITCH_SESSION',
        payload: {
          sessionId:   session.id,
          patientName: session.patient_name,
          analysis:    latest,
        },
      });
      localStorage.setItem('medai_session_id',   session.id);
      localStorage.setItem('medai_patient_name', session.patient_name);
    } catch (e) {
      console.error('Failed to switch session', e);
    }
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="app-logo">
          <span className="logo-icon">🏥</span>
          MedAI
        </div>
        <button
          className="btn-new-session"
          onClick={() => dispatch({ type: 'NEW_SESSION' })}
        >
          ＋ New Session
        </button>
      </div>

      <div className="sidebar-section-label">Recent Sessions</div>

      <ul className="session-list">
        {state.sessions.length === 0 && (
          <li style={{ padding: '10px 10px', fontSize: 12, color: 'var(--text-3)' }}>
            No sessions yet. Upload a report!
          </li>
        )}
        {state.sessions.map((s) => (
          <SessionItem
            key={s.id}
            session={s}
            active={s.id === state.sessionId}
            onClick={() => handleSwitch(s)}
          />
        ))}
      </ul>

      <div className="sidebar-footer">
        <a href="/admin" target="_blank" rel="noreferrer">⚙ ETL Pipeline Admin</a>
      </div>
    </aside>
  );
}
