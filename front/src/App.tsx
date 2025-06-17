// App.tsx
import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { AuthPage } from './components/auth/AuthPage';
import { MainLayout } from './pages/layout/MainLayout';
import LandingPage from './pages/landing-page/LandingPage';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const token = localStorage.getItem('accessToken');
  return token ? <>{children}</> : <Navigate to="/login" replace />;
};

const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const token = localStorage.getItem('accessToken');
  // если залогинены, сразу в /app
  return token ? <Navigate to="/app" replace /> : <>{children}</>;
};

const App: React.FC = () => (
  <>
    <Routes>
      {/* Лендинг — только для неавторизованных */}
      <Route
        path="/"
        element={
          <PublicRoute>
            <LandingPage />
          </PublicRoute>
        }
      />
      <Route
        path="/login"
        element={
          <PublicRoute>
            <AuthPage />
          </PublicRoute>
        }
      />

      {/* Всё, что под /app, защищено */}
      <Route
        path="/app/*"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      />

      {/* Фолбэк: всё остальное → на корень */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </>
);

export default App;
