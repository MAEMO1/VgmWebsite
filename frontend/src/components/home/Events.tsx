'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { useLocale } from 'next-intl';
import { CalendarIcon, ClockIcon, MapPinIcon } from '@heroicons/react/24/outline';

export function Events() {
  const t = useTranslations('Events');
  const locale = useLocale();

  return (
    <div className="py-16 bg-gray-50">
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
          {/* Placeholder event cards */}
          {[1, 2, 3].map((index) => (
            <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-200">
              <div className="flex items-center mb-4">
                <CalendarIcon className="h-5 w-5 text-primary-600 mr-2" />
                <span className="text-sm font-medium text-gray-900">
                  {t(`event${index}.date`)}
                </span>
              </div>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {t(`event${index}.title`)}
              </h3>
              
              <p className="text-gray-600 mb-4">
                {t(`event${index}.description`)}
              </p>
              
              <div className="space-y-2 text-sm text-gray-500">
                <div className="flex items-center">
                  <ClockIcon className="h-4 w-4 mr-2" />
                  <span>{t(`event${index}.time`)}</span>
                </div>
                <div className="flex items-center">
                  <MapPinIcon className="h-4 w-4 mr-2" />
                  <span>{t(`event${index}.location`)}</span>
                </div>
              </div>
              
              <div className="mt-4">
                <Link
                  href={`/${locale}/events/event-${index}`}
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
            href={`/${locale}/events`}
            className="bg-primary-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors duration-200"
          >
            {t('viewAll')}
          </Link>
        </div>
      </div>
    </div>
  );
}
