export default function UserMessage({ message }) {
  return (
    <div className="message-row">
      <div className="msg-avatar user">👤</div>
      <div className="msg-body">
        <div className="msg-role">You</div>
        <div className="msg-content">{message.content}</div>
      </div>
    </div>
  );
}
