// src/components/chat/ChatInterface.tsx
import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, AlertTriangle, Mic, MicOff } from 'lucide-react';
import axios from 'axios';
import * as sdk from 'microsoft-cognitiveservices-speech-sdk';
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

export const ChatInterface: React.FC = () => {
  const { t } = useTranslation();
  const { token, user, setUser } = useAuth();

  /* ---------- state ---------- */
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [personalityId, setPersonalityId] = useState(user?.chat_personality);
  const [chatId, setChatId] = useState<number | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  /* speech-to-text */
  const [azListening, setAzListening] = useState(false);
  const [azTranscript, setAzTranscript] = useState('');
  const recognizerRef = useRef<sdk.SpeechRecognizer | null>(null);
  const lastRecognizedRef = useRef('');          // ✓ анти-дубль

  /* ---------- effects ---------- */
  useEffect(() => {
    if (!token || chatId === null) return;
    (async () => {
      try {
        setMessages(await fetchChatHistory(token));
      } catch (err) {
        console.error(t('chat.errors.loadHistory'), err);
      }
    })();
  }, [chatId, token, t]);

  useEffect(() => {
    if (user?.chat_personality && user.chat_personality !== personalityId) {
      setPersonalityId(user.chat_personality);
    }
  }, [user, personalityId]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  useEffect(() => {
    if (!token) return;
    axios
      .get<Chat>(`/api/chat/me`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setChatId(res.data.id))
      .catch((err) => console.error(t('chat.errors.loadChat'), err));
  }, [token, t]);

  /* показываем живую речь */
  useEffect(() => {
    if (azListening) setInputMessage(azTranscript);
  }, [azTranscript, azListening]);

  /* ---------- helpers ---------- */
  const createRecognizer = async () => {
    const { data } = await axios.get<{ token: string; region: string }>(
      `/api/speech/token`
    );
    const speechConfig = sdk.SpeechConfig.fromAuthorizationToken(
      data.token,
      data.region
    );
    speechConfig.speechRecognitionLanguage = 'ru-RU';
    return new sdk.SpeechRecognizer(
      speechConfig,
      sdk.AudioConfig.fromDefaultMicrophoneInput()
    );
  };

  const stopRecognizer = () =>
    new Promise<void>((resolve) => {
      recognizerRef.current?.stopContinuousRecognitionAsync(() => {
        recognizerRef.current?.close();
        recognizerRef.current = null;
        setAzListening(false);
        resolve();
      });
    });

  /* ---------- send handler ---------- */
  const send = async (text?: string) => {
    if (!token || isTyping) return;
    const content = (text ?? inputMessage ?? azTranscript).trim();
    if (!content) return;

    if (azListening) await stopRecognizer();

    setMessages((prev) => [
      ...prev,
      { id: Date.now().toString(), content, sender: 'user', timestamp: new Date() },
    ]);
    setInputMessage('');
    setAzTranscript('');
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

  /* ---------- mic start / stop ---------- */
  const handleMicClick = async () => {
    if (azListening) {
      await stopRecognizer();
      return;
    }
    try {
      const recognizer = await createRecognizer();
      recognizerRef.current = recognizer;
      setAzListening(true);
      setAzTranscript('');
      lastRecognizedRef.current = '';

      recognizer.recognized = (_, e) => {
        if (
          e.result.reason === sdk.ResultReason.RecognizedSpeech &&
          e.result.text &&
          e.result.text !== lastRecognizedRef.current
        ) {
          setAzTranscript(e.result.text);
          lastRecognizedRef.current = e.result.text;
        }
      };
      recognizer.sessionStopped = stopRecognizer;
      recognizer.startContinuousRecognitionAsync();
    } catch (err) {
      console.error('Azure Speech error', err);
      alert('Не удалось получить доступ к микрофону или Azure Speech API.');
    }
  };

  /* ---------- personality ---------- */
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

  const quickMessages = t('chat.quickMessages', { returnObjects: true }) as string[];
  const badges = t('chat.badges', { returnObjects: true }) as string[];

  /* ---------- render ---------- */
  return (
    <div className="chat-root">
      <header className="chat-header">
        <div className="chat-header-left">
          <div className="chat-avatar"><Bot size={24} /></div>
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

      <main className="chat-messages">
        {messages.map((m) => <MessageBubble key={m.id} message={m} />)}
        {isTyping && <TypingIndicator />}
        <div ref={endRef} />
      </main>

      <section className="chat-quick">
        {quickMessages.map((q, i) => (
          <button key={i} onClick={() => send(q)} className="quick-btn">
            {q}
          </button>
        ))}
      </section>

      <footer className="chat-input-wrap">
        <div className="chat-textarea-block">
          <textarea
            rows={2}
            placeholder={t('chat.placeholder')}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
            className="chat-textarea"
          />
          <button
            onClick={handleMicClick}
            className={`mic-btn ${azListening ? 'recording' : ''}`}
            title={azListening ? t('chat.mic.stop') : t('chat.mic.start')}
          >
            {azListening ? <MicOff size={16} /> : <Mic size={16} />}
          </button>
        </div>

        <button
          onClick={() => send()}
          disabled={(!inputMessage.trim() && !azTranscript.trim()) || isTyping}
          className="send-btn"
          title={t('chat.send')}
        >
          <Send size={20} />
        </button>
      </footer>

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
