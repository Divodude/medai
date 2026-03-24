import React, { useEffect } from 'react';
import { X, Clock, Flame, Leaf, Stethoscope, MapPin, Phone, Star, ExternalLink, ChevronRight } from 'lucide-react';

/**
 * Generic card detail modal.
 * Pass `type` = 'diet' | 'exercise' | 'remedy' | 'doctor'
 * and `data` = the card's data object.
 */
export default function CardDetailModal({ type, data, onClose }) {
  // Close on Escape
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  if (!data) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <span className="modal-icon">{data.icon || getDefaultIcon(type)}</span>
          <div>
            <h2 className="modal-title">{getTitle(type, data)}</h2>
            <p className="modal-sub">{getSubtitle(type, data)}</p>
          </div>
          <button className="modal-close" onClick={onClose}><X size={18} /></button>
        </div>

        {/* Body */}
        <div className="modal-body">
          {type === 'diet' && <DietDetail data={data} />}
          {type === 'exercise' && <ExerciseDetail data={data} />}
          {type === 'remedy' && <RemedyDetail data={data} />}
          {type === 'doctor' && <DoctorDetail data={data} />}
        </div>
      </div>
    </div>
  );
}

function getDefaultIcon(type) {
  return { diet: '🍽️', exercise: '🏋️', remedy: '🌿', doctor: '👨‍⚕️' }[type] || '📋';
}
function getTitle(type, d) {
  return d.meal || d.name || d.remedy || 'Details';
}
function getSubtitle(type, d) {
  return { diet: d.timing, exercise: d.difficulty, remedy: d.frequency, doctor: d.specialty }[type] || '';
}

// ─── Diet detail ──────────────────────────────────────────────────────────────
function DietDetail({ data }) {
  return (
    <div className="detail-sections">
      <Section title="About this meal" icon={<Leaf size={15} />}>
        <p className="detail-text">{data.description}</p>
      </Section>

      {data.macros && (
        <Section title="Nutritional Info" icon={<ChevronRight size={15} />}>
          <div className="detail-grid">
            {Object.entries(data.macros).map(([k, v]) => (
              <div key={k} className="detail-stat">
                <span className="detail-stat-val">{v}</span>
                <span className="detail-stat-label">{k}</span>
              </div>
            ))}
          </div>
        </Section>
      )}

      <Section title="When to eat" icon={<Clock size={15} />}>
        <div className="detail-badge">{data.timing}</div>
      </Section>
    </div>
  );
}

// ─── Exercise detail ──────────────────────────────────────────────────────────
function ExerciseDetail({ data }) {
  return (
    <div className="detail-sections">
      <Section title="How to do it" icon={<Flame size={15} />}>
        <p className="detail-text">{data.description}</p>
      </Section>

      <Section title="Session details" icon={<ChevronRight size={15} />}>
        <div className="detail-grid">
          <div className="detail-stat">
            <span className="detail-stat-val">{data.duration}</span>
            <span className="detail-stat-label">Duration</span>
          </div>
          {data.reps && (
            <div className="detail-stat">
              <span className="detail-stat-val">{data.reps}</span>
              <span className="detail-stat-label">Reps / Sets</span>
            </div>
          )}
          <div className="detail-stat">
            <span className="detail-stat-val" style={{ color: data.difficulty === 'Hard' ? 'var(--red)' : data.difficulty === 'Moderate' ? 'var(--amber)' : 'var(--teal)' }}>
              {data.difficulty}
            </span>
            <span className="detail-stat-label">Difficulty</span>
          </div>
        </div>
      </Section>

      {data.benefit && (
        <Section title="Why this helps" icon={<Leaf size={15} />}>
          <p className="detail-text">{data.benefit}</p>
        </Section>
      )}
    </div>
  );
}

// ─── Remedy detail ────────────────────────────────────────────────────────────
function RemedyDetail({ data }) {
  return (
    <div className="detail-sections">
      <Section title="Why it works" icon={<Leaf size={15} />}>
        <p className="detail-text">{data.benefit}</p>
      </Section>

      {data.ingredients?.length > 0 && (
        <Section title="Ingredients" icon={<ChevronRight size={15} />}>
          <div className="detail-tags">
            {data.ingredients.map((ing, i) => (
              <span key={i} className="ingredient-chip">{ing}</span>
            ))}
          </div>
        </Section>
      )}

      {data.instructions?.length > 0 && (
        <Section title="Step-by-step instructions" icon={<ChevronRight size={15} />}>
          <ol className="detail-steps">
            {data.instructions.map((step, i) => (
              <li key={i} className="detail-step">
                <span className="step-num">{i + 1}</span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
        </Section>
      )}

      <Section title="Frequency" icon={<Clock size={15} />}>
        <div className="detail-badge">{data.frequency}</div>
      </Section>
    </div>
  );
}

// ─── Doctor detail ────────────────────────────────────────────────────────────
function DoctorDetail({ data }) {
  const initials = (data.name || 'Dr').split(' ').slice(0, 2).map((w) => w[0]).join('').toUpperCase();
  return (
    <div className="detail-sections">
      <div className="doctor-hero">
        <div className="doctor-avatar doctor-avatar--lg">{initials}</div>
        <div>
          <h3 className="detail-text" style={{ fontWeight: 700, fontSize: '1.05rem' }}>{data.name}</h3>
          <span className="timing-badge" style={{ '--badge-color': 'var(--violet)' }}>{data.specialty}</span>
        </div>
      </div>

      <Section title="Contact & Location" icon={<MapPin size={15} />}>
        {data.address && (
          <div className="info-row"><MapPin size={13} /><span>{data.address}</span></div>
        )}
        {data.phone && (
          <div className="info-row"><Phone size={13} /><span>{data.phone}</span></div>
        )}
        {data.rating && (
          <div className="info-row"><Star size={13} fill="var(--amber)" color="var(--amber)" /><span>{data.rating} / 5</span></div>
        )}
      </Section>

      <div className="detail-actions">
        {data.maps_link && (
          <a className="card-btn" href={data.maps_link} target="_blank" rel="noreferrer">
            <MapPin size={14} /> Get Directions
          </a>
        )}
        {data.phone && (
          <a className="card-btn card-btn--ghost" href={`tel:${data.phone.replace(/\s/g, '')}`}>
            <Phone size={14} /> Call Now
          </a>
        )}
        {data.source_url && (
          <a className="card-btn card-btn--ghost" href={data.source_url} target="_blank" rel="noreferrer">
            <ExternalLink size={14} /> View Online
          </a>
        )}
      </div>
    </div>
  );
}

// ─── Shared sub-component ────────────────────────────────────────────────────
function Section({ title, icon, children }) {
  return (
    <div className="detail-section">
      <div className="detail-section-title">{icon}{title}</div>
      {children}
    </div>
  );
}
