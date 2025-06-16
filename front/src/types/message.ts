export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  type?: 'text' | 'task' | 'event';
}

export interface AssistantPersonality {
  id: string;
  name: string;
  description: string;
  tone: 'coach' | 'assistant' | 'friend' | 'girlfriend' | 'boyfriend';
  avatar: string;
}
