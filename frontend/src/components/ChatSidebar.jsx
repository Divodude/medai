import React, { useState, useRef, useEffect } from 'react';
import { X, Send, Bot, Loader2, MessageCircle, User } from 'lucide-react';
import useHealthStore from '../store/useHealthStore';
import { sendChatMessage } from '../api/client';
import MiniMarkdown from './MiniMarkdown';
import { resolveUserCity } from '../utils/location';

export default function ChatSidebar() {
  const {
    isChatOpen, setIsChatOpen,
    chatMessages, addChatMessage, setChatMessages,
    isChatLoading, setIsChatLoading,
    sessionId, analysisResult,
  } = useHealthStore();

  const [input, setInput] = useState('');
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

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
    const userMsg = { role: 'user', content: input.trim() };
    addChatMessage(userMsg);
    setInput('');
    setIsChatLoading(true);

    try {
      const city = await resolveUserCity();
      const response = await sendChatMessage(
        sessionId || 'default',
        userMsg.content,
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
      addChatMessage({ role: 'assistant', content: '⚠️ Failed to get response. Is the backend running?' });
    } finally {
      setIsChatLoading(false);
    }
  };

  return (
    <>
      <button className="chat-fab" onClick={() => setIsChatOpen(!isChatOpen)}>
        <MessageCircle size={22} />
        {chatMessages.length > 0 && (
          <span className="chat-fab-badge">{chatMessages.length}</span>
        )}
      </button>

      <div className={`chat-sidebar ${isChatOpen ? 'chat-sidebar--open' : ''}`}>
        <div className="chat-header">
          <Bot size={18} />
          <span>AI Health Assistant</span>
          {analysisResult && (
            <span className="inline-chat-context-badge" style={{ fontSize: '0.65rem' }}>
              📋 {analysisResult.condition}
            </span>
          )}
          <button className="chat-close" onClick={() => setIsChatOpen(false)}>
            <X size={16} />
          </button>
        </div>

        <div className="chat-messages">
          {chatMessages.length === 0 && (
            <div className="chat-empty">
              {analysisResult
                ? `Context loaded: ${analysisResult.condition}. Ask me anything!`
                : 'Upload a report or ask me a health question.'}
            </div>
          )}
          {chatMessages.map((msg, i) => (
            <div key={i} className={`chat-msg chat-msg--${msg.role}`}>
              {msg.content
                ? msg.role === 'assistant'
                  ? <MiniMarkdown content={msg.content} />
                  : <p>{msg.content}</p>
                : <Loader2 size={14} className="spin" />
              }
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        <div className="chat-input-row">
          <input
            className="chat-input"
            placeholder={analysisResult ? `Ask about ${analysisResult.condition}…` : 'Ask about your health…'}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send()}
          />
          <button className="chat-send" onClick={send} disabled={isChatLoading}>
            {isChatLoading ? <Loader2 size={16} className="spin" /> : <Send size={16} />}
          </button>
        </div>
      </div>
    </>
  );
}
