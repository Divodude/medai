import { useState } from 'react';
import { useApp } from '../../context/AppContext.jsx';
import { searchDoctors } from '../../api/api.js';

export default function DoctorsSection({ analysis }) {
  const { state } = useApp();
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState('');

  async function handleLoad() {
    if (loading || loaded) return;
    setLoading(true);
    setError('');
    try {
      const data = await searchDoctors(
        analysis.specialty || 'general physician',
        analysis.structured_summary?.city || '',
        state.sessionId,
      );
      setDoctors(data.doctors || []);
      setLoaded(true);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="report-section">
      <div className="report-section-title">👨‍⚕️ Nearby Doctors</div>

      {!loaded && (
        <button className="btn-load-doctors" onClick={handleLoad} disabled={loading}>
          {loading ? 'Searching…' : `Find ${analysis.specialty || 'Doctors'} Near You`}
        </button>
      )}

      {error && (
        <div style={{ fontSize: 13, color: 'var(--sev-high)', marginTop: 8 }}>⚠️ {error}</div>
      )}

      {loaded && doctors.length === 0 && (
        <div style={{ fontSize: 13, color: 'var(--text-2)', marginTop: 8 }}>
          No nearby doctors found. Try again with a different city.
        </div>
      )}

      <div className="doctors-grid">
        {doctors.map((doc, i) => (
          <div key={i} className="doctor-card">
            <div className="doctor-icon">👨‍⚕️</div>
            <div className="doctor-info">
              <div className="doctor-name">{doc.name || 'Doctor'}</div>
              <div className="doctor-specialty">{doc.specialty}</div>
              {doc.address && <div className="doctor-address">📍 {doc.address}</div>}
              {doc.phone   && <div className="doctor-address">📞 {doc.phone}</div>}
              {doc.maps_link && (
                <a className="doctor-maps-link" href={doc.maps_link} target="_blank" rel="noreferrer">
                  View on Maps →
                </a>
              )}
            </div>
            {doc.rating && (
              <div style={{ fontSize: 13, color: 'var(--sev-medium)', fontWeight: 600 }}>
                ⭐ {doc.rating}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
