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
    <div className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            {t('title')}
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {t('subtitle')}
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="bg-white border border-gray-200 rounded-2xl p-8 hover:shadow-lg transition-shadow duration-200">
              <div className="flex items-start mb-6">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-teal-100 rounded-xl flex items-center justify-center">
                    <feature.icon className="h-6 w-6 text-teal-600" />
                  </div>
                </div>
                <h3 className="ml-4 text-lg font-semibold text-gray-900">
                  {feature.title}
                </h3>
              </div>
              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
