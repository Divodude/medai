export default function RemediesSection({ analysis }) {
  const items = analysis.home_remedies || [];
  if (!items.length) return null;
  return (
    <div className="report-section">
      <div className="report-section-title">🌿 Home Remedies</div>
      <div className="cards-grid">
        {items.map((item, i) => (
          <div key={i} className="health-card">
            <span className="health-card-text">{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
