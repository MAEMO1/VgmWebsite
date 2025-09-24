'use client';

import { useState, useEffect } from 'react';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { CalendarIcon, ClockIcon, MapPinIcon } from '@heroicons/react/24/outline';

interface PrayerTime {
  name: string;
  time: string;
  arabic: string;
}

interface MosquePrayerTimes {
  mosque: string;
  address: string;
  times: PrayerTime[];
}

export default function PrayerTimesPage() {
  const [selectedMosque, setSelectedMosque] = useState('all');
  const [currentDate, setCurrentDate] = useState(new Date());

  // Mock data - in real app this would come from API
  const mosques = [
    { id: 'all', name: 'Alle Moskeeën' },
    { id: 'salahaddien', name: 'Moskee Salahaddien' },
    { id: 'al-fath', name: 'Moskee Al-Fath' },
    { id: 'selimiye', name: 'Moskee Selimiye' }
  ];

  const prayerTimesData: MosquePrayerTimes[] = [
    {
      mosque: 'Moskee Salahaddien',
      address: 'Sint-Pietersnieuwstraat 120, Gent',
      times: [
        { name: 'Fajr', time: '05:45', arabic: 'الفجر' },
        { name: 'Dhuhr', time: '12:30', arabic: 'الظهر' },
        { name: 'Asr', time: '15:45', arabic: 'العصر' },
        { name: 'Maghrib', time: '18:15', arabic: 'المغرب' },
        { name: 'Isha', time: '19:45', arabic: 'العشاء' }
      ]
    },
    {
      mosque: 'Moskee Al-Fath',
      address: 'Korte Meer 11, Gent',
      times: [
        { name: 'Fajr', time: '05:50', arabic: 'الفجر' },
        { name: 'Dhuhr', time: '12:35', arabic: 'الظهر' },
        { name: 'Asr', time: '15:50', arabic: 'العصر' },
        { name: 'Maghrib', time: '18:20', arabic: 'المغرب' },
        { name: 'Isha', time: '19:50', arabic: 'العشاء' }
      ]
    },
    {
      mosque: 'Moskee Selimiye',
      address: 'Kasteellaan 15, Gent',
      times: [
        { name: 'Fajr', time: '05:40', arabic: 'الفجر' },
        { name: 'Dhuhr', time: '12:25', arabic: 'الظهر' },
        { name: 'Asr', time: '15:40', arabic: 'العصر' },
        { name: 'Maghrib', time: '18:10', arabic: 'المغرب' },
        { name: 'Isha', time: '19:40', arabic: 'العشاء' }
      ]
    }
  ];

  const filteredData = selectedMosque === 'all' 
    ? prayerTimesData 
    : prayerTimesData.filter(mosque => mosque.mosque.toLowerCase().includes(selectedMosque));

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('nl-NL', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen bg-white">
      <Breadcrumbs items={[
        { name: 'Moskeeën', href: '/mosques' },
        { name: 'Gebedstijden' }
      ]} />
      
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Gebedstijden
          </h1>
          <p className="text-gray-600 text-lg">
            Bekijk de gebedstijden voor alle aangesloten moskeeën in Gent.
          </p>
        </div>

        {/* Controls */}
        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Selecteer Moskee
              </label>
              <select
                value={selectedMosque}
                onChange={(e) => setSelectedMosque(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                {mosques.map((mosque) => (
                  <option key={mosque.id} value={mosque.id}>
                    {mosque.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Datum
              </label>
              <div className="flex items-center px-3 py-2 border border-gray-300 rounded-md bg-white">
                <CalendarIcon className="h-5 w-5 text-gray-400 mr-2" />
                <span className="text-gray-900">{formatDate(currentDate)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Prayer Times */}
        <div className="space-y-8">
          {filteredData.map((mosque, index) => (
            <div key={index} className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center mb-6">
                <MapPinIcon className="h-5 w-5 text-gray-400 mr-2" />
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">
                    {mosque.mosque}
                  </h3>
                  <p className="text-gray-600">{mosque.address}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                {mosque.times.map((prayer, prayerIndex) => (
                  <div key={prayerIndex} className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">{prayer.name}</div>
                    <div className="text-2xl font-bold text-gray-900 mb-1">{prayer.time}</div>
                    <div className="text-sm text-gray-500">{prayer.arabic}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Info */}
        <div className="mt-12 bg-teal-50 border border-teal-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Belangrijke Informatie
          </h3>
          <ul className="text-gray-600 space-y-1">
            <li>• Gebedstijden worden dagelijks bijgewerkt</li>
            <li>• Tijden kunnen per moskee verschillen</li>
            <li>• Voor de meest actuele tijden, neem contact op met de betreffende moskee</li>
            <li>• Ramadan tijden worden apart aangegeven tijdens de heilige maand</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
