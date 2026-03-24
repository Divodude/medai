import React, { useState } from 'react';
import { Flame, CheckCircle2, Info } from 'lucide-react';
import useHealthStore from '../store/useHealthStore';
import { logExercise } from '../api/client';
import CardDetailModal from './CardDetailModal';

const difficultyColors = { Easy: 'var(--teal)', Moderate: 'var(--amber)', Hard: 'var(--red)' };

export default function ExerciseCard({ exercise }) {
  const [showDetail, setShowDetail] = useState(false);
  const { sessionId, completedExercises, toggleExercise } = useHealthStore();
  const done = completedExercises[exercise.name];

  const handleToggle = async (e) => {
    e.stopPropagation();
    toggleExercise(exercise.name);
    if (sessionId) {
      try { await logExercise(sessionId, exercise.name, !done); } catch (_) {}
    }
  };

  return (
    <>
      <div
        className={`card exercise-card card--clickable ${done ? 'card--done' : ''}`}
        onClick={() => setShowDetail(true)}
      >
        <div className="card-header">
          <span className="card-icon">{exercise.icon || '🏋️'}</span>
          <div className="card-title-group">
            <h3 className="card-title">{exercise.name}</h3>
            <span className="timing-badge" style={{ '--badge-color': difficultyColors[exercise.difficulty] || 'var(--teal)' }}>
              <Flame size={11} />{exercise.difficulty}
            </span>
          </div>
          {done && <CheckCircle2 className="card-check" size={20} />}
          <Info size={15} className="card-detail-hint" />
        </div>

        <p className="card-desc">{exercise.description}</p>

        <div className="exercise-meta">
          <div className="meta-pill">
            <span className="meta-label">Duration</span>
            <span className="meta-val">{exercise.duration}</span>
          </div>
          {exercise.reps && (
            <div className="meta-pill">
              <span className="meta-label">Reps</span>
              <span className="meta-val">{exercise.reps}</span>
            </div>
          )}
        </div>

        {exercise.benefit && <p className="card-benefit">💡 {exercise.benefit}</p>}

        <div className="card-footer">
          <button className={`card-btn ${done ? 'card-btn--done' : ''}`} onClick={handleToggle}>
            {done ? '✓ Done' : 'Mark Done'}
          </button>
          <button className="card-btn card-btn--ghost" onClick={(e) => { e.stopPropagation(); setShowDetail(true); }}>
            <Info size={13} /> Details
          </button>
        </div>
      </div>

      {showDetail && <CardDetailModal type="exercise" data={exercise} onClose={() => setShowDetail(false)} />}
    </>
  );
}
