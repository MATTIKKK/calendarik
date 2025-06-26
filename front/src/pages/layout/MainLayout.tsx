// src/layouts/MainLayout.tsx
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
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import { ChatInterface } from '../../components/chat/chat-interface/ChatInterface';
import { CalendarView } from '../../components/calendar/CalendarView';
import './layout.css';

type ActiveTab = 'chat' | 'calendar' | 'settings';

export const MainLayout: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const { user, logout } = useAuth();

  const menuItems: { id: ActiveTab; icon: React.FC<any>; label: string }[] = [
    { id: 'chat', icon: MessageCircle, label: t('layout.nav.chat') },
    { id: 'calendar', icon: CalendarIcon, label: t('layout.nav.calendar') },
  ];

  return (
    <div className="layout-root">
      {/* Mobile toggle */}
      <button
        onClick={() => setMenuOpen(!menuOpen)}
        className="menu-btn"
        aria-label={menuOpen ? t('layout.nav.closeMenu') : t('layout.nav.openMenu')}
      >
        {menuOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Sidebar */}
      <aside className={`sidebar ${menuOpen ? 'open' : ''}`}>
        {menuOpen && <div className="overlay" onClick={() => setMenuOpen(false)} />}
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

        {/* Navigation */}
        <nav className="nav">
          <ul>
            {menuItems.map(({ id, icon: Icon, label }) => (
              <li key={id}>
                <button
                  onClick={() => {
                    navigate(id);
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
          <button
            onClick={() => { navigate('settings'); setMenuOpen(false); }}
            className="nav-btn"
          >
            <Settings size={20} />
            <span>{t('layout.nav.settings')}</span>
          </button>
          <button onClick={logout} className="nav-btn logout">
            <LogOut size={20} />
            <span>{t('layout.nav.logout')}</span>
          </button>
        </div>
      </aside>

      {/* Main content + nested Routes */}
      <main className="content">
        <Routes>
          <Route index element={<Navigate to="chat" replace />} />
          <Route path="chat" element={<ChatInterface />} />
          <Route path="calendar" element={<CalendarView />} />
          <Route
            path="settings"
            element={
              <div className="settings-card">
                <h2>{t('layout.settings.title')}</h2>
                <div className="settings-grid">
                  <label>
                    {t('layout.settings.name')}
                    <input type="text" value={user?.full_name || ''} readOnly />
                  </label>
                  <label>
                    {t('layout.settings.email')}
                    <input type="email" value={user?.email || ''} readOnly />
                  </label>
                  <label>
                    {t('layout.settings.timezone')}
                    <input type="text" value={user?.timezone || ''} readOnly />
                  </label>
                  <label>
                    {t('layout.settings.gender')}
                    <input type="text" value={user?.gender || ''} readOnly />
                  </label>
                </div>
              </div>
            }
          />
          <Route path="*" element={<Navigate to="chat" replace />} />
        </Routes>
      </main>
    </div>
  );
};
