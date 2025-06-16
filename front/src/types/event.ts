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
