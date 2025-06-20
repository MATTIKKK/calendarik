export * from './user';
export * from './auth';
export * from './message';
export * from './event';
export * from './chat';

export interface User {
  id: number;
  email: string;
  full_name: string;
  timezone: string;
  gender: string;
  is_active: boolean;
}

export interface Message {
  id: string;
  content: string;
  sender: 'assistant' | 'user';
  timestamp: Date;
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
  tone: string;
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
  full_name: string;
  timezone: string;
  gender: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
