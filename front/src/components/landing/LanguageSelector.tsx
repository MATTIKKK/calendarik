import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'

const LanguageSelector: React.FC = () => {
  const { i18n } = useTranslation();
  const langs = [
    { code: 'en', label: 'EN' },
    { code: 'ru', label: 'RU' },
    { code: 'kz', label: 'KZ' },
  ];
  const saved = localStorage.getItem('lang') || i18n.language
  const initialIndex = langs.findIndex(l => l.code === saved)
  const [activeIndex, setActiveIndex] = useState(
    initialIndex >= 0 ? initialIndex : 0
  ) 

  const changeLanguage = (lang: string) => {
    console.log('changeLanguage', lang)
    i18n.changeLanguage(lang)
    localStorage.setItem('lang', lang)
    setActiveIndex(langs.findIndex(l => l.code === lang))
  }

  useEffect(() => {
    const idx = langs.findIndex(l => l.code === i18n.language)
    if (idx >= 0) setActiveIndex(idx)
  }, [i18n.language])

  return (
    <div className="absolute top-4 right-4 flex space-x-1  rounded-lg p-1 text-xs backdrop-blur-sm z-20">
      {langs.map(l => {
        const isActive = i18n.language === l.code;
        return (
          <button
            key={l.code}
            onClick={() => changeLanguage(l.code)}
            className={`
              px-2 py-0.5 rounded transition-colors duration-200 font-bold cursor-pointer
              ${isActive
                ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white'
                : 'text-gray-600 hover:bg-gray-200 hover:text-gray-800'}
            `}
          >
            {l.label}
          </button>
        );
      })}
    </div>
  );
};

export default LanguageSelector;
