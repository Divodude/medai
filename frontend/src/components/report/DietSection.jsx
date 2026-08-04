import { useState } from 'react';
import { useApp } from '../../context/AppContext.jsx';
import { logDiet } from '../../api/api.js';

export default function DietSection({ analysis }) {
  const { state } = useApp();
  const items = analysis.diet_plan || [];
  const [logged, setLogged] = useState({});

  if (!items.length) return null;

  async function handleLog(item, idx) {
    if (logged[idx]) return;
    try {
      await logDiet(state.sessionId, item);
      setLogged((p) => ({ ...p, [idx]: true }));
    } catch (e) {
      console.error('Failed to log diet', e);
    }
  }

  return (
    <div className="report-section">
      <div className="report-section-title">🥗 Diet Plan</div>
      <div className="cards-grid">
        {items.map((item, i) => (
          <div key={i} className="health-card">
            <span className="health-card-text">{item}</span>
            <button
              className={`btn-log${logged[i] ? ' logged' : ''}`}
              onClick={() => handleLog(item, i)}
            >
              {logged[i] ? '✓ Logged' : 'Log'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
