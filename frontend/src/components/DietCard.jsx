import React, { useState } from 'react';
import { Utensils, Clock, ChevronDown, ChevronUp, CheckCircle2, Info } from 'lucide-react';
import useHealthStore from '../store/useHealthStore';
import { logDiet } from '../api/client';
import CardDetailModal from './CardDetailModal';

const timingColors = {
  Morning: 'var(--amber)',
  Afternoon: 'var(--teal)',
  Evening: 'var(--violet)',
  Night: 'var(--indigo)',
};

export default function DietCard({ meal }) {
  const [showDetail, setShowDetail] = useState(false);
  const { sessionId, loggedMeals, toggleMeal } = useHealthStore();
  const logged = loggedMeals[meal.meal];

  const handleLog = async (e) => {
    e.stopPropagation();
    toggleMeal(meal.meal);
    if (sessionId) {
      try { await logDiet(sessionId, meal.meal); } catch (_) {}
    }
  };

  return (
    <>
      <div className={`card diet-card card--clickable ${logged ? 'card--done' : ''}`} onClick={() => setShowDetail(true)}>
        <div className="card-header">
          <span className="card-icon">{meal.icon || '🍽️'}</span>
          <div className="card-title-group">
            <h3 className="card-title">{meal.meal}</h3>
            <span className="timing-badge" style={{ '--badge-color': timingColors[meal.timing] || 'var(--teal)' }}>
              <Clock size={11} />{meal.timing}
            </span>
          </div>
          {logged && <CheckCircle2 className="card-check" size={20} />}
          <Info size={15} className="card-detail-hint" />
        </div>

        <p className="card-desc">{meal.description}</p>

        {meal.macros && (
          <div className="macro-row">
            {Object.entries(meal.macros).map(([k, v]) => (
              <span key={k} className="macro-chip"><b>{v}</b> {k}</span>
            ))}
          </div>
        )}

        <div className="card-footer">
          <button className={`card-btn ${logged ? 'card-btn--done' : ''}`} onClick={handleLog}>
            {logged ? '✓ Logged' : 'Log Meal'}
          </button>
          <button className="card-btn card-btn--ghost" onClick={(e) => { e.stopPropagation(); setShowDetail(true); }}>
            <Info size={13} /> Details
          </button>
        </div>
      </div>

      {showDetail && <CardDetailModal type="diet" data={meal} onClose={() => setShowDetail(false)} />}
    </>
  );
}
