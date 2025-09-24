'use client';

import Link from 'next/link';
import { useLocale } from 'next-intl';

export function EventsSection() {
  const locale = useLocale();

  return (
    <div className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Aankomende Evenementen
          </h2>
          <p className="text-lg text-gray-600">
            Ontdek interessante evenementen die worden georganiseerd door onze aangesloten moskeeën
          </p>
        </div>

        {/* Empty State */}
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Geen evenementen gepland</h3>
          <p className="text-gray-500 mb-6">
            Er zijn momenteel geen evenementen gepland. Nieuwe evenementen worden hier weergegeven zodra ze beschikbaar zijn.
          </p>
          <Link
            href={`/${locale}/events`}
            className="inline-flex items-center px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
          >
            Alle evenementen bekijken
          </Link>
        </div>
      </div>
    </div>
  );
}
