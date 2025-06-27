// src/components/chat/ChatInterface.tsx
import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Bot,
  AlertTriangle,
  Mic,
  MicOff,
} from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../../../contexts/AuthContext';
import { fetchChatHistory } from '../../../api/ChatApi';
import { personalities } from '../../../constants/personalities';
import { Message } from '../../../types/message';
import { Chat } from '../../../types/chat';
import { MessageBubble } from '../message-bubble/MessageBubble';
import { TypingIndicator } from '../typing-indicator/TypingIndicator';
import './chat-interface.css';
import { useTranslation } from 'react-i18next';

export const ChatInterface: React.FC = () => {
  const { t } = useTranslation();

  const { token, user, setUser } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [personalityId, setPersonalityId] = useState(user?.chat_personality);

  console.log("user chat personality", user?.chat_personality)
  const [chatId, setChatId] = useState<number | null>(null);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  // загрузка истории
  useEffect(() => {
    if (!token || chatId === null) return;
    (async () => {
      try {
        const msgs = await fetchChatHistory(chatId, token);
        setMessages(msgs);
      } catch (err) {
        console.error(t('chat.errors.loadHistory'), err);
      }
    })();
  }, [chatId, token, t]);

  useEffect(() => {
    if (user?.chat_personality && user.chat_personality !== personalityId) {
      setPersonalityId(user.chat_personality);
    }

  }, [user?.chat_personality])

  // автоскролл
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // создание/получение chatId
  useEffect(() => {
    if (!token) return;
    axios.get<Chat>(`/api/chat/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    .then(res => setChatId(res.data.id))
    .catch(err => console.error(t('chat.errors.loadChat'), err));
  }, [token, t]);

  const send = async (text?: string) => {
    if (!token || isTyping) return;
    const content = (text ?? inputMessage).trim();
    if (!content) return;

    setMessages(prev => [
      ...prev,
      { id: Date.now().toString(), content, sender: 'user', timestamp: new Date() },
    ]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const { data } = await axios.post(`/api/chat/message`, {
        message: content,
        personality: personalityId,
        chat_id: chatId ?? undefined,
      }, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (chatId === null) setChatId(data.chat_id);

      setMessages(prev => [
        ...prev,
        { id: (Date.now()+1).toString(), content: data.message, sender: 'assistant', timestamp: new Date() },
      ]);
    } catch (err) {
      console.error(t('chat.errors.send'), err);
    } finally {
      setIsTyping(false);
    }
  };

  // Enter → отправка
  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  // микрофон (симуляция)
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream);
      rec.ondataavailable = (e) => {
        if (e.data.size) {
          setTimeout(() => {
            setInputMessage(t('chat.voiceSimulated'));
            setIsRecording(false);
          }, 2000);
        }
      };
      rec.start();
      setMediaRecorder(rec);
      setIsRecording(true);
    } catch {
      alert(t('chat.errors.micPermission'));
    }
  };
  const stopRecording = () => {
    mediaRecorder?.stop();
    mediaRecorder?.stream.getTracks().forEach(t => t.stop());
    setMediaRecorder(null);
    setIsRecording(false);
  };

  // смена личности
  const changePersonality = async (newId: string) => {
    if (!token) return;
    setPersonalityId(newId);
    try {
      const result = await axios.put(`/api/user/me/personality`, { personality: newId }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      console.log("result in chat personality", result)
      setUser({ ...user!, chat_personality: newId });
    } catch (err) {
      console.error(t('chat.errors.updatePersonality'), err);
    }
  };

  // быстрые ответы и бейджи из локалей
  const quickMessages = t('chat.quickMessages', { returnObjects: true }) as string[];
  const badges = t('chat.badges', { returnObjects: true }) as string[];

  return (
    <div className="chat-root">
      {/* header */}
      <header className="chat-header">
        <div className="chat-header-left">
          <div className="chat-avatar"><Bot size={24} /></div>
          <h3 className="chat-title">{t('chat.title')}</h3>
        </div>
        <select
          className="pers-select"
          value={personalityId}
          onChange={e => changePersonality(e.target.value)}
        >
          {personalities.map(p => (
            <option key={p.id} value={p.id}>
              {p.avatar} {t(`personalities.${p.id}.name`)}
            </option>
          ))}
        </select>
      </header>

      {/* сообщения */}
      <main className="chat-messages">
        {messages.map(m => <MessageBubble key={m.id} message={m} />)}
        {isTyping && <TypingIndicator />}
        <div ref={endRef} />
      </main>

      {/* быстрые ответы */}
      <section className="chat-quick">
        {quickMessages.map((q, i) => (
          <button key={i} onClick={() => send(q)} className="quick-btn">
            {q}
          </button>
        ))}
      </section>

      {/* ввод */}
      <footer className="chat-input-wrap">
        <div className="chat-textarea-block">
          <textarea
            rows={2}
            placeholder={t('chat.placeholder')}
            value={inputMessage}
            onChange={e => setInputMessage(e.target.value)}
            onKeyDown={onKeyDown}
            className="chat-textarea"
          />
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`mic-btn ${isRecording ? 'recording' : ''}`}
            title={isRecording ? t('chat.mic.stop') : t('chat.mic.start')}
          >
            {isRecording ? <MicOff size={16}/> : <Mic size={16}/>}
          </button>
        </div>
        <button
          onClick={() => send()}
          disabled={!inputMessage.trim() || isTyping}
          className="send-btn"
          title={t('chat.send')}
        >
          <Send size={20}/>
        </button>
      </footer>

      {/* бейджи */}
      <div className="chat-badges">
        {badges.map((b, i) => (
          <span key={i}><AlertTriangle size={14}/> {b}</span>
        ))}
      </div>
    </div>
  );
};
