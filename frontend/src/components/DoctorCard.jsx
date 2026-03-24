import React, { useState } from 'react';
import { MapPin, Phone, Star, Info } from 'lucide-react';
import CardDetailModal from './CardDetailModal';

export default function DoctorCard({ doctor }) {
  const [showDetail, setShowDetail] = useState(false);
  const initials = (doctor.name || 'Dr').split(' ').slice(0, 2).map((w) => w[0]).join('').toUpperCase();

  return (
    <>
      <div className="card doctor-card card--clickable" onClick={() => setShowDetail(true)}>
        <div className="card-header">
          <div className="doctor-avatar">{initials}</div>
          <div className="card-title-group">
            <h3 className="card-title">{doctor.name}</h3>
            <span className="timing-badge" style={{ '--badge-color': 'var(--violet)' }}>
              {doctor.specialty}
            </span>
          </div>
          {doctor.rating && (
            <div className="rating-badge">
              <Star size={12} fill="var(--amber)" color="var(--amber)" />
              <span>{doctor.rating.toFixed(1)}</span>
            </div>
          )}
          <Info size={15} className="card-detail-hint" />
        </div>

        <div className="doctor-info">
          {doctor.address && (
            <div className="info-row"><MapPin size={13} /><span>{doctor.address}</span></div>
          )}
          {doctor.phone && (
            <div className="info-row"><Phone size={13} /><span>{doctor.phone}</span></div>
          )}
        </div>

        <div className="card-footer">
          <button
            className="card-btn"
            onClick={(e) => { e.stopPropagation(); if (doctor.maps_link) window.open(doctor.maps_link, '_blank'); }}
          >
            <MapPin size={13} /> Directions
          </button>
          <button className="card-btn card-btn--ghost" onClick={(e) => { e.stopPropagation(); setShowDetail(true); }}>
            <Info size={13} /> Details
          </button>
        </div>
      </div>

      {showDetail && <CardDetailModal type="doctor" data={doctor} onClose={() => setShowDetail(false)} />}
    </>
  );
}
