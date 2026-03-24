import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import ChatSidebar from './components/ChatSidebar';
import { Activity, History as HistIcon } from 'lucide-react';
import './App.css';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <nav className="topnav">
          <div className="topnav-brand">
            <Activity size={22} color="var(--teal)" />
            <span>HealthAI</span>
          </div>
          <div className="topnav-links">
            <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'nav-link--active' : ''}`}>
              Dashboard
            </NavLink>
            <NavLink to="/history" className={({ isActive }) => `nav-link ${isActive ? 'nav-link--active' : ''}`}>
              <HistIcon size={15} /> History
            </NavLink>
          </div>
        </nav>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </main>
        <ChatSidebar />
      </div>
    </BrowserRouter>
  );
}
