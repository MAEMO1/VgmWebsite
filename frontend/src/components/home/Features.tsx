'use client';

import { useTranslations } from 'next-intl';
import { 
  MapPinIcon, 
  CalendarIcon, 
  HeartIcon, 
  BellIcon,
  UsersIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';

export function Features() {
  const t = useTranslations('Features');

  const features = [
    {
      icon: MapPinIcon,
      title: t('mosqueDirectory.title'),
      description: t('mosqueDirectory.description'),
    },
    {
      icon: CalendarIcon,
      title: t('events.title'),
      description: t('events.description'),
    },
    {
      icon: HeartIcon,
      title: t('donations.title'),
      description: t('donations.description'),
    },
    {
      icon: BellIcon,
      title: t('notifications.title'),
      description: t('notifications.description'),
    },
    {
      icon: UsersIcon,
      title: t('community.title'),
      description: t('community.description'),
    },
    {
      icon: GlobeAltIcon,
      title: t('multilingual.title'),
      description: t('multilingual.description'),
    },
  ];

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
          {features.map((feature, index) => (
            <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-200">
              <div className="flex items-center mb-4">
                <div className="flex-shrink-0">
                  <feature.icon className="h-8 w-8 text-primary-600" />
                </div>
                <h3 className="ml-3 text-lg font-semibold text-gray-900">
                  {feature.title}
                </h3>
              </div>
              <p className="text-gray-600">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
