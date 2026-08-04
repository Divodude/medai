import { useState, useRef } from 'react';
import { useApp } from '../../context/AppContext.jsx';
import { analyzeReport } from '../../api/api.js';

const STAGES = ['Extracting', 'Transforming', 'Loading'];

export default function UploadModal({ onClose }) {
  const { state, dispatch } = useApp();
  const [file, setFile] = useState(null);
  const [name, setName] = useState(state.patientName || '');
  const [city, setCity] = useState('');
  const [drag, setDrag] = useState(false);
  const [stageIdx, setStageIdx] = useState(-1);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  function handleDrop(e) {
    e.preventDefault();
    setDrag(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  }

  async function handleSubmit() {
    if (!file || uploading) return;

    setUploading(true);
    setStageIdx(0);

    // Simulate stage progression (actual work happens server-side)
    const stageTimer = setInterval(() => {
      setStageIdx((i) => (i < STAGES.length - 1 ? i + 1 : i));
    }, 2200);

    try {
      const result = await analyzeReport(file, state.sessionId, name || 'Patient', city);
      clearInterval(stageTimer);

      dispatch({
        type: 'SET_ANALYSIS',
        payload: {
          analysis:    result,
          sessionId:   result.session_id,
          patientName: name || 'Patient',
        },
      });

      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          role: 'ai',
          content:
            `✅ Report analysed! I found: **${result.condition}** (${result.severity} severity).\n\n` +
            `${result.summary}\n\n` +
            `Click **📋 Report** at the top to view your full health plan including diet, exercise, and home remedies. Feel free to ask me anything!`,
          streaming: false,
        },
      });

      dispatch({ type: 'OPEN_REPORT' });
      onClose();
    } catch (e) {
      clearInterval(stageTimer);
      dispatch({
        type: 'ADD_MESSAGE',
        payload: { role: 'ai', content: `⚠️ Analysis failed: ${e.message}`, streaming: false },
      });
      onClose();
    } finally {
      setUploading(false);
      setStageIdx(-1);
    }
  }

  return (
    <div className="upload-modal-overlay" onClick={(e) => { if (!uploading && e.target === e.currentTarget) onClose(); }}>
      <div className="upload-modal">
        <h2>Upload Medical Report</h2>
        <p>Supports PDF, images (JPG/PNG), and plain text files.</p>

        {/* Drop Zone */}
        <div
          className={`upload-zone${drag ? ' drag-over' : ''}${file ? ' has-file' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
          onDragLeave={() => setDrag(false)}
          onDrop={handleDrop}
          onClick={() => !uploading && fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.jpg,.jpeg,.png,.txt"
            style={{ display: 'none' }}
            onChange={(e) => setFile(e.target.files[0] || null)}
          />
          {file ? (
            <>
              <div className="upload-zone-icon">✅</div>
              <div className="file-selected-name">{file.name}</div>
              <div className="upload-zone-sub">Click to change file</div>
            </>
          ) : (
            <>
              <div className="upload-zone-icon">📄</div>
              <div className="upload-zone-text">Drag & drop your report here</div>
              <div className="upload-zone-sub">or click to browse · PDF, PNG, JPG, TXT</div>
            </>
          )}
        </div>

        {/* Patient info */}
        <div className="upload-form-row">
          <input
            className="upload-form-input"
            placeholder="Patient name (optional)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={uploading}
          />
          <input
            className="upload-form-input"
            placeholder="City (optional)"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            disabled={uploading}
          />
        </div>

        {/* Stage pills during upload */}
        {uploading && (
          <div className="loading-stages">
            {STAGES.map((s, i) => (
              <span
                key={s}
                className={`stage-pill${i === stageIdx ? ' active' : i < stageIdx ? ' done' : ''}`}
              >
                {i < stageIdx ? '✓ ' : ''}{s}…
              </span>
            ))}
          </div>
        )}

        <div className="upload-actions">
          <button className="btn-cancel" onClick={onClose} disabled={uploading}>Cancel</button>
          <button className="btn-primary" onClick={handleSubmit} disabled={!file || uploading}>
            {uploading ? 'Analysing…' : 'Analyse Report'}
          </button>
        </div>
      </div>
    </div>
  );
}
