'use client';

import { useState } from 'react';
import { useTodayPrayerTimes, useTomorrowPrayerTimes } from '@/hooks/usePrayerTimes';
import { PrayerTimesWidget } from './PrayerTimesWidget';
import { CalendarIcon, ClockIcon, MapPinIcon } from '@heroicons/react/24/outline';
import { Skeleton } from '@/components/ui/Skeleton';

export function PrayerTimesPage() {
  const [selectedDate, setSelectedDate] = useState<'today' | 'tomorrow'>('today');
  
  const { data: todayData, isLoading: todayLoading } = useTodayPrayerTimes();
  const { data: tomorrowData, isLoading: tomorrowLoading } = useTomorrowPrayerTimes();

  const isLoading = selectedDate === 'today' ? todayLoading : tomorrowLoading;
  const data = selectedDate === 'today' ? todayData : tomorrowData;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Gebedstijden
            </h1>
            <p className="text-lg text-gray-600 mb-6">
              Gebedstijden voor Gent en omgeving
            </p>
            
            {/* Date Selector */}
            <div className="flex items-center justify-center space-x-4">
              <button
                onClick={() => setSelectedDate('today')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedDate === 'today'
                    ? 'bg-teal-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Vandaag
              </button>
              <button
                onClick={() => setSelectedDate('tomorrow')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedDate === 'tomorrow'
                    ? 'bg-teal-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Morgen
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Prayer Times */}
          <div className="lg:col-span-2">
            <PrayerTimesWidget />
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Location Info */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Locatie
              </h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <MapPinIcon className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Gent, België</p>
                    <p className="text-xs text-gray-500">51.0543°N, 3.7174°E</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <ClockIcon className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Tijdzone</p>
                    <p className="text-xs text-gray-500">CET (UTC+1)</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Calculation Method */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Berekening
              </h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-medium text-gray-900">Primaire bron</p>
                  <p className="text-xs text-gray-500">Diyanet İşleri Başkanlığı</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Fallback methode</p>
                  <p className="text-xs text-gray-500">ISNA (Islamic Society of North America)</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Hoge breedtegraad</p>
                  <p className="text-xs text-gray-500">Angle-based aanpassing</p>
                </div>
              </div>
            </div>

            {/* Prayer Times Info */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Gebedstijden
              </h3>
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex justify-between">
                  <span>Fajr (Dageraad):</span>
                  <span>15°</span>
                </div>
                <div className="flex justify-between">
                  <span>Sunrise (Zonsopgang):</span>
                  <span>-0.833°</span>
                </div>
                <div className="flex justify-between">
                  <span>Dhuhr (Middag):</span>
                  <span>Zon hoogste punt</span>
                </div>
                <div className="flex justify-between">
                  <span>Asr (Namiddag):</span>
                  <span>Hanafi methode</span>
                </div>
                <div className="flex justify-between">
                  <span>Maghrib (Zonsondergang):</span>
                  <span>-0.833°</span>
                </div>
                <div className="flex justify-between">
                  <span>Isha (Avond):</span>
                  <span>15°</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Additional Info */}
        <div className="mt-8 bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Belangrijke informatie
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Gebedstijden</h4>
              <p className="text-sm text-gray-600">
                Gebedstijden worden automatisch bijgewerkt en zijn gebaseerd op de exacte locatie van Gent. 
                Bij storingen van de Diyanet API wordt automatisch overgeschakeld naar astronomische berekeningen.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Zomertijd</h4>
              <p className="text-sm text-gray-600">
                Tijdens de zomertijd (CEST, UTC+2) worden de gebedstijden automatisch aangepast. 
                De berekeningen houden rekening met de seizoensgebonden veranderingen in daglicht.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
