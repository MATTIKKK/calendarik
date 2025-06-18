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
  onChatCreated?: (chat: Chat) => void;
}
interface ChatMessageDTO {
  id: number;
  content: string;
  role: string;
  created_at: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = () => {
  const { token, user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [personality, setPersonality] = useState<AssistantPersonality>(
    personalities.find((p) => p.id === user?.chat_personality) ?? personalities[0]
  );
  const [chatId, setChatId] = useState<number | null>(user?.chat_id ?? null);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(
    null
  );
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!token || chatId === null) return;

    (async () => {
      console.log('chatId', chatId);
      try {
        const { data } = await axios.get<ChatMessageDTO[]>(
          `http://128.251.224.196:8000/api/chat/${chatId}/messages`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setMessages(
          data
            .slice()
            .reverse()
            .map((m) => ({
              id: m.id.toString(),
              content: m.content,
              sender: m.role === 'assistant' ? 'assistant' : 'user',
              timestamp: new Date(m.created_at),
            }))
        );
      } catch (err) {
        console.error('Failed to load history', err);
      }
    })();
  }, [chatId, token]);

  /* -------- 2. автоскролл -------- */
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  /* -------- 3. отправка сообщения -------- */
  const send = async (text?: string) => {
    if (!token || isTyping) return;
    const content = (text ?? inputMessage).trim();
    if (!content) return;

    // оптимистично показываем
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        content,
        sender: 'user',
        timestamp: new Date(),
      },
    ]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const { data } = await axios.post(
        'http://128.251.224.196:8000/api/chat/message',
        {
          message: content,
          personality: personality.id,
          chat_id: chatId ?? undefined,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // если это первое сообщение — запоминаем chatId
      if (chatId === null) setChatId(data.chat_id);

      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          content: data.message,
          sender: 'assistant',
          timestamp: new Date(),
        },
      ]);
    } catch (err) {
      console.error('Failed to send message', err);
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
    if (!token) return;

    const next = personalities.find((p) => p.id === personalityId)!;
    setPersonality(next);
    try {
      await axios.put(
        'http://128.251.224.196:8000/api/auth/me/personality',
        { personality: personalityId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
    } catch (error) {
      console.error('Failed to update personality:', error);
    }
  };

  useEffect(() => {
    if (!token) return;
  
    axios
      .get<{ id: number }>('http://128.251.224.196:8000/api/chat/me', {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then(({ data }) => {
        setChatId(data.id);
        console.log('chatId in useEffect', data.id);
      })
      .catch(console.error);
  }, [token]);

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
            <h3 className="chat-title">Calendarik</h3>
            {/* <p className="chat-subtitle">
              {personality
                ? personality.name
                : 'Your personal planning companion'}
            </p> */}
          </div>
        </div>

        <select
          className="pers-select"
          value={personality.id}
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
        <div ref={endRef} />
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
            onKeyDown={keyPress}
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
