export default function KeyFindingsSection({ analysis }) {
  const findings = analysis.key_findings || [];
  if (!findings.length) return null;
  return (
    <div className="report-section">
      <div className="report-section-title">🔍 Key Findings</div>
      <ul className="findings-list">
        {findings.map((f, i) => (
          <li key={i} className="finding-item">{f}</li>
        ))}
      </ul>
    </div>
  );
}
