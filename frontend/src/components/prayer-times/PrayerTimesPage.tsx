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
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-white to-blue-50">
      {/* Hero Header */}
      <div className="bg-gradient-to-r from-teal-600 to-teal-700 text-white">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-white/20 rounded-full mb-4">
              <ClockIcon className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold mb-3">
              Gebedstijden
            </h1>
            <p className="text-xl text-teal-100 mb-8">
              Gebedstijden voor Gent en omgeving
            </p>
            
            {/* Date Selector */}
            <div className="flex items-center justify-center space-x-3">
              <button
                onClick={() => setSelectedDate('today')}
                className={`px-6 py-3 rounded-xl text-sm font-semibold transition-all duration-200 ${
                  selectedDate === 'today'
                    ? 'bg-white text-teal-600 shadow-lg'
                    : 'bg-white/20 text-white hover:bg-white/30'
                }`}
              >
                Vandaag
              </button>
              <button
                onClick={() => setSelectedDate('tomorrow')}
                className={`px-6 py-3 rounded-xl text-sm font-semibold transition-all duration-200 ${
                  selectedDate === 'tomorrow'
                    ? 'bg-white text-teal-600 shadow-lg'
                    : 'bg-white/20 text-white hover:bg-white/30'
                }`}
              >
                Morgen
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Prayer Times */}
          <div className="lg:col-span-2">
            <PrayerTimesWidget />
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Location Info */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-teal-100 rounded-full flex items-center justify-center">
                  <MapPinIcon className="w-5 h-5 text-teal-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Locatie
                </h3>
              </div>
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <MapPinIcon className="w-4 h-4 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Gent, België</p>
                    <p className="text-xs text-gray-500">51.0543°N, 3.7174°E</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <ClockIcon className="w-4 h-4 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Tijdzone</p>
                    <p className="text-xs text-gray-500">CET (UTC+1)</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Calculation Method */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                  <CalendarIcon className="w-5 h-5 text-purple-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Berekening
                </h3>
              </div>
              <div className="space-y-4">
                <div className="p-3 bg-teal-50 rounded-lg">
                  <p className="text-sm font-medium text-gray-900">Primaire bron</p>
                  <p className="text-xs text-gray-600">Diyanet İşleri Başkanlığı</p>
                </div>
                <div className="p-3 bg-blue-50 rounded-lg">
                  <p className="text-sm font-medium text-gray-900">Fallback methode</p>
                  <p className="text-xs text-gray-600">ISNA (Islamic Society of North America)</p>
                </div>
                <div className="p-3 bg-green-50 rounded-lg">
                  <p className="text-sm font-medium text-gray-900">Hoge breedtegraad</p>
                  <p className="text-xs text-gray-600">Angle-based aanpassing</p>
                </div>
              </div>
            </div>

            {/* Prayer Times Info */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
                  <ClockIcon className="w-5 h-5 text-orange-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Gebedstijden Details
                </h3>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Fajr (Dageraad)</span>
                  <span className="text-sm font-semibold text-gray-900">15°</span>
                </div>
                <div className="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Sunrise (Zonsopgang)</span>
                  <span className="text-sm font-semibold text-gray-900">-0.833°</span>
                </div>
                <div className="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Dhuhr (Middag)</span>
                  <span className="text-sm font-semibold text-gray-900">Zon hoogste punt</span>
                </div>
                <div className="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Asr (Namiddag)</span>
                  <span className="text-sm font-semibold text-gray-900">Hanafi methode</span>
                </div>
                <div className="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Maghrib (Zonsondergang)</span>
                  <span className="text-sm font-semibold text-gray-900">-0.833°</span>
                </div>
                <div className="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Isha (Avond)</span>
                  <span className="text-sm font-semibold text-gray-900">15°</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Additional Info */}
        <div className="mt-12 bg-white rounded-2xl shadow-lg border border-gray-200 p-8 hover:shadow-xl transition-all duration-300">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-12 h-12 bg-gradient-to-r from-teal-500 to-blue-500 rounded-full flex items-center justify-center">
              <ClockIcon className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900">
              Belangrijke informatie
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="p-6 bg-gradient-to-br from-teal-50 to-teal-100 rounded-xl">
              <div className="flex items-center space-x-3 mb-3">
                <div className="w-8 h-8 bg-teal-500 rounded-full flex items-center justify-center">
                  <ClockIcon className="w-4 h-4 text-white" />
                </div>
                <h4 className="text-lg font-semibold text-gray-900">Gebedstijden</h4>
              </div>
              <p className="text-sm text-gray-700 leading-relaxed">
                Gebedstijden worden automatisch bijgewerkt en zijn gebaseerd op de exacte locatie van Gent. 
                Bij storingen van de Diyanet API wordt automatisch overgeschakeld naar astronomische berekeningen.
              </p>
            </div>
            <div className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl">
              <div className="flex items-center space-x-3 mb-3">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                  <SunIcon className="w-4 h-4 text-white" />
                </div>
                <h4 className="text-lg font-semibold text-gray-900">Zomertijd</h4>
              </div>
              <p className="text-sm text-gray-700 leading-relaxed">
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
