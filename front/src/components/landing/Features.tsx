// src/components/landing/Features.tsx
import React from 'react';
import * as LucideIcons from 'lucide-react';
import { useTranslation } from 'react-i18next';

const Features: React.FC = () => {
  const { t } = useTranslation();

  // we’ll pull both icon name *and* text from translation files
  const items = t('features.items', { returnObjects: true }) as Array<{
    icon: string;
    title: string;
    description: string;
  }>;

  return (
    <section className="py-20 bg-white pr-5 pl-5">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Heading */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            {t('features.heading')}{' '}
            <span className="bg-gradient-to-r from-cyan-500 to-blue-500 bg-clip-text text-transparent">
              {t('features.highlight')}
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {t('features.subheading')}
          </p>
        </div>

        {/* Feature list */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {items.map((feat, idx) => {
            const Icon = (LucideIcons as any)[feat.icon] || LucideIcons.Star;
            const isEven = idx % 2 === 0;
            const gradient =
              idx === 0
                ? 'from-cyan-500 to-blue-500'
                : idx === 1
                ? 'from-yellow-500 to-orange-500'
                : idx === 2
                ? 'from-green-500 to-emerald-500'
                : 'from-purple-500 to-indigo-500';

            return (
              <div
                key={idx}
                className={`flex items-center space-x-8 ${
                  !isEven ? 'md:flex-row-reverse md:space-x-reverse' : ''
                }`}
              >
                <div className="flex-shrink-0">
                  <div
                    className={`w-24 h-24 bg-gradient-to-br ${gradient} rounded-3xl flex items-center justify-center shadow-lg`}
                  >
                    <Icon className="w-12 h-12 text-white" />
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">
                    {feat.title}
                  </h3>
                  <p className="text-gray-600 text-lg leading-relaxed">
                    {feat.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Stats */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-gradient-to-br from-cyan-50 to-blue-50 rounded-2xl p-8 text-center">
            <div className="text-3xl font-bold text-cyan-600 mb-2">
              {t('features.stats.users')}
            </div>
            <div className="text-gray-600">{t('features.stats.usersLabel')}</div>
          </div>
          <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-2xl p-8 text-center">
            <div className="text-3xl font-bold text-orange-600 mb-2">
              {t('features.stats.meetings')}
            </div>
            <div className="text-gray-600">{t('features.stats.meetingsLabel')}</div>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-8 text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">
              {t('features.stats.uptime')}
            </div>
            <div className="text-gray-600">{t('features.stats.uptimeLabel')}</div>
          </div>
        </div>  
      </div>
    </section>
  );
};

export default Features;
