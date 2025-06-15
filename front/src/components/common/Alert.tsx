import React from 'react';
import { AlertCircle, CheckCircle2, XCircle } from 'lucide-react';
import './Alert.css';

export type AlertType = 'success' | 'error' | 'info';

interface AlertProps {
  type: AlertType;
  message: string;
  onClose?: () => void;
}

export const Alert: React.FC<AlertProps> = ({ type, message, onClose }) => {
  const icons = {
    success: <CheckCircle2 className="alert-icon success" />,
    error: <XCircle className="alert-icon error" />,
    info: <AlertCircle className="alert-icon info" />,
  };

  return (
    <div className={`alert alert-${type}`}>
      {icons[type]}
      <span className="alert-message">{message}</span>
      {onClose && (
        <button onClick={onClose} className="alert-close">
          ×
        </button>
      )}
    </div>
  );
};
