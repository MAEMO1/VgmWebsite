'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { useLocale } from 'next-intl';
import { PrayerTimesWidget } from '@/components/prayer-times/PrayerTimesWidget';

export function Hero() {
  const t = useTranslations('Hero');
  const locale = useLocale();

  return (
    <div className="bg-teal-600 text-white">
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-center">
          {/* Left Content */}
          <div className="lg:col-span-2 text-center lg:text-left">
            {/* Main Title */}
            <h1 className="text-5xl md:text-6xl font-bold mb-6 text-white">
              Vereniging van Gentse Moskeeën
            </h1>
            
            <p className="text-xl text-teal-100 mb-12 max-w-3xl mx-auto leading-relaxed">
              Uw centrale platform voor moskee-informatie, evenementen en gemeenschapsdiensten in Gent
            </p>
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Link
                href={`/${locale}/mosques`}
                className="bg-white text-teal-600 px-8 py-4 rounded-xl font-semibold hover:bg-teal-50 transition-colors duration-200 shadow-lg hover:shadow-xl"
              >
                Ontdek Moskeeën
              </Link>
              <Link
                href={`/${locale}/events`}
                className="bg-transparent text-white border-2 border-white px-8 py-4 rounded-xl font-semibold hover:bg-white hover:text-teal-600 transition-colors duration-200 shadow-lg hover:shadow-xl"
              >
                Bekijk Evenementen
              </Link>
            </div>
          </div>
          
          {/* Right Content - Prayer Times */}
          <div className="lg:col-span-1">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6">
              <PrayerTimesWidget />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
