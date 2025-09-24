'use client';

import Link from 'next/link';
import { useLocale } from 'next-intl';

export function MosquesSection() {
  const locale = useLocale();

  const mosques = [
    {
      name: 'Moskee Salahaddien',
      address: 'Sint-Pietersnieuwstraat 120, Gent',
      events: 12,
      image: '/api/placeholder/400/200'
    },
    {
      name: 'Moskee Al-Fath',
      address: 'Korte Meer 11, Gent',
      events: 8,
      image: '/api/placeholder/400/200'
    },
    {
      name: 'Moskee Selimiye',
      address: 'Kasteellaan 15, Gent',
      events: 6,
      image: '/api/placeholder/400/200'
    }
  ];

  return (
    <div className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Moskeeën in Gent
          </h2>
          <p className="text-lg text-gray-600">
            Ontdek alle aangesloten moskeeën en hun diensten
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          {mosques.map((mosque, index) => (
            <div key={index} className="bg-white border border-gray-200 rounded-2xl overflow-hidden hover:shadow-lg transition-shadow">
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
                  <svg className="w-4 h-4 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <span className="text-sm text-gray-600">{mosque.address}</span>
                </div>
                
                <div className="flex items-center mb-4">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-teal-100 text-teal-800">
                    {mosque.events} evenementen
                  </span>
                </div>
                
                <Link
                  href={`/${locale}/mosques/${mosque.name.toLowerCase().replace(/\s+/g, '-')}`}
                  className="inline-flex items-center px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
                >
                  Meer informatie
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
            Alle moskeeën bekijken
          </Link>
        </div>
      </div>
    </div>
  );
}
