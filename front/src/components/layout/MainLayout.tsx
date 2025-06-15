import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import {
  MessageCircle, Calendar as CalendarIcon,
  Settings, LogOut, Menu, X,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { ChatInterface } from '../chat/chat-interface/ChatInterface';
import { CalendarView } from '../calendar/CalendarView';
import './layout.css';

type ActiveTab = 'chat' | 'calendar' | 'settings';

export const MainLayout: React.FC = () => {
  const [activeTab, setActiveTab]   = useState<ActiveTab>('chat');
  const [menuOpen,  setMenuOpen]    = useState(false);
  const { user, logout }            = useAuth();

  const menuItems = [
    { id: 'chat' as ActiveTab,     icon: MessageCircle, label: 'Chat',     count: null },
    { id: 'calendar' as ActiveTab, icon: CalendarIcon, label: 'Calendar', count: 3    },
  ];

  const changeTab = (tab: ActiveTab) => {
    setActiveTab(tab);
    setMenuOpen(false);
  };

  return (
    <div className="layout-root">
      {/* Mobile toggle */}
      <button onClick={() => setMenuOpen(!menuOpen)} className="menu-btn">
        {menuOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Sidebar */}
      <aside className={`sidebar ${menuOpen ? 'open' : ''}`}>
        {menuOpen && <div className="overlay" onClick={() => setMenuOpen(false)} />}

        {/* profile */}
        <section className="profile">
          <div className="avatar-lg">
            {user?.full_name?.charAt(0).toUpperCase()}
          </div>
          <div className="profile-info">
            <h3>{user?.full_name}</h3>
            <p>{user?.email}</p>
          </div>
        </section>

        {/* nav */}
        <nav className="nav">
          <ul>
            {menuItems.map(({ id, icon: Icon, label, count }) => (
              <li key={id}>
                <button
                  onClick={() => changeTab(id)}
                  className={`nav-btn ${activeTab === id ? 'active' : ''}`}
                >
                  <Icon size={20} />
                  <span>{label}</span>
                  {count && <span className="badge">{count}</span>}
                </button>
              </li>
            ))}
          </ul>
        </nav>

        {/* footer */}
        <div className="sidebar-footer">
          <button onClick={() => changeTab('settings')} className="nav-btn">
            <Settings size={20} />
            <span>Settings</span>
          </button>
          <button onClick={logout} className="nav-btn logout">
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* content */}
      <main className="content">
        <Routes>
          <Route
            path="/"
            element={
              <>
                {activeTab === 'chat'      && <ChatInterface />}
                {activeTab === 'calendar'  && <CalendarView />}
                {activeTab === 'settings'  && (
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
                )}
              </>
            }
          />
        </Routes>
      </main>
    </div>
  );
};
