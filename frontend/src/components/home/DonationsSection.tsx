'use client';

import Link from 'next/link';
import { useLocale } from 'next-intl';

export function DonationsSection() {
  const locale = useLocale();

  return (
    <div className="py-16 bg-teal-50">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Fondsenwervingscampagnes
          </h2>
          <p className="text-lg text-gray-600">
            Steun onze gemeenschap door bij te dragen aan belangrijke campagnes
          </p>
        </div>

        {/* Empty State */}
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Geen campagnes actief</h3>
          <p className="text-gray-500 mb-6">
            Er zijn momenteel geen fondsenwervingscampagnes actief. Nieuwe campagnes worden hier weergegeven zodra ze beschikbaar zijn.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href={`/${locale}/donations`}
              className="inline-flex items-center px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
            >
              Algemene donaties
            </Link>
            <Link
              href={`/${locale}/donations/campaigns`}
              className="inline-flex items-center px-6 py-3 bg-white text-teal-600 border-2 border-teal-600 rounded-lg hover:bg-teal-50 transition-colors"
            >
              Alle campagnes bekijken
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
