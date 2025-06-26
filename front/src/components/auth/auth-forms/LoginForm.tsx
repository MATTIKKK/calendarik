// src/components/auth/LoginForm.tsx
import React, { useState } from 'react';
import { Mail, Lock, Eye, EyeOff, LogIn } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import './auth-forms.css';
import { useAuth } from '../../../contexts/AuthContext';
import { Alert } from '../../alert/Alert';
import { useNavigate } from 'react-router-dom';



interface LoginFormProps {
  onSwitchToRegister: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSwitchToRegister }) => {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [alert, setAlert] = useState<{
    type: 'success' | 'error';
    message: string;
  } | null>(null);
  const { login, loading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAlert(null);
    try {
      await login(email, password);
      setAlert({
        type: 'success',
        message: t('auth.login.alerts.success'),
      });
      setTimeout(() => {
        navigate('/');
      }, 1500);
    } catch {
      setAlert({
        type: 'error',
        message: t('auth.login.alerts.error'),
      });
    }
  };

  return (
    <div className="form-wrapper relative">

      <div className="form-card">
        <header className="form-header">
          <div className="form-icon-wrap">
            <LogIn size={32} color="#fff" />
          </div>
          <h2 className="form-title">{t('auth.login.title')}</h2>
          <p className="form-subtitle">{t('auth.login.subtitle')}</p>
        </header>

        {alert && (
          <Alert
            type={alert.type}
            message={alert.message}
            onClose={() => setAlert(null)}
          />
        )}

        <form onSubmit={handleSubmit} className="form-body">
          {/* Email */}
          <div className="form-field">
            <label className="form-label">{t('auth.login.emailLabel')}</label>
            <div className="input-group">
              <Mail className="input-icon-left" size={20} />
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="form-input with-left-icon"
                placeholder={t('auth.login.placeholders.email')}
                autoComplete="email"
                required
              />
            </div>
          </div>

          {/* Password */}
          <div className="form-field">
            <label className="form-label">{t('auth.login.passwordLabel')}</label>
            <div className="input-group">
              <Lock className="input-icon-left" size={20} />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="form-input with-left-icon with-right-button"
                placeholder={t('auth.login.placeholders.password')}
                autoComplete="current-password"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(v => !v)}
                className="toggle-password-button"
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="submit-button"
          >
            {loading
              ? <>
                  <span className="spinner" /> {t('auth.login.buttons.signIn')}…
                </>
              : t('auth.login.buttons.signIn')
            }
          </button>
        </form>

        {/* Footer */}
        <footer className="form-footer">
          <span>{t('auth.login.footer')} </span>
          <button
            onClick={onSwitchToRegister}
            className="link-button"
          >
            {t('auth.login.buttons.signUp')}
          </button>
        </footer>
      </div>
    </div>
  );
};
