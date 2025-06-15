import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AuthPage } from './components/auth/AuthPage';
import { MainLayout } from './components/layout/MainLayout';
import './app.css'; // подключаем общие стили

// Компонент для защищенных роутов
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { user } = useAuth();
  const token = localStorage.getItem('accessToken');

  if (!token || !user) {
    // Если нет токена или пользователя, редиректим на страницу логина
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Компонент для публичных роутов (доступных только неавторизованным)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  const token = localStorage.getItem('accessToken');

  if (token && user) {
    // Если пользователь авторизован, редиректим на главную
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

const AppContent: React.FC = () => {
  return (
    <Routes>
      {/* Публичные роуты */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <AuthPage />
          </PublicRoute>
        }
      />

      {/* Защищенные роуты */}
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
};

export default App;
