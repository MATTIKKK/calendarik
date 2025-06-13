export interface User {
  id: string;
  email: string;
  name: string;
  timezone: string;
  gender: 'male' | 'female' | 'other';
  createdAt: Date;
}

export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  type?: 'text' | 'task' | 'event';
}

export interface Event {
  id: string;
  title: string;
  description?: string;
  startTime: Date;
  endTime: Date;
  priority: 'low' | 'medium' | 'high';
  type: 'task' | 'meeting' | 'deadline' | 'personal';
  userId: string;
}

export interface AssistantPersonality {
  id: string;
  name: string;
  description: string;
  tone: 'coach' | 'assistant' | 'friend' | 'girlfriend' | 'boyfriend';
  avatar: string;
}

export interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

export interface RegisterData {
  email: string;
  password: string;
  name: string;
  timezone: string;
  gender: 'male' | 'female' | 'other';
}