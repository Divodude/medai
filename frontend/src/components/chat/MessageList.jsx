import { useEffect, useRef } from 'react';
import { useApp } from '../../context/AppContext.jsx';
import UserMessage from './UserMessage.jsx';
import AiMessage from './AiMessage.jsx';

export default function MessageList() {
  const { state } = useApp();
  const { messages, analysis } = state;
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="message-list">
        <div className="empty-state">
          <div className="empty-icon">🩺</div>
          <h2>AI Health Assistant</h2>
          <p>Upload a medical report to get your personalised health analysis, diet plan, and more.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="message-list">
      {messages.map((msg, i) =>
        msg.role === 'user'
          ? <UserMessage key={i} message={msg} />
          : <AiMessage   key={i} message={msg} />
      )}
      <div ref={bottomRef} />
    </div>
  );
}
