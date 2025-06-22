import { Message } from './message';

export interface ChatMessage extends Message {
  chat_id: number;
  role: 'user' | 'assistant';
  created_at: string;
  updated_at: string;
}

export interface Chat {
  id: number;
  title: string;
  owner_id: number;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

export interface SendMessageRequest {
  message: string;
  chat_id?: number;
  personality: string;
}

export interface SendMessageResponse {
  message: string;
  chat_id: number;
  title?: string;
}
