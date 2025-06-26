// src/components/landing/HowItWorks.tsx
import React from 'react';
import { MessageSquare, Calendar, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const HowItWorks: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const steps = [
    {
      icon: MessageSquare,
      key: 'chat',
      color: 'from-cyan-500 to-blue-500',
    },
    {
      icon: Calendar,
      key: 'analysis',
      color: 'from-yellow-500 to-orange-500',
    },
    {
      icon: CheckCircle,
      key: 'schedule',
      color: 'from-green-500 to-emerald-500',
    },
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-white pr-5 pl-5">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Heading */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            {t('howItWorks.heading')}{' '}
            <span className="bg-gradient-to-r from-cyan-500 to-blue-500 bg-clip-text text-transparent">
              {t('howItWorks.highlight')}
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {t('howItWorks.subheading')}
          </p>
        </div>

        {/* Steps */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, i) => {
            const Icon = step.icon;
            return (
              <div key={step.key} className="relative group">
                <div className="bg-white rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:scale-105 border border-gray-100">
                  <div
                    className={`w-16 h-16 bg-gradient-to-r ${step.color} rounded-2xl flex items-center justify-center mb-6 group-hover:animate-pulse`}
                  >
                    <Icon className="w-8 h-8 text-white" />
                  </div>

                  <div className="flex items-center mb-4">
                    <span className="text-3xl font-bold text-gray-300 mr-4">
                      0{i + 1}
                    </span>
                    <h3 className="text-xl font-bold text-gray-900">
                      {t(`howItWorks.steps.${step.key}.title`)}
                    </h3>
                  </div>

                  <p className="text-gray-600 leading-relaxed">
                    {t(`howItWorks.steps.${step.key}.description`)}
                  </p>
                </div>

                {/* Connector line */}
                {i < steps.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 w-8 h-0.5 bg-gradient-to-r from-gray-300 to-transparent transform -translate-y-1/2 z-10">
                    <div className="absolute right-0 top-1/2 w-2 h-2 bg-gray-400 rounded-full transform -translate-y-1/2" />
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* CTA */}
        <div className="mt-16 text-center">
          <div className="bg-gradient-to-r from-cyan-50 to-blue-50 rounded-3xl p-8 max-w-4xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              {t('howItWorks.cta.title')}
            </h3>
            <p className="text-gray-600 mb-6">
              {t('howItWorks.cta.description')}
            </p>
            <button
              onClick={() => navigate('/login')}
              className="bg-gradient-to-r from-cyan-500 to-blue-500 text-white px-8 py-4 rounded-2xl font-bold text-lg hover:shadow-lg transition-all duration-300 transform hover:scale-105"
            >
              {t('howItWorks.cta.button')}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
