import { useState, useRef } from 'react';
import { useApp } from '../../context/AppContext.jsx';
import { sendChat, analyzeReport } from '../../api/api.js';
import UploadModal from './UploadModal.jsx';

export default function ChatInput() {
  const { state, dispatch } = useApp();
  const [text, setText] = useState('');
  const [showUpload, setShowUpload] = useState(false);
  const [sending, setSending] = useState(false);
  const textareaRef = useRef(null);

  const canSend = text.trim().length > 0 && !sending && !state.loading;
  const hasSession = !!state.sessionId;

  async function handleSend() {
    if (!canSend) return;
    if (!hasSession) {
      setShowUpload(true);
      return;
    }

    const msg = text.trim();
    setText('');
    setSending(true);
    textareaRef.current?.focus();

    dispatch({ type: 'ADD_MESSAGE', payload: { role: 'user', content: msg } });
    dispatch({ type: 'ADD_MESSAGE', payload: { role: 'ai', content: '', streaming: true } });

    try {
      await sendChat(state.sessionId, msg, (chunk) => {
        dispatch({ type: 'APPEND_AI_CHUNK', payload: chunk });
      });
    } catch (e) {
      dispatch({ type: 'APPEND_AI_CHUNK', payload: `\n\n⚠️ Error: ${e.message}` });
    } finally {
      dispatch({ type: 'FINISH_STREAM' });
      setSending(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleTextareaInput(e) {
    setText(e.target.value);
    // Auto-resize
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 160) + 'px';
  }

  return (
    <>
      <div className="chat-input-area">
        <div className="chat-input-box">
          <button
            className="btn-upload-trigger"
            onClick={() => setShowUpload(true)}
            title="Upload a medical report"
          >
            📎
          </button>

          <textarea
            ref={textareaRef}
            className="chat-textarea"
            placeholder={hasSession ? 'Ask me anything about your report…' : 'Upload a report first, or type a message…'}
            rows={1}
            value={text}
            onChange={handleTextareaInput}
            onKeyDown={handleKeyDown}
            disabled={sending || state.loading}
          />

          <button
            className="btn-send"
            onClick={handleSend}
            disabled={!canSend}
            title="Send (Enter)"
          >
            ↑
          </button>
        </div>
        <div className="chat-input-hint">
          Press Enter to send · Shift+Enter for new line · 📎 to upload report
        </div>
      </div>

      {showUpload && (
        <UploadModal onClose={() => setShowUpload(false)} />
      )}
    </>
  );
}
