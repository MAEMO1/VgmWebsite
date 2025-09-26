'use client';

import Link from 'next/link';
import { useLocale } from 'next-intl';
import { useTranslations } from 'next-intl';
import { useMosques } from '@/hooks/useApi';
import { MapPinIcon, UsersIcon, CalendarIcon } from '@heroicons/react/24/outline';
import { SectionErrorBoundary } from '@/components/ErrorBoundary';

export function MosquesSection() {
  const locale = useLocale();
  const t = useTranslations('Home');
  const { data: mosques, isLoading, error } = useMosques();

  return (
    <SectionErrorBoundary sectionName="Moskeeën">
      <MosquesSectionContent 
        locale={locale} 
        t={t} 
        mosques={mosques} 
        isLoading={isLoading} 
        error={error} 
      />
    </SectionErrorBoundary>
  );
}

function MosquesSectionContent({ 
  locale, 
  t, 
  mosques, 
  isLoading, 
  error 
}: {
  locale: string;
  t: any;
  mosques: any;
  isLoading: boolean;
  error: any;
}) {

  if (isLoading) {
    return (
      <div className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              {t('mosques.title')}
            </h2>
            <p className="text-lg text-gray-600">
              {t('mosques.description')}
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white border border-gray-200 rounded-2xl overflow-hidden animate-pulse">
                <div className="h-48 bg-gray-200"></div>
                <div className="p-6">
                  <div className="h-6 bg-gray-200 rounded mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded mb-3"></div>
                  <div className="h-8 bg-gray-200 rounded"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              {t('mosques.title')}
            </h2>
            <p className="text-lg text-red-600">
              {t('mosques.error')}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            {t('mosques.title')}
          </h2>
          <p className="text-lg text-gray-600">
            {t('mosques.description')}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          {mosques?.slice(0, 6).map((mosque) => (
            <div key={mosque.id} className="bg-white border border-gray-200 rounded-2xl overflow-hidden hover:shadow-lg transition-shadow">
              {/* Mosque Image Placeholder */}
              <div className="h-48 bg-gray-200 flex items-center justify-center">
                <div className="w-20 h-20 bg-teal-100 rounded-full flex items-center justify-center">
                  <svg className="w-10 h-10 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
              </div>
              
              <div className="p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {mosque.name}
                </h3>
                
                <div className="flex items-center mb-3">
                  <MapPinIcon className="w-4 h-4 text-gray-400 mr-2" />
                  <span className="text-sm text-gray-600">{mosque.address}</span>
                </div>
                
                <div className="space-y-2 text-sm text-gray-600 mb-4">
                  {mosque.capacity && (
                    <div className="flex items-center">
                      <UsersIcon className="w-4 h-4 mr-2" />
                      <span>{mosque.capacity} {t('mosques.capacity')}</span>
                    </div>
                  )}
                  {mosque.established_year && (
                    <div className="flex items-center">
                      <CalendarIcon className="w-4 h-4 mr-2" />
                      <span>{mosque.established_year} {t('mosques.established')}</span>
                    </div>
                  )}
                </div>
                
                <Link
                  href={`/${locale}/mosques/${mosque.id}`}
                  className="inline-flex items-center px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
                >
                  {t('mosques.viewDetails')}
                </Link>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center">
          <Link
            href={`/${locale}/mosques`}
            className="inline-flex items-center px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
          >
            {t('mosques.viewAll')}
          </Link>
        </div>
      </div>
    </div>
  );
}
