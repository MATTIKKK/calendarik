import React from 'react';
import { Check, Star } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const Pricing: React.FC = () => {
  const { t } = useTranslation();

  // pull the plans data (with name, price, features, etc.) from translations
  const plans = t('pricing.plans', { returnObjects: true }) as Array<{
    name: string;
    price: string;
    period: string;
    popular?: boolean;
    features: string[];
  }>;

  const benefits = t('pricing.benefits', { returnObjects: true }) as string[];

  return (
    <section className="py-20 bg-white pr-5 pl-5">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Heading */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            {t('pricing.heading')}{' '}
            <span className="bg-gradient-to-r from-cyan-500 to-blue-500 bg-clip-text text-transparent">
              {t('pricing.highlight')}
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {t('pricing.subheading')}
          </p>
        </div>

        {/* Plans */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {plans.map((plan, idx) => (
            <div
              key={idx}
              className={`
                relative bg-white rounded-3xl shadow-lg border-2 transition-all duration-300 hover:shadow-2xl hover:scale-105
                ${plan.popular ? 'border-cyan-500 ring-4 ring-cyan-100' : 'border-gray-200'}
              `}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <div className="bg-gradient-to-r from-cyan-500 to-blue-500 text-white px-4 py-2 rounded-full text-sm font-bold flex items-center">
                    <Star className="w-4 h-4 mr-1" />
                    {t('pricing.popularBadge')}
                  </div>
                </div>
              )}
              <div className="p-8">
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">
                    {plan.name}
                  </h3>
                  <div className="flex items-baseline justify-center">
                    <span className="text-5xl font-extrabold text-gray-900">
                      {plan.price}
                    </span>
                    <span className="text-xl text-gray-500 ml-2">
                      /{plan.period}
                    </span>
                  </div>
                </div>
                <ul className="space-y-4 mb-8">
                  {plan.features.map((f, i) => (
                    <li key={i} className="flex items-center">
                      <div
                        className={`
                          w-5 h-5 bg-gradient-to-r ${
                            plan.popular
                              ? 'from-cyan-500 to-blue-500'
                              : 'from-gray-500 to-gray-600'
                          } rounded-full flex items-center justify-center mr-3 flex-shrink-0
                        `}
                      >
                        <Check className="w-3 h-3 text-white" />
                      </div>
                      <span className="text-gray-700">{f}</span>
                    </li>
                  ))}
                </ul>
                <button
                  className={`
                    w-full py-4 rounded-2xl font-bold text-lg transition-all duration-300
                    ${
                      plan.popular
                        ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white hover:shadow-lg transform hover:scale-105'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }
                  `}
                >
                  {plan.popular
                    ? t('pricing.button.pro')
                    : t('pricing.button.free')}
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Note + Benefits */}
        <div className="mt-16 text-center">
          <p className="text-gray-600 mb-8">{t('pricing.note')}</p>
          <div
            className="
              flex flex-col md:flex-row 
              items-center justify-center 
              text-sm text-gray-500
              space-y-4 md:space-y-0 md:space-x-8
            "
          >
            {benefits.map((b, i) => (
              <div key={i} className="flex items-center">
                <div
                  className={`
                    w-2 h-2 rounded-full mr-2 
                    ${i === 0 ? 'bg-green-500' : i === 1 ? 'bg-blue-500' : 'bg-purple-500'}
                  `}
                ></div>
                {b}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Pricing;
