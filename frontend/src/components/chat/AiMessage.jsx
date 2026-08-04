export default function AiMessage({ message }) {
  return (
    <div className="message-row">
      <div className="msg-avatar ai">🤖</div>
      <div className="msg-body">
        <div className="msg-role">MedAI</div>
        <div className="msg-content">
          {message.content}
          {message.streaming && <span className="msg-cursor" />}
        </div>
      </div>
    </div>
  );
}
