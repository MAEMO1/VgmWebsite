'use client';

import { useTranslations } from 'next-intl';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { CalendarIcon, MapPinIcon, ClockIcon, UserIcon } from '@heroicons/react/24/outline';

export default function JanazahPage() {
  const t = useTranslations('Janazah');

  // Mock data - in real app this would come from API
  const janazahPrayers = [
    {
      id: 1,
      name: 'Ahmed Al-Rashid',
      age: 67,
      deathDate: '2024-01-15',
      prayerDate: '2024-01-16',
      prayerTime: '14:00',
      mosque: 'Centrale Moskee Gent',
      mosqueAddress: 'Kortrijksesteenweg 123, 9000 Gent',
      cemetery: 'Begraafplaats Gent',
      notes: 'Familie vraagt om bloemen te vermijden'
    },
    {
      id: 2,
      name: 'Fatima Hassan',
      age: 45,
      deathDate: '2024-01-14',
      prayerDate: '2024-01-15',
      prayerTime: '15:30',
      mosque: 'Moskee Al-Hidayah',
      mosqueAddress: 'Bruggestraat 45, 9000 Gent',
      cemetery: 'Begraafplaats Gent',
      notes: 'Vrouwenafdeling beschikbaar'
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Breadcrumbs items={[
        { name: 'Gemeenschap', href: '/community' },
        { name: 'Begrafenisgebeden' }
      ]} />
      
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Begrafenisgebeden (Janazah)
          </h1>
          <p className="text-gray-600 text-lg">
            Informatie over aankomende begrafenisgebeden in de moskeeën van Gent.
          </p>
        </div>

        {/* Search and Filter */}
        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Zoeken
              </label>
              <input
                type="text"
                placeholder="Naam van overledene..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Moskee
              </label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>Alle moskeeën</option>
                <option>Centrale Moskee Gent</option>
                <option>Moskee Al-Hidayah</option>
                <option>Moskee Al-Noor</option>
              </select>
            </div>
            <div className="flex items-end">
              <button className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                Filter
              </button>
            </div>
          </div>
        </div>

        {/* Janazah Prayers List */}
        <div className="space-y-6">
          {janazahPrayers.map((prayer) => (
            <div key={prayer.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
              <div className="flex flex-col md:flex-row md:items-start md:justify-between">
                <div className="flex-1">
                  <div className="flex items-center mb-4">
                    <UserIcon className="h-6 w-6 text-gray-400 mr-3" />
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900">
                        {prayer.name}
                      </h3>
                      <p className="text-gray-600">
                        {prayer.age} jaar oud
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div className="flex items-center text-gray-600">
                      <CalendarIcon className="h-5 w-5 mr-2" />
                      <span>Overleden: {new Date(prayer.deathDate).toLocaleDateString('nl-NL')}</span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <ClockIcon className="h-5 w-5 mr-2" />
                      <span>Gebed: {new Date(prayer.prayerDate).toLocaleDateString('nl-NL')} om {prayer.prayerTime}</span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <MapPinIcon className="h-5 w-5 mr-2" />
                      <span>{prayer.mosque}</span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <MapPinIcon className="h-5 w-5 mr-2" />
                      <span>{prayer.cemetery}</span>
                    </div>
                  </div>

                  {prayer.notes && (
                    <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                      <p className="text-blue-800 text-sm">
                        <strong>Opmerkingen:</strong> {prayer.notes}
                      </p>
                    </div>
                  )}
                </div>

                <div className="mt-4 md:mt-0 md:ml-6">
                  <button className="bg-gray-900 text-white px-6 py-2 rounded-md hover:bg-gray-800 transition-colors">
                    Meer Details
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Call to Action */}
        <div className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            Begrafenisgebed Melden
          </h3>
          <p className="text-gray-600 mb-6">
            Heeft u een begrafenisgebed dat gemeld moet worden? Neem contact op met de betreffende moskee.
          </p>
          <button className="bg-blue-600 text-white px-8 py-3 rounded-md hover:bg-blue-700 transition-colors">
            Begrafenisgebed Melden
          </button>
        </div>
      </div>
    </div>
  );
}
