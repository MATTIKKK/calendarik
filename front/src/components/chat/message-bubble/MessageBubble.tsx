import React from 'react';
import { Bot, User } from 'lucide-react';
import { Message } from '../../../types/message';
import './message-bubble.css';          // ← подключаем тот же CSS, где лежат стили чата

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.sender === 'user';

  return (
    <div className={`bubble-row ${isUser ? 'user' : 'assistant'}`} style={{ whiteSpace: "pre-line" }}   >
      <div className={`bubble-wrap ${isUser ? 'user' : 'assistant'}`}>
        {/* аватар */}
        <div className={`avatar ${isUser ? 'user' : 'assistant'}`}>
          {isUser ? <User size={20} /> : <Bot size={20} />}
        </div>

        {/* пузырь */}
        <div className={`bubble ${isUser ? 'user' : 'assistant'}`}>
          <p>{message.content}</p>
          <p className={`time ${isUser ? 'user' : 'assistant'}`}>
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>
      </div>
    </div>
  );
};
