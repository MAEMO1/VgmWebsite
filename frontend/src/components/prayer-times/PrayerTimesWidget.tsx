'use client';

import { useTodayPrayerTimes } from '@/hooks/usePrayerTimes';
import { getCurrentPrayerStatus, getNextPrayerTime } from '@/lib/prayer-times';
import { ClockIcon, SunIcon, MoonIcon } from '@heroicons/react/24/outline';
import { Skeleton } from '@/components/ui/Skeleton';

export function PrayerTimesWidget() {
  const { data: prayerTimesResponse, isLoading, error } = useTodayPrayerTimes();

  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Gebedstijden</h3>
          <Skeleton className="h-6 w-16" />
        </div>
        <div className="space-y-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="flex items-center justify-between">
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-4 w-12" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !prayerTimesResponse?.success || !prayerTimesResponse.data) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Gebedstijden</h3>
          <span className="text-xs text-gray-500">
            {prayerTimesResponse?.source === 'calculation' ? 'Berekend' : 'Vandaag'}
          </span>
        </div>
        <div className="text-center py-4">
          <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-2">
            <ClockIcon className="w-6 h-6 text-red-600" />
          </div>
          <p className="text-sm text-gray-600">
            Gebedstijden niet beschikbaar
          </p>
        </div>
      </div>
    );
  }

  const prayerTimes = prayerTimesResponse.data;
  const currentStatus = getCurrentPrayerStatus(prayerTimes);
  const nextPrayerTimes = getNextPrayerTime(prayerTimes);

  const prayerIcons = {
    Fajr: <MoonIcon className="w-4 h-4 text-blue-600" />,
    Sunrise: <SunIcon className="w-4 h-4 text-yellow-600" />,
    Dhuhr: <SunIcon className="w-4 h-4 text-orange-600" />,
    Asr: <SunIcon className="w-4 h-4 text-orange-500" />,
    Maghrib: <SunIcon className="w-4 h-4 text-red-600" />,
    Isha: <MoonIcon className="w-4 h-4 text-indigo-600" />
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Gebedstijden</h3>
        <div className="text-right">
          <span className="text-xs text-gray-500">
            {prayerTimesResponse.source === 'diyanet' ? 'Diyanet' : 'Berekend'}
          </span>
          <div className="text-xs text-gray-400">
            {new Date(prayerTimes.date).toLocaleDateString('nl-NL')}
          </div>
        </div>
      </div>

      {/* Current Status */}
      {currentStatus.current && (
        <div className="mb-4 p-3 bg-teal-50 rounded-lg border border-teal-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-teal-900">
                Huidige gebed: {currentStatus.current}
              </p>
              {currentStatus.next && (
                <p className="text-xs text-teal-700">
                  Volgende: {currentStatus.next}
                  {currentStatus.timeUntilNext && ` (${currentStatus.timeUntilNext})`}
                </p>
              )}
            </div>
            <ClockIcon className="w-5 h-5 text-teal-600" />
          </div>
        </div>
      )}

      {/* Prayer Times List */}
      <div className="space-y-3">
        {nextPrayerTimes.map((prayer) => (
          <div
            key={prayer.name}
            className={`flex items-center justify-between p-2 rounded-lg transition-colors ${
              prayer.isNext
                ? 'bg-teal-50 border border-teal-200'
                : 'hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center space-x-3">
              {prayerIcons[prayer.name as keyof typeof prayerIcons]}
              <span className={`text-sm font-medium ${
                prayer.isNext ? 'text-teal-900' : 'text-gray-900'
              }`}>
                {prayer.name}
              </span>
            </div>
            <span className={`text-sm font-mono ${
              prayer.isNext ? 'text-teal-700' : 'text-gray-600'
            }`}>
              {prayer.time}
            </span>
          </div>
        ))}
      </div>

      {/* Source Info */}
      <div className="mt-4 pt-3 border-t border-gray-100">
        <p className="text-xs text-gray-500 text-center">
          {prayerTimesResponse.source === 'diyanet' 
            ? 'Gegevens van Diyanet İşleri Başkanlığı'
            : 'Berekend volgens ISNA methode'
          }
        </p>
      </div>
    </div>
  );
}
