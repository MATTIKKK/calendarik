import React, { useState } from 'react';
import { personalities, PersonalityConfig } from '../../constants/personalities'; 
import { useTranslation } from 'react-i18next';

const PersonalitySelector: React.FC = () => {
  const { t } = useTranslation()

  const [selected, setSelected] = useState<string>('assistant');

  const handlePersonalitySelect = (personality: PersonalityConfig) => {
    setSelected(personality.id);
    localStorage.setItem('selectedPersonality', personality.id);
  };

  return (
    <section className="py-20 bg-white pr-5 pl-5">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            {t("personality.heading")}
            <span className="bg-gradient-to-r from-cyan-500 to-blue-500 bg-clip-text text-transparent"> {t("personality.highlight")}</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {t("personality.subheading")}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          {personalities.map((personality) => {
            const isActive = personality.id === selected
            const name        = t(`personalities.${personality.id}.name`)
            const desc        = t(`personalities.${personality.id}.description`)
            const previewText = t(`personalities.${personality.id}.preview`)

            return <div
              key={personality.id}
              onClick={() => handlePersonalitySelect(personality)}
              className={`relative p-6 rounded-2xl cursor-pointer transition-all duration-300 transform hover:scale-105 hover:shadow-xl ${
                selected === personality.id
                  ? 'shadow-2xl ring-4 ring-cyan-500 ring-opacity-50'
                  : 'shadow-lg hover:shadow-xl'
              }`}
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${personality.color} rounded-2xl opacity-10`}></div>
              <div className="relative z-10 text-center">
                <div className="text-4xl mb-4">{personality.avatar}</div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{name}</h3>
                <p className="text-sm text-gray-600">{desc}</p>
                {selected === personality.id && (
                  <div className="absolute -top-2 -right-2 w-6 h-6 bg-cyan-500 rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </div>
            </div>
          })}
        </div>

        <div className="mt-12 text-center">
          <div className="bg-gradient-to-r from-cyan-50 to-blue-50 rounded-2xl p-8 max-w-4xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              {t(`personality.previewLabel`)}: {t(`personalities.${selected}.name`)}
            </h3>
            <div className="bg-white rounded-xl p-6 shadow-inner">
              <div className="flex items-start space-x-4">
                <div className="text-2xl">
                  {personalities.find(p => p.id === selected)?.avatar}
                </div>
                <div className="flex-1 text-left">
                  <div className="bg-gray-100 rounded-2xl px-4 py-3 inline-block">
                    <p className="text-gray-800">
                      {selected === 'assistant' && t(`previewMessages.${selected}`)}
                      {selected === 'coach' && t(`previewMessages.${selected}`)}
                      {selected === 'friend' && t(`previewMessages.${selected}`)}
                      {selected === 'girlfriend' && t(`previewMessages.${selected}`)}
                      {selected === 'boyfriend' && t(`previewMessages.${selected}`)}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PersonalitySelector;