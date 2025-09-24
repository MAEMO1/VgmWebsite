'use client';

import Link from 'next/link';
import { useLocale } from 'next-intl';

export function NewsSection() {
  const locale = useLocale();

  return (
    <div className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Laatste Nieuws
          </h2>
          <p className="text-lg text-gray-600">
            Blijf op de hoogte van het laatste nieuws en aankondigingen
          </p>
        </div>

        {/* Empty State */}
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Geen nieuws</h3>
          <p className="text-gray-500 mb-6">
            Er zijn momenteel geen nieuwsartikelen beschikbaar.
          </p>
          <Link
            href={`/${locale}/news`}
            className="inline-flex items-center px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
          >
            Alle nieuws bekijken
          </Link>
        </div>
      </div>
    </div>
  );
}
