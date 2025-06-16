import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Bot,
  Calendar,
  Clock,
  AlertTriangle,
  Mic,
  MicOff,
} from 'lucide-react';
import { Message, AssistantPersonality } from '../../../types';
import { Chat } from '../../../types/chat';
// import { chatService } from '../../../services/chatService';
import { MessageBubble } from '../message-bubble/MessageBubble';
import { TypingIndicator } from '../typing-indicator/TypingIndicator';
import './chat-interface.css';
import axios from 'axios';
import { useAuth } from '../../../contexts/AuthContext';

export const personalities: AssistantPersonality[] = [
  {
    id: 'assistant',
    name: 'Professional Assistant',
    description: 'Formal…',
    tone: 'assistant',
    avatar: '💼',
  },
  {
    id: 'coach',
    name: 'Motivational Coach',
    description: 'Energetic…',
    tone: 'coach',
    avatar: '💪',
  },
  {
    id: 'friend',
    name: 'Best Friend',
    description: 'Casual…',
    tone: 'friend',
    avatar: '👥',
  },
  {
    id: 'girlfriend',
    name: 'Caring Girlfriend',
    description: 'Sweet…',
    tone: 'girlfriend',
    avatar: '💕',
  },
  {
    id: 'boyfriend',
    name: 'Supportive Boyfriend',
    description: 'Protective…',
    tone: 'boyfriend',
    avatar: '❤️',
  },
];

/* быстрые ответы */
const quickMessages = [
  'Schedule a meeting',
  "What's my schedule today?",
  'Find free time this week',
  'Cancel my 3pm appointment',
];

interface ChatInterfaceProps {
  initialChatId?: number;
  onChatCreated?: (chat: Chat) => void;
}

const updateUserPersonality = async (personalityId: string) => {
  const token = localStorage.getItem('accessToken');
  if (!token) return;

  try {
    await axios.put(
      'http://localhost:8000/api/auth/me/personality',
      { personality: personalityId },
      { headers: { Authorization: `Bearer ${token}` } }
    );
  } catch (error) {
    console.error('Failed to update personality:', error);
  }
};

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  initialChatId,
  onChatCreated,
}) => {
  /* — state — */
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentChatId, setCurrentChatId] = useState<number | undefined>(
    initialChatId
  );
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [personality, setPersonality] = useState<AssistantPersonality>(
    personalities[0]
  );
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(
    null
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user } = useAuth();

  /* — прокрутка вниз — */
  useEffect(() => {
    if (initialChatId) {
      loadChat(initialChatId);
    }
  }, [initialChatId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  /* — отправка текста — */
  const loadChat = async (chatId: number) => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/chat/${chatId}/messages`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
          },
        }
      );

      const formattedMessages = response.data.map((msg: any) => ({
        id: msg.id.toString(),
        content: msg.content,
        sender: msg.role,
        timestamp: new Date(msg.created_at),
      }));

      setMessages(formattedMessages);
      setCurrentChatId(chatId);
    } catch (error) {
      console.error('Failed to load chat:', error);
    }
  };

  const send = async (text?: string) => {
    const content = text ?? inputMessage;
    if (!content.trim() || isTyping) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      content,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const response = await axios.post(
        'http://localhost:8000/api/ai/analyze',
        {
          message: content,
          chat_id: currentChatId,
          personality: personality.id,
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
          },
        }
      );

      if (!currentChatId && response.data.chat_id) {
        setCurrentChatId(response.data.chat_id);
        if (onChatCreated) {
          const chatResponse = await axios.get(
            `http://localhost:8000/api/chat/${response.data.chat_id}`,
            {
              headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
              },
            }
          );
          onChatCreated(chatResponse.data);
        }
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.data.message,
        sender: 'assistant',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsTyping(false);
    }
  };

  /* — горячая клавиша Enter — */
  const keyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  /* — микрофон — */
  const startRec = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream);
      rec.ondataavailable = (e) => {
        if (e.data.size) {
          setTimeout(() => {
            setInputMessage('This is a simulated voice message transcription');
            setIsRecording(false);
          }, 2000);
        }
      };
      rec.start();
      setMediaRecorder(rec);
      setIsRecording(true);
    } catch {
      alert('Unable to access microphone. Check permissions.');
    }
  };

  const stopRec = () => {
    mediaRecorder?.stop();
    mediaRecorder?.stream.getTracks().forEach((t) => t.stop());
    setMediaRecorder(null);
    setIsRecording(false);
  };

  const handlePersonalityChange = async (personalityId: string) => {
    const next = personalities.find((p) => p.id === personalityId)!;
    setPersonality(next);
    await updateUserPersonality(personalityId);
  };

  /* — JSX — */
  return (
    <div className="chat-root">
      {/* header */}
      <header className="chat-header">
        <div className="chat-header-left">
          <div className="chat-avatar">
            <Bot size={24} />
          </div>
          <div>
            <h3 className="chat-title">Bro</h3>
            {/* <p className="chat-subtitle">
              {personality
                ? personality.name
                : 'Your personal planning companion'}
            </p> */}
          </div>
        </div>

        <select
          className="pers-select"
          value={user?.chat_personality}
          onChange={(e) => handlePersonalityChange(e.target.value)}
        >
          {personalities.map((p) => (
            <option key={p.id} value={p.id}>
              {p.avatar} {p.name}
            </option>
          ))}
        </select>
      </header>

      {/* сообщения */}
      <main className="chat-messages">
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
        {isTyping && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </main>

      {/* быстрые ответы */}
      <section className="chat-quick">
        {quickMessages.map((msg, i) => (
          <button key={i} onClick={() => send(msg)} className="quick-btn">
            {msg}
          </button>
        ))}
      </section>

      {/* ввод */}
      <footer className="chat-input-wrap">
        <div className="chat-textarea-block">
          <textarea
            rows={2}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={keyPress}
            placeholder="Tell me about your plans, tasks, or deadlines…"
            className="chat-textarea"
          />
          <button
            onClick={isRecording ? stopRec : startRec}
            className={`mic-btn ${isRecording ? 'recording' : ''}`}
          >
            {isRecording ? <MicOff size={16} /> : <Mic size={16} />}
          </button>
        </div>

        <button
          onClick={() => send()}
          disabled={!inputMessage.trim() || isTyping}
          className="send-btn"
        >
          <Send size={20} />
        </button>
      </footer>

      {/* нижние бейджи */}
      <div className="chat-badges">
        <span>
          <Calendar size={14} /> Calendar Integration
        </span>
        <span>
          <Clock size={14} /> Smart Scheduling
        </span>
        <span>
          <AlertTriangle size={14} /> Deadline Management
        </span>
      </div>
    </div>
  );
};
