import SessionSidebar from '../components/sidebar/SessionSidebar.jsx';
import ChatHeader from '../components/chat/ChatHeader.jsx';
import ReportPanel from '../components/report/ReportPanel.jsx';
import MessageList from '../components/chat/MessageList.jsx';
import ChatInput from '../components/chat/ChatInput.jsx';

export default function MainPage() {
  return (
    <div className="app-shell">
      <SessionSidebar />

      <main className="main-area">
        <ChatHeader />
        <ReportPanel />
        <MessageList />
        <ChatInput />
      </main>
    </div>
  );
}
