import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, Loader2, User } from 'lucide-react';
import useHealthStore from '../store/useHealthStore';
import { sendChatMessage } from '../api/client';
import MiniMarkdown from './MiniMarkdown';
import { resolveUserCity } from '../utils/location';

/**
 * Inline chat panel embedded directly on the Dashboard.
 * Passes the current analysisResult as context so the AI always
 * knows what report was uploaded — no DB round-trip needed.
 */
export default function InlineChat() {
  const {
    chatMessages, addChatMessage, setChatMessages,
    isChatLoading, setIsChatLoading,
    sessionId, analysisResult,
  } = useHealthStore();

  const [input, setInput] = useState('');
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // Build context — always read fresh from store (already resolved before send)
  const buildContext = (resolvedCity) => ({
    condition: analysisResult?.condition || null,
    severity: analysisResult?.severity || null,
    summary: analysisResult?.summary || null,
    key_findings: analysisResult?.key_findings || null,
    specialty: analysisResult?.specialty || null,
    location: resolvedCity || null,
  });

  const send = async () => {
    if (!input.trim() || isChatLoading) return;
    const text = input.trim();
    setInput('');
    addChatMessage({ role: 'user', content: text });
    setIsChatLoading(true);

    try {
      // Always resolve location before sending (uses cache after first call)
      const city = await resolveUserCity();
      const response = await sendChatMessage(
        sessionId || 'default',
        text,
        buildContext(city)
      );
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let aiContent = '';
      addChatMessage({ role: 'assistant', content: '' });

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        aiContent += decoder.decode(value, { stream: true });
        setChatMessages((prev) =>
          prev.map((m, i) => (i === prev.length - 1 ? { ...m, content: aiContent } : m))
        );
      }
    } catch {
      addChatMessage({ role: 'assistant', content: 'Could not reach the AI. Is the backend running?' });
    } finally {
      setIsChatLoading(false);
    }
  };

  // Context-aware suggestion chips
  const suggestions = analysisResult
    ? [
        `What is ${analysisResult.condition}?`,
        `Foods to avoid with ${analysisResult.condition}?`,
        `Find a ${analysisResult.specialty || 'doctor'} near me`,
      ]
    : [
        'What can you help me with?',
        'Am I at risk for diabetes?',
        'Tips for better sleep',
      ];

  return (
    <div className="inline-chat">
      {/* Header */}
      <div className="inline-chat-header">
        <Bot size={18} color="var(--teal)" />
        <span>Chat with AI</span>
        {analysisResult ? (
          <span className="inline-chat-context-badge" title={analysisResult.condition}>
            📋 {analysisResult.condition}
          </span>
        ) : (
          <span className="inline-chat-context-badge" style={{ color: 'var(--sub)', borderColor: 'var(--border)', background: 'transparent' }}>
            No report yet
          </span>
        )}
      </div>

      {/* Messages */}
      <div className="inline-chat-messages">
        {chatMessages.length === 0 && (
          <div className="inline-chat-empty">
            <Bot size={28} color="var(--teal)" opacity={0.4} />
            <p>
              {analysisResult
                ? `I have context of your ${analysisResult.condition} report. Ask me anything!`
                : 'Upload a report first, or ask me a general health question.'}
            </p>
            <div className="suggestion-chips">
              {suggestions.map((s, i) => (
                <button key={i} className="suggestion-chip" onClick={() => setInput(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {chatMessages.map((msg, i) => (
          <div key={i} className={`inline-msg inline-msg--${msg.role}`}>
            <div className="inline-msg-avatar">
              {msg.role === 'user' ? <User size={13} /> : <Bot size={13} />}
            </div>
            <div className="inline-msg-bubble">
              {msg.content
                ? msg.role === 'assistant'
                  ? <MiniMarkdown content={msg.content} />
                  : <span>{msg.content}</span>
                : <Loader2 size={13} className="spin" />
              }
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="inline-chat-input-row">
        <input
          className="inline-chat-input"
          placeholder={analysisResult ? `Ask about ${analysisResult.condition}…` : 'Ask a health question…'}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
        />
        <button className="inline-chat-send" onClick={send} disabled={isChatLoading}>
          {isChatLoading ? <Loader2 size={15} className="spin" /> : <Send size={15} />}
        </button>
      </div>
    </div>
  );
}
