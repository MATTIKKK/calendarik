import { AssistantPersonality } from "../types/landing";

export const personalities: AssistantPersonality[] = [
  {
    id: 'assistant',
    name: 'Professional Assistant',
    description: 'Formal and efficient tone',
    tone: 'assistant',
    avatar: '💼',
    color: 'from-blue-500 to-blue-600'
  },
  {
    id: 'coach',
    name: 'Motivational Coach',
    description: 'Energetic and dynamic',
    tone: 'coach',
    avatar: '💪',
    color: 'from-orange-500 to-red-500'
  },
  {
    id: 'friend',
    name: 'Best Friend',
    description: 'Casual and informal',
    tone: 'friend',
    avatar: '👥',
    color: 'from-green-500 to-emerald-500'
  },
  {
    id: 'girlfriend',
    name: 'Caring Girlfriend',
    description: 'Sweet and supportive',
    tone: 'girlfriend',
    avatar: '💕',
    color: 'from-pink-500 to-rose-500'
  },
  {
    id: 'boyfriend',
    name: 'Supportive Boyfriend',
    description: 'Protective and reassuring',
    tone: 'boyfriend',
    avatar: '❤️',
    color: 'from-purple-500 to-indigo-500'
  }
];