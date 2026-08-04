import { useState } from 'react';
import { useApp } from '../../context/AppContext.jsx';
import { logExercise } from '../../api/api.js';

export default function ExerciseSection({ analysis }) {
  const { state } = useApp();
  const items = analysis.exercise_plan || [];
  const [done, setDone] = useState({});

  if (!items.length) return null;

  async function handleToggle(item, idx) {
    const newVal = !done[idx];
    try {
      await logExercise(state.sessionId, item, newVal);
      setDone((p) => ({ ...p, [idx]: newVal }));
    } catch (e) {
      console.error('Failed to log exercise', e);
    }
  }

  return (
    <div className="report-section">
      <div className="report-section-title">🏋️ Exercise Plan</div>
      <div className="cards-grid">
        {items.map((item, i) => (
          <div key={i} className="health-card">
            <button
              className={`btn-complete${done[i] ? ' done' : ''}`}
              onClick={() => handleToggle(item, i)}
              title="Mark complete"
            />
            <span className="health-card-text" style={{ textDecoration: done[i] ? 'line-through' : 'none', color: done[i] ? 'var(--text-3)' : 'var(--text-1)' }}>
              {item}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
