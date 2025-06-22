import { Feature, PricingPlan, Review } from "../types/landing";

export const features: Feature[] = [
  {
    icon: 'Globe',
    title: 'Multi-Timezone Support',
    description: 'Adapt automatically to any timezone — all events are shown in your local time, no matter where you are.'
  },
  {
    icon: 'Brain',
    title: 'Mental Clarity by Design',
    description: 'Calendarik takes full control of your tasks so you don’t have to hold everything in your head. Your mind stays clear and focused.'
  },
  {
    icon: 'Bell',
    title: 'Smart Reminders & Risk Reduction',
    description: 'Always stay ahead of your day. Calendarik reminds you of every plan and prevents missed events or loss of control.'
  },
  {
    icon: 'Zap',
    title: 'Coming Soon: Smart Integrations',
    description: 'Integrations with Google Calendar, Outlook and more — so your plans always stay in sync.'
  }
];

export const reviews: Review[] = [
  {
    name: 'Sarah Chen',
    role: 'Project Coordinator',
    content: 'Calendarik helps me stay focused by taking full control of my tasks and plans. I no longer need to memorize everything — it keeps me on track and reminds me when it matters.',
    avatar: '👩‍💼',
    rating: 5
  },
  {
    name: 'Marcus Johnson',
    role: 'Remote Consultant',
    content: 'The timezone adaptation is seamless. I travel often, and Calendarik always shows my events in local time. No confusion, no missed meetings.',
    avatar: '👨‍💻',
    rating: 5
  },
  {
    name: 'Elena Rodriguez',
    role: 'Productive Minimalist',
    content: 'What I love most is the mental clarity. I open the calendar, and everything I need is laid out simply — with reminders, priorities, and zero clutter.',
    avatar: '👩‍🚀',
    rating: 5
  }
];


export const pricingPlans: PricingPlan[] = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    color: 'from-gray-500 to-gray-600',
    features: [
      'Up to 50 events per month',
      'Basic scheduling assistant',
      '2 timezone support',
      'Email reminders',
      'Mobile app access'
    ]
  },
  {
    name: 'Pro',
    price: '$12',
    period: 'per month',
    color: 'from-cyan-500 to-blue-500',
    popular: true,
    features: [
      'Unlimited events',
      'AI personality modes',
      'Unlimited timezone support',
      'Conflict prevention',
      'Upcoming: calendar integrations',
      'Priority support',
      'Usage analytics'
    ]
  }
];

export const faqItems = [
  {
    question: 'How does the AI assistant understand my scheduling preferences?',
    answer: 'Our AI learns from your past scheduling patterns, meeting preferences, and feedback to make increasingly accurate suggestions. It considers factors like your preferred meeting times, buffer periods, and work-life balance preferences.'
  },
  {
    question: 'Can I change the AI personality after setting it up?',
    answer: 'Absolutely! You can switch between different AI personalities anytime in your settings. Each personality maintains the same scheduling intelligence but communicates in their unique style.'
  },
  {
    question: 'How does timezone handling work for international teams?',
    answer: 'Calendarik automatically detects and converts time zones for all participants. It shows meeting times in everyone\'s local timezone and prevents scheduling conflicts due to timezone confusion.'
  },
  {
    question: 'What calendars can I integrate with Calendarik?',
    answer: 'Integrations are coming soon. We plan to support Google Calendar, Outlook, Apple Calendar, and most CalDAV-compatible calendar services.'
  },
  {
    question: 'Is my calendar data secure and private?',
    answer: 'Yes, we use enterprise-grade encryption and never share your personal data. Calendarik keeps your data safe and only uses local processing for AI when possible.'
  }
];
