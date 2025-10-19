'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslations } from 'next-intl';
import { ClockIcon, MapPinIcon, CalendarIcon } from '@heroicons/react/24/outline';
import { apiClient } from '@/api/client';
import { ErrorState } from '@/components/ui/ErrorState';

interface PrayerTime {
  id: number;
  mosque_id: number;
  date: string;
  fajr: string;
  dhuhr: string;
  asr: string;
  maghrib: string;
  isha: string;
}

interface Mosque {
  id: number;
  name: string;
  address: string;
  latitude: number;
  longitude: number;
}

export function PrayerTimesPage() {
  const t = useTranslations('PrayerTimes');
  const [selectedMosque, setSelectedMosque] = useState<number | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);

  // Fetch mosques
  const { data: mosques = [], isLoading: mosquesLoading } = useQuery<Mosque[]>({
    queryKey: ['mosques'],
    queryFn: () => apiClient.get<Mosque[]>('/api/mosques'),
    refetchOnWindowFocus: false,
  });

  // Fetch prayer times
  const { data: prayerTimes, isLoading: prayerTimesLoading, isError: prayerTimesError } = useQuery<PrayerTime>({
    queryKey: ['prayer-times', selectedMosque, selectedDate],
    queryFn: () => apiClient.get<PrayerTime>(`/api/prayer-times?mosque_id=${selectedMosque}&date=${selectedDate}`),
    enabled: !!selectedMosque,
    refetchOnWindowFocus: false,
  });

  // Auto-select first mosque if available
  useEffect(() => {
    if (mosques.length > 0 && !selectedMosque) {
      setSelectedMosque(mosques[0].id);
    }
  }, [mosques, selectedMosque]);

  const prayerNames = [
    { key: 'fajr', name: 'Fajr', time: prayerTimes?.fajr },
    { key: 'dhuhr', name: 'Dhuhr', time: prayerTimes?.dhuhr },
    { key: 'asr', name: 'Asr', time: prayerTimes?.asr },
    { key: 'maghrib', name: 'Maghrib', time: prayerTimes?.maghrib },
    { key: 'isha', name: 'Isha', time: prayerTimes?.isha },
  ];

  const selectedMosqueData = mosques.find(m => m.id === selectedMosque);

  if (mosquesLoading) {
    return (
      <div className="min-h-screen bg-white">
        <div className="max-w-6xl mx-auto px-6 py-8">
          <div className="flex items-center justify-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" aria-label="Gebedstijden worden geladen" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Gebedstijden
            </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Bekijk de dagelijkse gebedstijden voor alle VGM moskeeën in Gent
          </p>
        </div>

        {/* Controls */}
        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Mosque Selection */}
            <div>
              <label htmlFor="mosque-select" className="block text-sm font-medium text-gray-700 mb-2">
                <MapPinIcon className="inline w-4 h-4 mr-1" />
                Selecteer Moskee
              </label>
              <select
                id="mosque-select"
                value={selectedMosque || ''}
                onChange={(e) => setSelectedMosque(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
              >
                <option value="">Selecteer een moskee</option>
                {mosques.map((mosque) => (
                  <option key={mosque.id} value={mosque.id}>
                    {mosque.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Date Selection */}
            <div>
              <label htmlFor="date-select" className="block text-sm font-medium text-gray-700 mb-2">
                <CalendarIcon className="inline w-4 h-4 mr-1" />
                Selecteer Datum
              </label>
              <input
                type="date"
                id="date-select"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
              />
          </div>
        </div>
      </div>

        {/* Prayer Times Display */}
        {selectedMosque && (
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            {/* Mosque Info */}
            {selectedMosqueData && (
              <div className="bg-primary text-white p-6">
                <h2 className="text-2xl font-bold mb-2">{selectedMosqueData.name}</h2>
                <p className="text-primary-100">{selectedMosqueData.address}</p>
              </div>
            )}

            {/* Prayer Times */}
            <div className="p-6">
              {prayerTimesLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
                </div>
              ) : prayerTimesError ? (
                <ErrorState
                  title="Gebedstijden laden mislukt"
                  message="Het laden van gebedstijden is mislukt. Probeer het later opnieuw."
                  tone="critical"
                />
              ) : prayerTimes ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                  {prayerNames.map((prayer) => (
                    <div
                      key={prayer.key}
                      className="bg-gray-50 rounded-lg p-4 text-center"
                    >
                      <div className="flex items-center justify-center mb-2">
                        <ClockIcon className="w-5 h-5 text-primary mr-2" />
                <h3 className="text-lg font-semibold text-gray-900">
                          {prayer.name}
                </h3>
              </div>
                      <div className="text-2xl font-bold text-primary">
                        {prayer.time}
                      </div>
                </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500">Geen gebedstijden beschikbaar voor de geselecteerde datum.</p>
                </div>
              )}
            </div>

            {/* Additional Info */}
            <div className="bg-gray-50 px-6 py-4 border-t">
              <div className="text-sm text-gray-600 text-center">
                <p className="mb-2">
                  <strong>Let op:</strong> Gebedstijden zijn berekend op basis van de locatie van de moskee.
                </p>
                <p>
                  Voor de meest accurate tijden, raadpleeg de lokale moskee of gebruik een betrouwbare gebedstijden app.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Instructions */}
        {!selectedMosque && (
          <div className="text-center py-12">
            <ClockIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Selecteer een moskee
            </h3>
            <p className="text-gray-600">
              Kies een moskee uit de lijst om de gebedstijden te bekijken.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}