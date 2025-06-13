import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Bot,
  Calendar,
  Clock,
  AlertTriangle,
  Mic,
  MicOff,
  ChevronDown,
} from 'lucide-react';
import { Message, AssistantPersonality } from '../../../types';
import { MessageBubble } from '../message-bubble/MessageBubble';
import { TypingIndicator } from '../typing-indicator/TypingIndicator';
import './chat-interface.css';

export const personalities: AssistantPersonality[] = [
  { id: 'assistant',  name: 'Professional Assistant', description: 'Formal…',  tone: 'assistant',  avatar: '💼' },
  { id: 'coach',      name: 'Motivational Coach',   description: 'Energetic…', tone: 'coach',      avatar: '💪' },
  { id: 'friend',     name: 'Best Friend',          description: 'Casual…',    tone: 'friend',     avatar: '👥' },
  { id: 'girlfriend', name: 'Caring Girlfriend',    description: 'Sweet…',     tone: 'girlfriend', avatar: '💕' },
  { id: 'boyfriend',  name: 'Supportive Boyfriend', description: 'Protective…',tone: 'boyfriend',  avatar: '❤️' },
];

/* быстрые ответы */
const quickMessages = [
  'Schedule a meeting',
  'What’s my schedule today?',
  'Find free time this week',
  'Cancel my 3pm appointment',
];

export const ChatInterface: React.FC = () => {
  /* — state — */
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content:
        'Hi! I’m your AI assistant. Tell me about your plans, tasks, or deadlines, and I’ll help you organize them in your calendar. How can I help you today?',
      sender: 'assistant',
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false); 
  const [personality, setPersonality] = useState<AssistantPersonality >(
    { id:'assistant',  name:'Professional Assistant', description:'Formal…',  tone:'assistant',  avatar:'💼' },
  );
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(
    null
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);

  /* — прокрутка вниз — */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  /* — отправка текста — */
  const send = (text?: string) => {
    const content = text ?? inputMessage;
    if (!content.trim()) return;

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

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          content: generateAIResponse(content),
          sender: 'assistant',
          timestamp: new Date(),
        },
      ]);
      setIsTyping(false);
    }, 1500);
  };

  /* — генерация «ответа» — */
  const generateAIResponse = (txt: string) => {
    const t = txt.toLowerCase();
    if (/meeting|call/.test(t)) return 'I see you mentioned a meeting…';
    if (/deadline|due/.test(t)) return 'I notice you have a deadline…';
    if (/task|todo/.test(t)) return 'Great! I’ll help you schedule…';
    if (/schedule today/.test(t)) return 'Here’s your schedule for today…';
    if (/free time/.test(t)) return 'Looking at your calendar…';
    if (/cancel.*3pm/.test(t)) return 'I’ve cancelled your 3 PM appointment…';
    return 'Got it! Tell me timeframe, priority, and details so I can fit it in.';
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

        {/* <select> вместо кастомного дропдауна */}
        <select
          className="pers-select"
          value={personality.id}
          onChange={(e) => {
            const next = personalities.find(p => p.id === e.target.value)!;
            setPersonality(next);
          }}
        >
          {personalities.map(p => (
            <option key={p.id} value={p.id}>
              {p.avatar}  {p.name}
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
          disabled={!inputMessage.trim()}
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
