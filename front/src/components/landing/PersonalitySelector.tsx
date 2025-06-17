import React, { useState } from 'react';
import { personalities } from '../../constants/personalities';
import { AssistantPersonality } from '../../types/landing';

const PersonalitySelector: React.FC = () => {
  const [selectedPersonality, setSelectedPersonality] = useState<string>('assistant');

  const handlePersonalitySelect = (personality: AssistantPersonality) => {
    setSelectedPersonality(personality.id);
    // Here you would typically save to localStorage or make an API call
    localStorage.setItem('selectedPersonality', personality.id);
  };

  return (
    <section className="py-20 bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Choose Your AI Assistant's
            <span className="bg-gradient-to-r from-cyan-500 to-blue-500 bg-clip-text text-transparent"> Personality</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Select how your personal AI assistant will communicate with you: professional, motivational, friendly, or caring 💖
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          {personalities.map((personality) => (
            <div
              key={personality.id}
              onClick={() => handlePersonalitySelect(personality)}
              className={`relative p-6 rounded-2xl cursor-pointer transition-all duration-300 transform hover:scale-105 hover:shadow-xl ${
                selectedPersonality === personality.id
                  ? 'shadow-2xl ring-4 ring-cyan-500 ring-opacity-50'
                  : 'shadow-lg hover:shadow-xl'
              }`}
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${personality.color} rounded-2xl opacity-10`}></div>
              <div className="relative z-10 text-center">
                <div className="text-4xl mb-4">{personality.avatar}</div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{personality.name}</h3>
                <p className="text-sm text-gray-600">{personality.description}</p>
                {selectedPersonality === personality.id && (
                  <div className="absolute -top-2 -right-2 w-6 h-6 bg-cyan-500 rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <div className="bg-gradient-to-r from-cyan-50 to-blue-50 rounded-2xl p-8 max-w-4xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Preview: {personalities.find(p => p.id === selectedPersonality)?.name}
            </h3>
            <div className="bg-white rounded-xl p-6 shadow-inner">
              <div className="flex items-start space-x-4">
                <div className="text-2xl">
                  {personalities.find(p => p.id === selectedPersonality)?.avatar}
                </div>
                <div className="flex-1 text-left">
                  <div className="bg-gray-100 rounded-2xl px-4 py-3 inline-block">
                    <p className="text-gray-800">
                      {selectedPersonality === 'assistant' && "I've found 3 optimal time slots for your team meeting. Shall I send the invitations?"}
                      {selectedPersonality === 'coach' && "You've got this! I found some amazing time slots that'll work perfectly for everyone. Ready to crush this meeting?"}
                      {selectedPersonality === 'friend' && "Hey! Found some great times for your meeting. Want me to set it up for you?"}
                      {selectedPersonality === 'girlfriend' && "Hi sweetie! I found some perfect times for your meeting. I made sure to leave buffer time so you won't be stressed 💕"}
                      {selectedPersonality === 'boyfriend' && "Hey babe, got your meeting sorted. I blocked out some extra time before so you can prep properly ❤️"}
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