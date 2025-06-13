import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AuthPage } from './components/auth/AuthPage';
import { MainLayout } from './components/layout/MainLayout';
import './app.css'; // подключаем общие стили

const AppContent: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="app-loading">
        <div className="loader-wrapper">
          <div className="loader-outer">
            <div className="loader-inner" />
          </div>
          <p className="loading-text">Loading your AI assistant...</p>
        </div>
      </div>
    );
  }

  return user ? (
    <Router>
      <Routes>
        <Route path="/*" element={<MainLayout />} />
      </Routes>
    </Router>
  ) : (
    <AuthPage />
  );
};

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
