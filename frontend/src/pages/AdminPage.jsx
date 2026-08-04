import { useEffect, useState } from 'react';
import { getAllPipelineRuns } from '../api/api.js';

function formatDate(str) {
  if (!str) return '—';
  return new Date(str).toLocaleString();
}

function duration(start, end) {
  if (!start || !end) return '—';
  const ms = new Date(end) - new Date(start);
  return `${(ms / 1000).toFixed(1)}s`;
}

export default function AdminPage() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getAllPipelineRuns()
      .then(setRuns)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ background: 'var(--bg-page)', minHeight: '100vh' }}>
      <div className="admin-page">
        <h1>⚙️ ETL Pipeline Admin</h1>
        <p className="sub">
          Live audit trail of all pipeline runs. Each upload triggers an Extract → Transform → Load job tracked here.
          <a href="/" style={{ marginLeft: 12, color: 'var(--accent)' }}>← Back to App</a>
        </p>

        {loading && <p style={{ color: 'var(--text-2)' }}>Loading pipeline runs…</p>}
        {error   && <p style={{ color: 'var(--sev-high)' }}>⚠️ {error}</p>}

        {!loading && !error && runs.length === 0 && (
          <p style={{ color: 'var(--text-2)', fontSize: 14 }}>
            No pipeline runs yet. Upload a medical report to see ETL executions here.
          </p>
        )}

        {runs.length > 0 && (
          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Run ID</th>
                  <th>Patient</th>
                  <th>Filename</th>
                  <th>Status</th>
                  <th>Duration</th>
                  <th>Records</th>
                  <th>Started</th>
                  <th>Error</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((r) => (
                  <tr key={r.id}>
                    <td style={{ color: 'var(--text-3)', fontFamily: 'monospace' }}>#{r.id}</td>
                    <td>{r.patient_name || '—'}</td>
                    <td style={{ color: 'var(--text-2)', fontFamily: 'monospace', fontSize: 12 }}>{r.filename}</td>
                    <td>
                      <span className={`status-chip status-${r.status}`}>{r.status}</span>
                    </td>
                    <td style={{ color: 'var(--text-2)' }}>{duration(r.started_at, r.completed_at)}</td>
                    <td style={{ textAlign: 'center' }}>{r.records_loaded ?? 0}</td>
                    <td style={{ color: 'var(--text-3)', fontSize: 12 }}>{formatDate(r.started_at)}</td>
                    <td>
                      {r.error_message
                        ? <span className="error-text">{r.error_message.slice(0, 80)}…</span>
                        : <span style={{ color: 'var(--text-3)' }}>—</span>
                      }
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
