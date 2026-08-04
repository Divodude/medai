export default function ProfileSection({ analysis }) {
  const p = analysis.structured_summary;
  if (!p) return null;

  const cells = [
    { label: 'Age',        value: p.age       || '—' },
    { label: 'Gender',     value: p.gender     || '—' },
    { label: 'Diagnoses',  value: (p.diagnoses || []).join(', ') || '—' },
    { label: 'Medications',value: (p.medications || []).join(', ') || '—' },
    { label: 'Allergies',  value: (p.allergies || []).join(', ') || '—' },
    { label: 'Deficiencies',value: (p.deficiencies || []).join(', ') || '—' },
  ];

  const labs = p.abnormal_lab_values || [];

  return (
    <div className="report-section">
      <div className="report-section-title">👤 Patient Profile</div>
      <div className="profile-grid">
        {cells.map((c) => (
          <div key={c.label} className="profile-cell">
            <div className="profile-cell-label">{c.label}</div>
            <div className="profile-cell-value">{c.value}</div>
          </div>
        ))}
      </div>

      {labs.length > 0 && (
        <>
          <div style={{ marginTop: 12, fontSize: 12, fontWeight: 600, color: 'var(--text-2)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Abnormal Lab Values
          </div>
          <div className="profile-grid" style={{ marginTop: 6 }}>
            {labs.map((lab, i) => (
              <div key={i} className="profile-cell" style={{ borderColor: 'rgba(248,81,73,0.25)' }}>
                <div className="profile-cell-label">{lab.marker}</div>
                <div className="profile-cell-value" style={{ color: 'var(--sev-high)' }}>
                  {lab.value} {lab.unit}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
