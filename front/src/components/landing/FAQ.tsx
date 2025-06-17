import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { faqItems } from '../../constants/content';

const FAQ: React.FC = () => {
  const [openItems, setOpenItems] = useState<number[]>([]);

  const toggleItem = (index: number) => {
    setOpenItems(prev => 
      prev.includes(index) 
        ? prev.filter(i => i !== index)
        : [...prev, index]
    );
  };

  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-white">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Frequently Asked
            <span className="bg-gradient-to-r from-cyan-500 to-blue-500 bg-clip-text text-transparent"> Questions</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Got questions? We've got answers. Here are the most common questions about Calendarik.
          </p>
        </div>

        <div className="space-y-4">
          {faqItems.map((item, index) => (
            <div key={index} className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
              <button
                onClick={() => toggleItem(index)}
                className="w-full px-8 py-6 text-left flex items-center justify-between hover:bg-gray-50 transition-colors duration-200"
              >
                <h3 className="text-lg font-semibold text-gray-900 pr-4">{item.question}</h3>
                {openItems.includes(index) ? (
                  <ChevronUp className="w-5 h-5 text-cyan-500 flex-shrink-0" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
                )}
              </button>
              
              {openItems.includes(index) && (
                <div className="px-8 pb-6">
                  <div className="border-t border-gray-100 pt-6">
                    <p className="text-gray-600 leading-relaxed">{item.answer}</p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="mt-16 text-center">
          <div className="bg-gradient-to-r from-cyan-50 to-blue-50 rounded-3xl p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Still have questions?</h3>
            <p className="text-gray-600 mb-6">Our support team is here to help you get the most out of Calendarik.</p>
            <button className="bg-gradient-to-r from-cyan-500 to-blue-500 text-white px-8 py-4 rounded-2xl font-bold text-lg hover:shadow-lg transition-all duration-300">
              Contact Support
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FAQ;