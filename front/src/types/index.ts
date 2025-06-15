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
