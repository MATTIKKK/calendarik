// src/components/landing/Hero.tsx
import React from 'react';
import { Calendar, MessageCircle, Clock, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSelector from './LanguageSelector';

const Hero: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();

  return (
    <section className="relative min-h-screen bg-gradient-to-br from-cyan-50 via-blue-50 to-indigo-100 overflow-hidden pr-5 pl-5">
      {/* language selector floats above everything */}
      <LanguageSelector />

      {/* Animated background blobs */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-gradient-to-r from-cyan-400 to-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse"></div>
        <div className="absolute top-40 right-10 w-96 h-96 bg-gradient-to-r from-yellow-400 to-orange-400 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse animation-delay-2000"></div>
        <div className="absolute bottom-20 left-1/3 w-80 h-80 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse animation-delay-4000"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center min-h-screen">

          {/* Left: Branding & CTA */}
          <div className="text-center lg:text-left">
            <div className="flex items-center justify-center lg:justify-start mb-6">
              <div className="bg-gradient-to-r from-cyan-500 to-blue-500 p-3 rounded-2xl mr-4">
                <Calendar className="w-8 h-8 text-white" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
                NeChaos
              </span>
            </div>

            <h1 className="text-5xl md:text-7xl font-extrabold text-gray-900 mb-8 leading-tight">
              {t('hero.title.part1')}
              <span className="block bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500 bg-clip-text text-transparent">
                {t('hero.title.part2')}
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-600 mb-10 max-w-2xl">
              {t('hero.subtitle')}
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start mb-12">
              <button
                onClick={() => navigate('/login')}
                className="group relative bg-gradient-to-r from-cyan-500 to-blue-500 text-white px-8 py-4 rounded-2xl font-bold text-lg transition-all duration-300 hover:shadow-2xl hover:scale-105"
              >
                <span className="relative z-10 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 mr-2" />
                  {t('hero.cta.tryFree')}
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-600 to-blue-600 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </button>

              <button className="bg-white text-gray-700 px-8 py-4 rounded-2xl font-bold text-lg border-2 border-gray-200 hover:border-cyan-300 hover:shadow-lg transition-all duration-300">
                {t('hero.cta.watchDemo')}
              </button>
            </div>

            <div className="flex items-center justify-center lg:justify-start space-x-8 text-sm text-gray-500">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                {t('hero.features.freeForever')}
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                {t('hero.features.noCard')}
              </div>
            </div>
          </div>

          {/* Right: Mini Chat Preview */}
          <div className="relative">
            <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-md mx-auto">
              <div className="flex items-center mb-6">
                <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="ml-4 text-sm text-gray-500">
                  {t('hero.chatLabel')}
                </span>
              </div>

              <div className="space-y-4 mb-6">
                <div className="flex items-start">
                  <div className="bg-gradient-to-r from-cyan-500 to-blue-500 p-2 rounded-full mr-3 flex-shrink-0">
                    <MessageCircle className="w-4 h-4 text-white" />
                  </div>
                  <div className="bg-gray-100 rounded-2xl px-4 py-3 max-w-sm">
                    <p className="text-sm">{t('hero.chatExample.user')}</p>
                  </div>
                </div>

                <div className="flex items-start justify-end">
                  <div className="bg-gradient-to-r from-cyan-500 to-blue-500 rounded-2xl px-4 py-3 max-w-sm text-white">
                    <p className="text-sm">{t('hero.chatExample.bot')}</p>
                  </div>
                  <div className="bg-gradient-to-r from-cyan-500 to-blue-500 p-2 rounded-full ml-3 flex-shrink-0">
                    <span className="text-white text-sm">🤖</span>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-2xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-sm">
                      {t('hero.chatExample.slotDate')}
                    </span>
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                      {t('hero.chatExample.bestMatch')}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                    <div>🇺🇸 {t('hero.chatExample.newYork')}</div>
                    <div>🇬🇧 {t('hero.chatExample.london')}</div>
                    <div>🇯🇵 {t('hero.chatExample.tokyo')}</div>
                    <div>🇦🇺 {t('hero.chatExample.sydney')}</div>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <button className="bg-gray-100 text-gray-600 px-4 py-2 rounded-lg text-sm hover:bg-gray-200 transition-colors">
                  {t('hero.chatExample.moreOptions')}
                </button>
                <button className="bg-gradient-to-r from-cyan-500 to-blue-500 text-white px-4 py-2 rounded-lg text-sm hover:shadow-lg transition-shadow">
                  {t('hero.chatExample.scheduleNow')}
                </button>
              </div>
            </div>

            {/* Floating icons */}
            <div className="absolute -top-4 -right-4 bg-yellow-400 p-3 rounded-2xl shadow-lg animate-bounce">
              <Clock className="w-6 h-6 text-white" />
            </div>
            <div className="absolute -bottom-4 -left-4 bg-gradient-to-r from-green-400 to-emerald-400 p-3 rounded-2xl shadow-lg animate-pulse">
              <span className="text-white font-bold text-sm">{t('hero.chatExample.powered')}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
