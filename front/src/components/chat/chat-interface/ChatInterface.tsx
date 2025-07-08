// src/components/chat/ChatInterface.tsx
import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, AlertTriangle, Mic, MicOff } from 'lucide-react';
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
import { API_URL } from '../../../config';
import SpeechRecognition, {
  useSpeechRecognition,
} from 'react-speech-recognition';

export const ChatInterface: React.FC = () => {
  const { t } = useTranslation();
  const { token, user, setUser } = useAuth();

  // ------------------------------------------------------------------
  // STATE
  // ------------------------------------------------------------------
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [personalityId, setPersonalityId] = useState(user?.chat_personality);
  const [chatId, setChatId] = useState<number | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  // Speech‑to‑Text hook
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
  } = useSpeechRecognition();

  // ------------------------------------------------------------------
  // EFFECTS
  // ------------------------------------------------------------------
  // Подгрузка истории
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

  // Синхронизируем выбранную «личность»
  useEffect(() => {
    if (user?.chat_personality && user.chat_personality !== personalityId) {
      setPersonalityId(user.chat_personality);
    }
  }, [user, personalityId]);

  // Автоскролл
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Получаем / создаём chat‑id
  useEffect(() => {
    if (!token) return;
    axios
      .get<Chat>(`/api/chat/me`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setChatId(res.data.id))
      .catch((err) => console.error(t('chat.errors.loadChat'), err));
  }, [token, t]);

  // Когда идёт запись — выводим «живой» транскрипт в textarea
  useEffect(() => {
    if (listening) setInputMessage(transcript);
  }, [transcript, listening]);

  // ------------------------------------------------------------------
  // HANDLERS
  // ------------------------------------------------------------------
  const send = async (text?: string) => {
    if (!token || isTyping) return;
    const content = (text ?? inputMessage).trim();
    if (!content) return;

    if (listening) SpeechRecognition.stopListening();

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
    resetTranscript();
    setIsTyping(true);

    try {
      const { data } = await axios.post(
        `/api/chat/message`,
        {
          message: content,
          personality: personalityId,
          chat_id: chatId ?? undefined,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

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
      console.error(t('chat.errors.send'), err);
    } finally {
      setIsTyping(false);
    }
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  // Запуск / остановка микрофона
  const handleMicClick = () => {

    if (!browserSupportsSpeechRecognition) {
      alert(
        'SpeechRecognition API не поддерживается в этом браузере. Попробуйте Chrome или Safari ≥14.1.'
      );
      return;
    }
    if (listening) {
      SpeechRecognition.stopListening();
    } else {
      SpeechRecognition.startListening({
        continuous: true,
        interimResults: true,
        language: 'ru-RU', // при необходимости поменяйте
      });
    }
  };

  const changePersonality = async (newId: string) => {
    if (!token) return;
    setPersonalityId(newId);
    try {
      await axios.put(
        `/api/user/me/personality`,
        { personality: newId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setUser({ ...user!, chat_personality: newId });
    } catch (err) {
      console.error(t('chat.errors.updatePersonality'), err);
    }
  };

  const quickMessages = t('chat.quickMessages', {
    returnObjects: true,
  }) as string[];
  const badges = t('chat.badges', { returnObjects: true }) as string[];

  // ------------------------------------------------------------------
  // RENDER
  // ------------------------------------------------------------------
  return (
    <div className="chat-root">
      {/* Header */}
      <header className="chat-header">
        <div className="chat-header-left">
          <div className="chat-avatar">
            <Bot size={24} />
          </div>
          <h3 className="chat-title">{t('chat.title')}</h3>
        </div>
        <select
          className="pers-select"
          value={personalityId}
          onChange={(e) => changePersonality(e.target.value)}
        >
          {personalities.map((p) => (
            <option key={p.id} value={p.id}>
              {p.avatar} {t(`personalities.${p.id}.name`)}
            </option>
          ))}
        </select>
      </header>

      {/* Сообщения */}
      <main className="chat-messages">
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
        {isTyping && <TypingIndicator />}
        <div ref={endRef} />
      </main>

      {/* Быстрые ответы */}
      <section className="chat-quick">
        {quickMessages.map((q, i) => (
          <button key={i} onClick={() => send(q)} className="quick-btn">
            {q}
          </button>
        ))}
      </section>

      {/* Ввод */}
      <footer className="chat-input-wrap">
        <div className="chat-textarea-block">
          <textarea
            rows={2}
            placeholder={t('chat.placeholder')}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={onKeyDown}
            className="chat-textarea"
          />
          <button
            onClick={handleMicClick}
            className={`mic-btn ${listening ? 'recording' : ''}`}
            title={listening ? t('chat.mic.stop') : t('chat.mic.start')}
          >
            {listening ? <MicOff size={16} /> : <Mic size={16} />}
          </button>
        </div>
        <button
          onClick={() => send()}
          disabled={!inputMessage.trim() || isTyping}
          className="send-btn"
          title={t('chat.send')}
        >
          <Send size={20} />
        </button>
      </footer>

      {/* Бейджи */}
      <div className="chat-badges">
        {badges.map((b, i) => (
          <span key={i}>
            <AlertTriangle size={14} /> {b}
          </span>
        ))}
      </div>
    </div>
  );
};
