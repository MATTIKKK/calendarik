import axios from 'axios';
import { Chat, SendMessageRequest, SendMessageResponse } from '../types/chat';
import { API_URL } from '../config';

// const API_URL = 'http://128.251.224.196:8000/api';

export const chatService = {
  async getChats(): Promise<Chat[]> {
    const token = localStorage.getItem('accessToken');
    const response = await axios.get(`/api/chat/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data.chats;
  },

  async getChat(chatId: number): Promise<Chat> {
    const token = localStorage.getItem('accessToken');
    const response = await axios.get(`/api/chat/${chatId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },

  async sendMessage(
    data: SendMessageRequest & { personality?: string; language?: string }
  ): Promise<SendMessageResponse> {
    const token = localStorage.getItem('accessToken');
    const response = await axios.post(
      `/api/ai/analyze`,
      {
        message: data.message,
        chat_id: data.chat_id,
        personality: data.personality || 'assistant',
        language: data.language,
      },
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    return {
      message: response.data.message,
      chat_id: response.data.chat_id,
      title: !data.chat_id && response.data.title
        ? response.data.title
        : response.data.message.slice(0, 50) + '...',
    };
  },

  async updateChatTitle(chatId: number, title: string): Promise<Chat> {
    const token = localStorage.getItem('accessToken');
    const response = await axios.put(
      `/api/chat/${chatId}`,
      { title },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return response.data;
  },

  async deleteChat(chatId: number): Promise<void> {
    const token = localStorage.getItem('accessToken');
    await axios.delete(`/api/chat/${chatId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  },
};
