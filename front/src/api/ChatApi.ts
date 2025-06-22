// src/api/ChatApi.ts
import axios from 'axios';
import { ChatMessage, SendMessageRequest, SendMessageResponse } from '../types/chat';
import { API_URL } from '../config';
import { Message } from '../types/message';

const WELCOME_TEXT = 'Привет! Я ваш личный помощник-планировщик. Чем могу помочь?';

export async function fetchChatHistory(
  chatId: number,
  token: string
): Promise<Message[]> {
  const { data } = await axios.get<ChatMessage[]>(
    `${API_URL}/api/chat/${chatId}/messages`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  let msgs: Message[] = data
    .slice()
    .reverse()
    .map((m) => ({
      id: m.id.toString(),
      content: m.content,
      sender: m.role === 'assistant' ? 'assistant' : 'user',
      timestamp: new Date(m.created_at),
    }));

  if (msgs.length === 0) {
    msgs = [
      {
        id: 'welcome',
        content: WELCOME_TEXT,
        sender: 'assistant',
        timestamp: new Date(),
      },
    ];
  }

  return msgs;
}


export async function sendChatMessage(
  payload: SendMessageRequest,
  token: string
): Promise<SendMessageResponse> {
  const { data } = await axios.post<SendMessageResponse>(
    `${API_URL}/api/chat/message`,
    payload,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return data;
}