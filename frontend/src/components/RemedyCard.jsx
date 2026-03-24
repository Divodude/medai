import React, { useState } from 'react';
import { Info } from 'lucide-react';
import CardDetailModal from './CardDetailModal';

export default function RemedyCard({ remedy }) {
  const [showDetail, setShowDetail] = useState(false);

  return (
    <>
      <div className="card remedy-card card--clickable" onClick={() => setShowDetail(true)}>
        <div className="card-header">
          <span className="card-icon">{remedy.icon || '🌿'}</span>
          <div className="card-title-group">
            <h3 className="card-title">{remedy.remedy}</h3>
            <span className="timing-badge" style={{ '--badge-color': 'var(--green)' }}>
              {remedy.frequency}
            </span>
          </div>
          <Info size={15} className="card-detail-hint" />
        </div>

        <p className="card-desc">{remedy.benefit}</p>

        <div className="ingredient-row">
          {(remedy.ingredients || []).map((ing, i) => (
            <span key={i} className="ingredient-chip">{ing}</span>
          ))}
        </div>

        <div className="card-footer">
          <button className="card-btn" onClick={(e) => { e.stopPropagation(); setShowDetail(true); }}>
            <Info size={13} /> View Full Guide
          </button>
        </div>
      </div>

      {showDetail && <CardDetailModal type="remedy" data={remedy} onClose={() => setShowDetail(false)} />}
    </>
  );
}
