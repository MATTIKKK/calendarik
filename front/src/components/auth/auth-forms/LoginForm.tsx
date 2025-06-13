import React, { useState } from 'react';
import { Mail, Lock, Eye, EyeOff, LogIn } from 'lucide-react';
import './auth-forms.css';
import { useAuth } from '../../../contexts/AuthContext';

interface LoginFormProps {
  onSwitchToRegister: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSwitchToRegister }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const { login, loading } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login(email, password);
    } catch {
      setError('Invalid email or password');
    }
  };

  return (
    <div className="form-wrapper">
      <div className="form-card">
        <header className="form-header">
          <div className="form-icon-wrap">
            <LogIn size={32} color="#fff" />
          </div>
          <h2 className="form-title">Welcome Back</h2>
          <p className="form-subtitle">Sign in to continue with your AI assistant</p>
        </header>

        <form onSubmit={handleSubmit} className="form-body">
          <div className="form-field">
            <label className="form-label">Email Address</label>
            <div className="input-group">
              <Mail className="input-icon-left" size={20} />
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="form-input with-left-icon"
                placeholder="Enter your email"
                required
              />
            </div>
          </div>

          <div className="form-field">
            <label className="form-label">Password</label>
            <div className="input-group">
              <Lock className="input-icon-left" size={20} />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="form-input with-left-icon with-right-button"
                placeholder="Enter your password"
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

          {error && <div className="form-error">{error}</div>}

          <button type="submit" disabled={loading} className="submit-button">
            {loading ? (
              <>
                <span className="spinner" /> Signing In…
              </>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <footer className="form-footer">
          <span>Don’t have an account? </span>
          <button onClick={onSwitchToRegister} className="link-button">
            Sign up
          </button>
        </footer>
      </div>
    </div>
  );
};
