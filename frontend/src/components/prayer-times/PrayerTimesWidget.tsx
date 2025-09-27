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
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 hover:shadow-xl transition-all duration-300">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-gradient-to-r from-teal-500 to-teal-600 rounded-full flex items-center justify-center">
            <ClockIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-2xl font-bold text-gray-900">Gebedstijden</h3>
            <p className="text-sm text-gray-500">
              {new Date(prayerTimes.date).toLocaleDateString('nl-NL', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </p>
          </div>
        </div>
        <div className="text-right">
          <div className="px-3 py-1 bg-teal-100 text-teal-800 rounded-full text-xs font-semibold">
            {prayerTimesResponse.source === 'diyanet' ? 'Diyanet' : 'Berekend'}
          </div>
        </div>
      </div>

      {/* Current Status */}
      {currentStatus.current && (
        <div className="mb-6 p-4 bg-gradient-to-r from-teal-50 to-teal-100 rounded-xl border border-teal-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-teal-900">
                Huidige gebed: {currentStatus.current}
              </p>
              {currentStatus.next && (
                <p className="text-xs text-teal-700 mt-1">
                  Volgende: {currentStatus.next}
                  {currentStatus.timeUntilNext && ` (${currentStatus.timeUntilNext})`}
                </p>
              )}
            </div>
            <div className="w-10 h-10 bg-teal-500 rounded-full flex items-center justify-center">
              <ClockIcon className="w-5 h-5 text-white" />
            </div>
          </div>
        </div>
      )}

      {/* Prayer Times List */}
      <div className="space-y-4">
        {nextPrayerTimes.map((prayer) => (
          <div
            key={prayer.name}
            className={`flex items-center justify-between p-4 rounded-xl transition-all duration-200 ${
              prayer.isNext
                ? 'bg-gradient-to-r from-teal-50 to-teal-100 border-2 border-teal-200 shadow-md'
                : 'bg-gray-50 hover:bg-gray-100 border border-gray-200'
            }`}
          >
            <div className="flex items-center space-x-4">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                prayer.isNext ? 'bg-teal-500' : 'bg-gray-200'
              }`}>
                {prayerIcons[prayer.name as keyof typeof prayerIcons]}
              </div>
              <span className={`text-base font-semibold ${
                prayer.isNext ? 'text-teal-900' : 'text-gray-900'
              }`}>
                {prayer.name}
              </span>
            </div>
            <span className={`text-lg font-mono font-bold ${
              prayer.isNext ? 'text-teal-700' : 'text-gray-700'
            }`}>
              {prayer.time}
            </span>
          </div>
        ))}
      </div>

      {/* Source Info */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-center space-x-2">
          <div className="w-2 h-2 bg-teal-500 rounded-full"></div>
          <p className="text-sm text-gray-600 font-medium">
            {prayerTimesResponse.source === 'diyanet' 
              ? 'Gegevens van Diyanet İşleri Başkanlığı'
              : 'Berekend volgens ISNA methode'
            }
          </p>
        </div>
      </div>
    </div>
  );
}
