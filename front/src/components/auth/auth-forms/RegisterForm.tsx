import React, { useState } from 'react';
import { Mail, Lock, User, Globe, Eye, EyeOff, UserPlus } from 'lucide-react';
import './auth-forms.css';
import { RegisterData } from '../../../types';
import { useAuth } from '../../../contexts/AuthContext';
import moment from 'moment-timezone';
import { Alert } from '../../common/alert/Alert';
import { useNavigate } from 'react-router-dom';
import { ITimezoneOption } from 'react-timezone-select';

interface RegisterFormProps {
  onSwitchToLogin: () => void;
}

const timezones = moment.tz.names().sort();

export const RegisterForm: React.FC<RegisterFormProps> = ({
  onSwitchToLogin,
}) => {
  const [formData, setFormData] = useState<RegisterData>({
    email: '',
    password: '',
    full_name: '',
    timezone: 'UTC',
    gender: 'other',
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
    setFormData((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAlert(null);

    if (formData.password !== confirmPassword) {
      setAlert({ type: 'error', message: 'Passwords do not match' });
      return;
    }
    if (formData.password.length < 6) {
      setAlert({
        type: 'error',
        message: 'Password must be at least 6 characters long',
      });
      return;
    }
    try {
      await register(formData);
      setAlert({
        type: 'success',
        message: 'Registration successful! Redirecting...',
      });
      setTimeout(() => {
        navigate('/');
      }, 1500);
    } catch {
      setAlert({
        type: 'error',
        message: 'Registration failed. Please try again.',
      });
    }
  };

  return (
    <div className="form-wrapper">
      <div className="form-card">
        <header className="form-header">
          <div className="form-icon-wrap">
            <UserPlus size={32} color="#fff" />
          </div>
          <h2 className="form-title">Join Us</h2>
          <p className="form-subtitle">Create your account to get started</p>
        </header>

        {alert && (
          <Alert
            type={alert.type}
            message={alert.message}
            onClose={() => setAlert(null)}
          />
        )}

        <form onSubmit={handleSubmit} className="form-body">
          <div className="form-field">
            <label className="form-label">Full Name</label>
            <div className="input-group">
              <User className="input-icon-left" size={20} />
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => update('full_name', e.target.value)}
                className="form-input with-left-icon"
                placeholder="Enter your full name"
                required
              />
            </div>
          </div>

          <div className="form-field">
            <label className="form-label">Email Address</label>
            <div className="input-group">
              <Mail className="input-icon-left" size={20} />
              <input
                type="email"
                value={formData.email}
                onChange={(e) => update('email', e.target.value)}
                className="form-input with-left-icon"
                placeholder="Enter your email"
                required
              />
            </div>
          </div>

          <div className="two-col-grid">
            <div className="form-field">
              <label className="form-label">Timezone</label>
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

            <div className="form-field">
              <label className="form-label">Gender</label>
              <select
                value={formData.gender}
                onChange={(e) => update('gender', e.target.value)}
                className="form-select"
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>

          <div className="form-field">
            <label className="form-label">Password</label>
            <div className="input-group">
              <Lock className="input-icon-left" size={20} />
              <input
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={(e) => update('password', e.target.value)}
                className="form-input with-left-icon with-right-button"
                placeholder="Create a password"
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

          <div className="form-field">
            <label className="form-label">Confirm Password</label>
            <div className="input-group">
              <Lock className="input-icon-left" size={20} />
              <input
                type={showPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="form-input with-left-icon"
                placeholder="Confirm your password"
                required
              />
            </div>
          </div>

          <button type="submit" disabled={loading} className="submit-button">
            {loading ? (
              <>
                <span className="spinner" /> Creating Account…
              </>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        <footer className="form-footer">
          <span>Already have an account? </span>
          <button onClick={onSwitchToLogin} className="link-button">
            Sign in
          </button>
        </footer>
      </div>
    </div>
  );
};
