export interface Event {
  id: string;
  title: string;
  description?: string;
  startTime: Date;
  endTime?: Date;          // для задач может быть null
  priority: 'high' | 'medium' | 'low';
  type: 'meeting' | 'deadline' | 'task';   // ← добавили task
  userId: string;
}