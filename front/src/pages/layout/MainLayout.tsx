// MainLayout.tsx
import React, { useState } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import {
  MessageCircle,
  Calendar as CalendarIcon,
  Settings,
  LogOut,
  Menu,
  X,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { ChatInterface } from '../../components/chat/chat-interface/ChatInterface';
import { CalendarView } from '../../components/calendar/CalendarView';
import './layout.css';

type ActiveTab = 'chat' | 'calendar' | 'settings';

export const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const { user, logout } = useAuth();

  const menuItems = [
    { id: 'chat' as ActiveTab, icon: MessageCircle, label: 'Chat' },
    { id: 'calendar' as ActiveTab, icon: CalendarIcon, label: 'Calendar' },
  ];

  return (
    <div className="layout-root">
      {/* Mobile toggle */}
      <button onClick={() => setMenuOpen(!menuOpen)} className="menu-btn">
        {menuOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Sidebar */}
      <aside className={`sidebar ${menuOpen ? 'open' : ''}`}>
        {menuOpen && (
          <div className="overlay" onClick={() => setMenuOpen(false)} />
        )}
        {/* Profile */}
        <section className="profile">
          <div className="avatar-lg">
            {user?.full_name?.charAt(0).toUpperCase()}
          </div>
          <div className="profile-info">
            <h3>{user?.full_name}</h3>
            <p>{user?.email}</p>
          </div>
        </section>

        {/* Навигация */}
        <nav className="nav">
          <ul>
            {menuItems.map(({ id, icon: Icon, label }) => (
              <li key={id}>
                <button
                  onClick={() => {
                    navigate(id); // навигация в /app/chat или /app/calendar
                    setMenuOpen(false);
                  }}
                  className={`nav-btn ${
                    window.location.pathname.endsWith(id) ? 'active' : ''
                  }`}
                >
                  <Icon size={20} />
                  <span>{label}</span>
                </button>
              </li>
            ))}
          </ul>
        </nav>

        {/* Footer */}
        <div className="sidebar-footer">
          <button onClick={() => navigate('settings')} className="nav-btn">
            <Settings size={20} />
            <span>Settings</span>
          </button>
          <button onClick={logout} className="nav-btn logout">
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Основной контент + вложенные Routes */}
      <main className="content">
        <Routes>
          {/* при заходе на /app → редиректим в чат */}
          <Route index element={<Navigate to="chat" replace />} />

          {/* собственно вкладки */}
          <Route path="chat" element={<ChatInterface />} />
          <Route path="calendar" element={<CalendarView />} />
          <Route
            path="settings"
            element={
              <div className="settings-card">
                <h2>Settings</h2>
                <div className="settings-grid">
                  <label>
                    Name
                    <input type="text" value={user?.full_name || ''} readOnly />
                  </label>
                  <label>
                    Email
                    <input type="email" value={user?.email || ''} readOnly />
                  </label>
                  <label>
                    Timezone
                    <input type="text" value={user?.timezone || ''} readOnly />
                  </label>
                  <label>
                    Gender
                    <input type="text" value={user?.gender || ''} readOnly />
                  </label>
                </div>
              </div>
            }
          />

          {/* всё что не найдено → обратно в чат */}
          <Route path="*" element={<Navigate to="chat" replace />} />
        </Routes>
      </main>
    </div>
  );
};
