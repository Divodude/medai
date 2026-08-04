function timeAgo(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins  = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days  = Math.floor(diff / 86400000);
  if (mins  < 1)  return 'just now';
  if (mins  < 60) return `${mins}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return `${days}d ago`;
}

export default function SessionItem({ session, active, onClick }) {
  return (
    <li className={`session-item${active ? ' active' : ''}`} onClick={onClick}>
      <span className="session-item-name">
        {session.patient_name || 'Patient'}
      </span>
      <span className="session-item-time">
        {timeAgo(session.created_at)}
      </span>
    </li>
  );
}
