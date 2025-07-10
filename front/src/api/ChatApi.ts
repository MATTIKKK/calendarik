// src/api/ChatApi.ts
import axios from 'axios';
import { ChatMessage, SendMessageRequest, SendMessageResponse } from '../types/chat';
import { API_URL } from '../config';
import { Message } from '../types/message';

export async function fetchChatHistory(
  token: string
): Promise<Message[]> {
  const { data } = await axios.get<ChatMessage[]>(
    `/api/chat/me/messages`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  const msgs: Message[] = data
    .slice()
    .reverse()
    .map((m) => ({
      id: m.id.toString(),
      content: m.content,
      sender: m.role === 'assistant' ? 'assistant' : 'user',
      timestamp: new Date(m.created_at),
    }));

  return msgs;
}


export async function sendChatMessage(
  payload: SendMessageRequest,
  token: string
): Promise<SendMessageResponse> {
  const { data } = await axios.post<SendMessageResponse>(
    `/api/chat/message`,
    payload,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return data;
}