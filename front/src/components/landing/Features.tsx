import React from 'react';
import * as LucideIcons from 'lucide-react';
import { features } from '../../constants/content';

const Features: React.FC = () => {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Powerful Features for
            <span className="bg-gradient-to-r from-cyan-500 to-blue-500 bg-clip-text text-transparent"> Modern Teams</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Everything you need to manage complex schedules with ease and intelligence.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature, index) => {
            const Icon = (LucideIcons as any)[feature.icon] || LucideIcons.Star;
            const isEven = index % 2 === 0;
            
            return (
              <div key={index} className={`flex items-center space-x-8 ${!isEven ? 'md:flex-row-reverse md:space-x-reverse' : ''}`}>
                <div className="flex-shrink-0">
                  <div className={`w-24 h-24 bg-gradient-to-br ${
                    index === 0 ? 'from-cyan-500 to-blue-500' :
                    index === 1 ? 'from-yellow-500 to-orange-500' :
                    index === 2 ? 'from-green-500 to-emerald-500' :
                    'from-purple-500 to-indigo-500'
                  } rounded-3xl flex items-center justify-center shadow-lg`}>
                    <Icon className="w-12 h-12 text-white" />
                  </div>
                </div>
                
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">{feature.title}</h3>
                  <p className="text-gray-600 text-lg leading-relaxed">{feature.description}</p>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-gradient-to-br from-cyan-50 to-blue-50 rounded-2xl p-8 text-center">
            <div className="text-3xl font-bold text-cyan-600 mb-2">50K+</div>
            <div className="text-gray-600">Active Users</div>
          </div>
          <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-2xl p-8 text-center">
            <div className="text-3xl font-bold text-orange-600 mb-2">1M+</div>
            <div className="text-gray-600">Meetings Scheduled</div>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-8 text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">99.9%</div>
            <div className="text-gray-600">Uptime Guarantee</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Features;