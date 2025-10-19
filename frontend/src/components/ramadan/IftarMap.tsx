'use client';

import { useState } from 'react';
import { 
  CalendarIcon, 
  ClockIcon, 
  HeartIcon, 
  StarIcon,
  MoonIcon,
  SunIcon,
  GiftIcon,
  MapPinIcon
} from '@heroicons/react/24/outline';

export function IftarMap() {
  const [activeTab, setActiveTab] = useState('calendar');

  // Calculate Ramadan dates for 2024 (example)
  const ramadanStart = new Date('2024-03-11');
  const ramadanEnd = new Date('2024-04-09');
  const eidAlFitr = new Date('2024-04-10');

  const tabs = [
    { id: 'calendar', name: 'Ramadan Kalender', icon: CalendarIcon },
    { id: 'iftar', name: 'Iftar Tijden', icon: ClockIcon },
    { id: 'events', name: 'Speciale Evenementen', icon: StarIcon },
    { id: 'dua', name: 'Dua & Reflecties', icon: HeartIcon }
  ];

  const ramadanDays = Array.from({ length: 30 }, (_, i) => {
    const date = new Date(ramadanStart);
    date.setDate(date.getDate() + i);
    return {
      day: i + 1,
      date: date,
      fajr: '05:30',
      maghrib: '18:30',
      isha: '20:00'
    };
  });

  const specialEvents = [
    {
      date: '2024-03-11',
      title: 'Eerste dag van Ramadan',
      description: 'Welkom Ramadan! Begin van de gezegende maand.',
      type: 'special'
    },
    {
      date: '2024-03-21',
      title: 'Laylat al-Qadr (Nacht van Kracht)',
      description: 'De gezegende nacht die beter is dan duizend maanden.',
      type: 'laylat-al-qadr'
    },
    {
      date: '2024-04-10',
      title: 'Eid al-Fitr',
      description: 'Feest van het breken van het vasten.',
      type: 'eid'
    }
  ];

  const duas = [
    {
      title: 'Dua voor het begin van Ramadan',
      arabic: 'اللهم بارك لنا في رمضان',
      translation: 'O Allah, zegene ons in Ramadan',
      meaning: 'Een gebed om zegening te vragen voor de maand Ramadan'
    },
    {
      title: 'Dua voor Laylat al-Qadr',
      arabic: 'اللهم إنك عفو تحب العفو فاعف عني',
      translation: 'O Allah, U bent vergevingsgezind en houdt van vergeving, vergeef mij',
      meaning: 'Een krachtig gebed voor vergeving tijdens de Nacht van Kracht'
    },
    {
      title: 'Dua voor het breken van het vasten',
      arabic: 'اللهم لك صمت وعلى رزقك أفطرت',
      translation: 'O Allah, voor U heb ik gevast en met Uw voorziening heb ik het vasten verbroken',
      meaning: 'Een gebed dat wordt uitgesproken bij het breken van het vasten'
    }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'calendar':
  return (
    <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Ramadan Kalender 2024</h2>
              <p className="text-lg text-gray-600">
                Ramadan: {ramadanStart.toLocaleDateString('nl-NL')} - {ramadanEnd.toLocaleDateString('nl-NL')}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {ramadanDays.map((day) => (
                <div key={day.day} className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary mb-2">Dag {day.day}</div>
                    <div className="text-sm text-gray-600 mb-3">
                      {day.date.toLocaleDateString('nl-NL', { 
                        weekday: 'long', 
                        day: 'numeric', 
                        month: 'long' 
                      })}
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Fajr:</span>
                        <span className="font-semibold">{day.fajr}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Maghrib:</span>
                        <span className="font-semibold">{day.maghrib}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Isha:</span>
                        <span className="font-semibold">{day.isha}</span>
          </div>
        </div>
                  </div>
                  </div>
                ))}
              </div>
          </div>
        );

      case 'iftar':
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Iftar Tijden</h2>
              <p className="text-lg text-gray-600">
                Tijden voor het breken van het vasten (Maghrib) in Gent
              </p>
            </div>

            <div className="bg-gradient-to-r from-primary to-primary-600 rounded-lg p-8 text-white text-center">
              <MoonIcon className="w-16 h-16 mx-auto mb-4" />
              <h3 className="text-2xl font-bold mb-2">Vandaag's Iftar Tijd</h3>
              <div className="text-4xl font-bold mb-4">18:30</div>
              <p className="text-primary-100">
                De tijd voor het breken van het vasten wordt bepaald door de zonsondergang.
              </p>
          </div>
          
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                  <SunIcon className="w-6 h-6 mr-2 text-yellow-500" />
                  Suhoor (Dawn Meal)
            </h3>
                <p className="text-gray-600 mb-4">
                  De laatste maaltijd voor het begin van het vasten, gegeten voor Fajr.
                </p>
                <div className="text-lg font-semibold text-primary">
                  Aanbevolen tijd: Voor 05:30
              </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                  <MoonIcon className="w-6 h-6 mr-2 text-blue-500" />
                  Iftar (Breaking Fast)
                </h3>
                <p className="text-gray-600 mb-4">
                  De maaltijd waarmee het vasten wordt verbroken na zonsondergang.
                </p>
                <div className="text-lg font-semibold text-primary">
                  Tijd: 18:30 (Maghrib)
              </div>
              </div>
            </div>
          </div>
        );

      case 'events':
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Speciale Evenementen</h2>
              <p className="text-lg text-gray-600">
                Belangrijke dagen en evenementen tijdens Ramadan
              </p>
            </div>

            <div className="space-y-4">
              {specialEvents.map((event, index) => (
                <div key={index} className="bg-white rounded-lg shadow-md p-6 border-l-4 border-primary">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-gray-900 mb-2">{event.title}</h3>
                      <p className="text-gray-600 mb-2">{event.description}</p>
                      <div className="text-sm text-gray-500">
                        {new Date(event.date).toLocaleDateString('nl-NL', { 
                          weekday: 'long', 
                          day: 'numeric', 
                          month: 'long',
                          year: 'numeric'
                        })}
                      </div>
                    </div>
                    <div className="ml-4">
                      {event.type === 'laylat-al-qadr' && (
                        <StarIcon className="w-8 h-8 text-yellow-500" />
                      )}
                      {event.type === 'eid' && (
                        <GiftIcon className="w-8 h-8 text-green-500" />
                      )}
                      {event.type === 'special' && (
                        <HeartIcon className="w-8 h-8 text-red-500" />
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case 'dua':
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Dua & Reflecties</h2>
              <p className="text-lg text-gray-600">
                Gebeden en overdenkingen voor de gezegende maand Ramadan
              </p>
            </div>

            <div className="space-y-6">
              {duas.map((dua, index) => (
                <div key={index} className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4">{dua.title}</h3>
                  
                  <div className="space-y-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="text-lg font-semibold text-gray-800 mb-2">Arabisch:</h4>
                      <p className="text-2xl text-right font-arabic text-gray-900 leading-relaxed">
                        {dua.arabic}
                      </p>
                    </div>
                    
                    <div className="bg-primary-50 rounded-lg p-4">
                      <h4 className="text-lg font-semibold text-primary mb-2">Nederlandse Vertaling:</h4>
                      <p className="text-lg text-primary-800">{dua.translation}</p>
                    </div>
                    
                    <div className="bg-blue-50 rounded-lg p-4">
                      <h4 className="text-lg font-semibold text-blue-800 mb-2">Betekenis:</h4>
                      <p className="text-blue-700">{dua.meaning}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Ramadan 2024
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Welkom in de gezegende maand Ramadan. Vind hier alle informatie over gebedstijden, evenementen en spirituele begeleiding.
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="w-5 h-5 inline mr-2" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        {renderTabContent()}
      </div>
    </div>
  );
}