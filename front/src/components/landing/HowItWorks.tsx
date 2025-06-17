import React from 'react';
import { MessageSquare, Calendar, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const HowItWorks: React.FC = () => {
  const navigate = useNavigate();
  const steps = [
    {
      icon: MessageSquare,
      title: 'Chat with AI',
      description: 'Tell our AI assistant about your plans in natural language. No complex forms or settings.',
      color: 'from-cyan-500 to-blue-500'
    },
    {
      icon: Calendar,
      title: 'AI Finds Perfect Times',
      description: 'Our smart algorithm analyzes all schedules, preferences, and time zones to suggest optimal time slots.',
      color: 'from-yellow-500 to-orange-500'
    },
    {
      icon: CheckCircle,
      title: 'Schedule & Relax',
      description: 'Confirm your choice and let Calendarik handle events, reminders, and calendar updates automatically.',
      color: 'from-green-500 to-emerald-500'
    }
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            How It Works in
            <span className="bg-gradient-to-r from-cyan-500 to-blue-500 bg-clip-text text-transparent"> 3 Simple Steps</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            From chaos to perfectly organized calendar in minutes. No learning curve, no complexity.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={index} className="relative group">
                <div className="bg-white rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:scale-105 border border-gray-100">
                  <div className={`w-16 h-16 bg-gradient-to-r ${step.color} rounded-2xl flex items-center justify-center mb-6 group-hover:animate-pulse`}>
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                  
                  <div className="flex items-center mb-4">
                    <span className="text-3xl font-bold text-gray-300 mr-4">0{index + 1}</span>
                    <h3 className="text-xl font-bold text-gray-900">{step.title}</h3>
                  </div>
                  
                  <p className="text-gray-600 leading-relaxed">{step.description}</p>
                </div>

                {/* Connecting line for desktop */}
                {index < steps.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 w-8 h-0.5 bg-gradient-to-r from-gray-300 to-transparent transform -translate-y-1/2 z-10">
                    <div className="absolute right-0 top-1/2 w-2 h-2 bg-gray-400 rounded-full transform -translate-y-1/2"></div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className="mt-16 text-center">
          <div className="bg-gradient-to-r from-cyan-50 to-blue-50 rounded-3xl p-8 max-w-4xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Ready to experience the magic?</h3>
            <p className="text-gray-600 mb-6">Join thousands of users who've already simplified their scheduling.</p>
            <button className="bg-gradient-to-r from-cyan-500 to-blue-500 text-white px-8 py-4 rounded-2xl font-bold text-lg hover:shadow-lg transition-all duration-300 transform hover:scale-105" onClick={() => navigate('/login')}>
              Start Your Free Trial
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;