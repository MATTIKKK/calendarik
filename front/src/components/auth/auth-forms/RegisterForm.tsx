// src/components/auth/RegisterForm.tsx
import React, { useState, useEffect } from 'react';
import {
  Mail,
  Lock,
  User,
  Globe,
  Eye,
  EyeOff,
  UserPlus,
  Globe as LanguageIcon,
} from 'lucide-react';
import './auth-forms.css';
import { RegisterData } from '../../../types/auth';
import { useAuth } from '../../../contexts/AuthContext';
import moment from 'moment-timezone';
import { Alert } from '../../alert/Alert';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const timezones = moment.tz.names().sort();

export const RegisterForm: React.FC<{
  onSwitchToLogin: () => void;
}> = ({ onSwitchToLogin }) => {
  const { t, i18n } = useTranslation();
  const [formData, setFormData] = useState<RegisterData>({
    email: '',
    password: '',
    full_name: '',
    preferred_language: i18n.language,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    gender: 'male',
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [alert, setAlert] = useState<{
    type: 'success' | 'error';
    message: string;
  } | null>(null);
  const { register, loading } = useAuth();
  const navigate = useNavigate();

  const update = (field: keyof RegisterData, value: string) =>
    setFormData((p) => ({ ...p, [field]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAlert(null);

    if (formData.password !== confirmPassword) {
      setAlert({
        type: 'error',
        message: t('auth.register.alerts.passwordMismatch'),
      });
      return;
    }
    if (formData.password.length < 6) {
      setAlert({
        type: 'error',
        message: t('auth.register.alerts.passwordTooShort'),
      });
      return;
    }
    try {
      await register(formData);
      setAlert({
        type: 'success',
        message: t('auth.register.alerts.registrationSuccess'),
      });
      setTimeout(() => navigate('/'), 1500);
    } catch {
      setAlert({
        type: 'error',
        message: t('auth.register.alerts.registrationFailed'),
      });
    }
  };

  useEffect(() => {
    const saved = localStorage.getItem('lang');
    if (saved && saved !== i18n.language) {
      i18n.changeLanguage(saved);
      update('preferred_language', saved);
    }
  }, []);

  return (
    <div className="form-wrapper">
      <div className="form-card relative">
        <header className="form-header">
          <div className="form-icon-wrap">
            <UserPlus size={32} color="#fff" />
          </div>
          <h2 className="form-title">{t('auth.register.title')}</h2>
          <p className="form-subtitle">{t('auth.register.subtitle')}</p>
        </header>

        {alert && (
          <Alert
            type={alert.type}
            message={alert.message}
            onClose={() => setAlert(null)}
          />
        )}

        <form onSubmit={handleSubmit} className="form-body">
          {/* Full Name */}
          <div className="form-field">
            <label className="form-label">{t('auth.register.fullName')}</label>
            <div className="input-group">
              <User className="input-icon-left" size={20} />
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => update('full_name', e.target.value)}
                className="form-input with-left-icon"
                placeholder={t('auth.register.placeholders.fullName')}
                required
              />
            </div>
          </div>

          {/* Email */}
          <div className="form-field">
            <label className="form-label">{t('auth.register.email')}</label>
            <div className="input-group">
              <Mail className="input-icon-left" size={20} />
              <input
                type="email"
                value={formData.email}
                onChange={(e) => update('email', e.target.value)}
                className="form-input with-left-icon"
                placeholder={t('auth.register.placeholders.email')}
                required
              />
            </div>
          </div>

          {/* Timezone & Gender */}
          <div className="two-col-grid">
            <div className="form-field">
              <label className="form-label">{t('language.select')}</label>
              <div className="input-group">
                <LanguageIcon className="input-icon-left" size={20} />
                <select
                  value={formData.preferred_language}
                  onChange={(e) => {
                    const lang = e.target.value;
                    i18n.changeLanguage(lang); // меняем язык сразу
                    localStorage.setItem('lang', lang);
                    update('preferred_language', lang);
                  }}
                  className="form-select with-left-icon"
                >
                  <option value="en">{t('language.en')}</option>
                  <option value="ru">{t('language.ru')}</option>
                  <option value="kz">{t('language.kz')}</option>
                </select>
              </div>
            </div>

            <div className="form-field">
              <label className="form-label">{t('auth.register.gender')}</label>
              <select
                value={formData.gender}
                onChange={(e) => update('gender', e.target.value)}
                className="form-select"
              >
                <option value="male">
                  {t('auth.register.genderMale', 'Male')}
                </option>
                <option value="female">
                  {t('auth.register.genderFemale', 'Female')}
                </option>
                <option value="other">
                  {t('auth.register.genderOther', 'Other')}
                </option>
              </select>
            </div>
          </div>

          <div className="form-field">
            <label className="form-label">{t('auth.register.timezone')}</label>
            <div className="input-group">
              <Globe className="input-icon-left" size={20} />
              <select
                value={formData.timezone}
                onChange={(e) => update('timezone', e.target.value)}
                className="form-select with-left-icon"
              >
                {timezones.map((tz) => (
                  <option key={tz} value={tz}>
                    {tz}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Password */}
          <div className="form-field">
            <label className="form-label">{t('auth.register.password')}</label>
            <div className="input-group">
              <Lock className="input-icon-left" size={20} />
              <input
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={(e) => update('password', e.target.value)}
                className="form-input with-left-icon with-right-button"
                placeholder={t('auth.register.placeholders.password')}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="toggle-password-button"
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          {/* Confirm Password */}
          <div className="form-field">
            <label className="form-label">
              {t('auth.register.confirmPassword')}
            </label>
            <div className="input-group">
              <Lock className="input-icon-left" size={20} />
              <input
                type={showPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="form-input with-left-icon"
                placeholder={t('auth.register.placeholders.confirmPassword')}
                required
              />
            </div>
          </div>

          <button type="submit" disabled={loading} className="submit-button">
            {loading ? (
              <>
                <span className="spinner" />{' '}
                {t('auth.register.buttons.createAccount')}
              </>
            ) : (
              t('auth.register.buttons.createAccount')
            )}
          </button>
        </form>

        <footer className="form-footer">
          <span>{t('auth.register.haveAccount')} </span>
          <button onClick={onSwitchToLogin} className="link-button">
            {t('auth.register.buttons.signIn')}
          </button>
        </footer>
      </div>
    </div>
  );
};
