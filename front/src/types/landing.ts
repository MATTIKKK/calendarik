export interface AssistantPersonality {
  id: string;
  name: string;
  description: string;
  tone: string;
  avatar: string;
  color: string;
}

export interface Feature {
  icon: string;
  title: string;
  description: string;
}

export interface Review {
  name: string;
  role: string;
  content: string;
  avatar: string;
  rating: number;
}

export interface PricingPlan {
  name: string;
  price: string;
  period: string;
  features: string[];
  popular?: boolean;
  color: string;
}