import React from 'react';
import { Bot } from 'lucide-react';
import './typing-indicator.css';      

export const TypingIndicator: React.FC = () => (
  <div className="typing-row">
    <div className="typing-wrap">
      <div className="avatar assistant">
        <Bot size={20} />
      </div>

      <div className="typing-bubble">
        <span className="dot" style={{ animationDelay: '0ms' }} />
        <span className="dot" style={{ animationDelay: '150ms' }} />
        <span className="dot" style={{ animationDelay: '300ms' }} />
      </div>
    </div>
  </div>
);
