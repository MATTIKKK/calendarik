// src/components/landing/Reviews.tsx
import React from 'react';
import { Star } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const Reviews: React.FC = () => {
  const { t } = useTranslation();
  const items = t('reviews.items', { returnObjects: true }) as Array<{
    name: string;
    role: string;
    content: string;
    avatar: string;
    rating: number;
  }>;

  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-white px-4 pr-5 pl-5">
      <div className="max-w-6xl mx-auto px-4">
        {/* Heading */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            {t('reviews.heading')}
            <span className="bg-gradient-to-r from-cyan-500 to-blue-500 bg-clip-text text-transparent">
              {' '}{t('reviews.highlight')}
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {t('reviews.subheading')}
          </p>
        </div>

        {/* Review cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {items.map((r, i) => (
            <div
              key={i}
              className="bg-white rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:scale-105"
            >
              <div className="flex items-center mb-6 space-x-1">
                {[...Array(r.rating)].map((_, idx) => (
                  <Star key={idx} className="w-5 h-5 text-yellow-400 fill-current" />
                ))}
              </div>

              <blockquote className="text-gray-700 text-lg mb-6 leading-relaxed">
                "{r.content}"
              </blockquote>

              <div className="flex items-center">
                <div className="text-3xl mr-4">{r.avatar}</div>
                <div>
                  <div className="font-bold text-gray-900">{r.name}</div>
                  <div className="text-gray-500 text-sm">{r.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Call to action */}
        <div className="mt-16 text-center">
          <div className="bg-white rounded-3xl p-8 shadow-lg max-w-2xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              {t('reviews.cta.title')}
            </h3>
            <p className="text-gray-600 mb-6">{t('reviews.cta.text')}</p>
            <button className="bg-gradient-to-r from-cyan-500 to-blue-500 text-white px-8 py-4 rounded-2xl font-bold text-lg hover:shadow-lg transition-all duration-300">
              {t('reviews.cta.button')}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Reviews;
