export interface CalendarExtraction {
  type: 'event' | 'task' | 'meeting';
  title: string;
  description?: string;
  startTime: string;
  endTime?: string;
  priority?: 'low' | 'medium' | 'high';
}

export interface AIMessageAnalysis {
  detectedLanguage: string;
  calendarData?: CalendarExtraction;
  shouldCreateEvent: boolean;
}

export interface AIConfig {
  model: string;
  temperature: number;
  maxTokens: number;
  personality: string;
  userGender: string;
  language: string;
}
