import { useApp } from '../../context/AppContext.jsx';

export default function ChatHeader() {
  const { state, dispatch } = useApp();
  const { analysis, reportOpen, patientName, sessionId } = state;

  const sev = analysis?.severity || '';

  return (
    <div className="chat-header">
      {analysis && (
        <button
          className={`btn-report${reportOpen ? ' active' : ''}`}
          onClick={() => dispatch({ type: 'TOGGLE_REPORT' })}
          title={reportOpen ? 'Collapse report' : 'View full analysis report'}
        >
          📋 Report
          {sev && (
            <span className={`severity-badge severity-${sev}`} style={{ fontSize: 11 }}>
              {sev}
            </span>
          )}
        </button>
      )}

      <div style={{ flex: 1 }}>
        <div className="chat-header-title">
          {sessionId ? patientName : 'AI Health Assistant'}
        </div>
        {analysis && (
          <div className="chat-header-subtitle">
            {analysis.condition} · {analysis.specialty}
          </div>
        )}
      </div>
    </div>
  );
}
