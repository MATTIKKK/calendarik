import React, { useState } from 'react';
import './auth-page.css';          // ← подключаем новый CSS
import { LoginForm } from './auth-forms/LoginForm';
import { RegisterForm } from './auth-forms/RegisterForm';

export const AuthPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="auth-container">
      <div className="auth-bg" />   {/* декоративная «сеточка» */}
      <div className="auth-content">
        {isLogin ? (
          <LoginForm onSwitchToRegister={() => setIsLogin(false)} />
        ) : (
          <RegisterForm onSwitchToLogin={() => setIsLogin(true)} />
        )}
      </div>
    </div>
  );
};
