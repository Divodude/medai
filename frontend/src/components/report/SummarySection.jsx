export default function SummarySection({ analysis }) {
  return (
    <div className="report-section">
      <div className="report-section-title">📝 Summary</div>
      <p className="summary-text">{analysis.summary}</p>
    </div>
  );
}
