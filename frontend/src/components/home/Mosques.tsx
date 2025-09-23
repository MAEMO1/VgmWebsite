'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { useLocale } from 'next-intl';

export function Mosques() {
  const t = useTranslations('Mosques');
  const locale = useLocale();

  return (
    <div className="py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            {t('title')}
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {t('subtitle')}
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* Placeholder mosque cards */}
          {[1, 2, 3].map((index) => (
            <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow duration-200">
              <div className="h-48 bg-gray-200"></div>
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {t(`mosque${index}.name`)}
                </h3>
                <p className="text-gray-600 mb-4">
                  {t(`mosque${index}.description`)}
                </p>
                <div className="flex items-center text-sm text-gray-500 mb-4">
                  <span>{t(`mosque${index}.address`)}</span>
                </div>
                <Link
                  href={`/${locale}/mosques/mosque-${index}`}
                  className="text-primary-600 hover:text-primary-700 font-medium"
                >
                  {t('learnMore')} →
                </Link>
              </div>
            </div>
          ))}
        </div>
        
        <div className="text-center mt-12">
          <Link
            href={`/${locale}/mosques`}
            className="bg-primary-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors duration-200"
          >
            {t('viewAll')}
          </Link>
        </div>
      </div>
    </div>
  );
}
