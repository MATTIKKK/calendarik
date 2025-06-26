
export interface PersonalityConfig {
  id: 'assistant' | 'coach' | 'friend' | 'girlfriend' | 'boyfriend';

  tone: string;

  avatar: string;

  color: string;
}

export const personalities: PersonalityConfig[] = [
  {
    id: 'assistant',
    tone: 'assistant',
    avatar: '💼',
    color: 'from-blue-500 to-blue-600',
  },
  {
    id: 'coach',
    tone: 'coach',
    avatar: '💪',
    color: 'from-orange-500 to-red-500',
  },
  {
    id: 'friend',
    tone: 'friend',
    avatar: '👥',
    color: 'from-green-500 to-emerald-500',
  },
  {
    id: 'girlfriend',
    tone: 'girlfriend',
    avatar: '💕',
    color: 'from-pink-500 to-rose-500',
  },
  {
    id: 'boyfriend',
    tone: 'boyfriend',
    avatar: '❤️',
    color: 'from-purple-500 to-indigo-500',
  },
];
