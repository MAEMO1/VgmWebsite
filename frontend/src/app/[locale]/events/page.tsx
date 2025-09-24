'use client';

import { useState } from 'react';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { ChevronLeftIcon, ChevronRightIcon, CalendarIcon, ClockIcon, MapPinIcon } from '@heroicons/react/24/outline';

interface Event {
  id: number;
  title: string;
  date: string;
  time: string;
  location: string;
  mosque: string;
  type: 'prayer' | 'event' | 'lecture' | 'community';
  description: string;
}

export default function EventsCalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewMode, setViewMode] = useState<'calendar' | 'list'>('calendar');

  // Mock events data
  const events: Event[] = [
    {
      id: 1,
      title: 'Vrijdaggebed',
      date: '2024-01-26',
      time: '13:00',
      location: 'Moskee Salahaddien',
      mosque: 'Sint-Pietersnieuwstraat 120, Gent',
      type: 'prayer',
      description: 'Wekelijks vrijdaggebed'
    },
    {
      id: 2,
      title: 'Iftar Gemeenschapsmaaltijd',
      date: '2024-01-28',
      time: '18:30',
      location: 'Moskee Al-Fath',
      mosque: 'Korte Meer 11, Gent',
      type: 'community',
      description: 'Gemeenschappelijke iftar-maaltijd tijdens Ramadan'
    },
    {
      id: 3,
      title: 'Islamitische Geschiedenis Lezing',
      date: '2024-01-30',
      time: '19:00',
      location: 'Moskee Selimiye',
      mosque: 'Kasteellaan 15, Gent',
      type: 'lecture',
      description: 'Lezing over de geschiedenis van de islam'
    },
    {
      id: 4,
      title: 'Vrijdaggebed',
      date: '2024-02-02',
      time: '13:00',
      location: 'Moskee Salahaddien',
      mosque: 'Sint-Pietersnieuwstraat 120, Gent',
      type: 'prayer',
      description: 'Wekelijks vrijdaggebed'
    }
  ];

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(day);
    }
    
    return days;
  };

  const getEventsForDate = (date: Date) => {
    const dateString = date.toISOString().split('T')[0];
    return events.filter(event => event.date === dateString);
  };

  const getEventTypeColor = (type: string) => {
    switch (type) {
      case 'prayer': return 'bg-blue-100 text-blue-800';
      case 'event': return 'bg-green-100 text-green-800';
      case 'lecture': return 'bg-purple-100 text-purple-800';
      case 'community': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    if (direction === 'prev') {
      newDate.setMonth(newDate.getMonth() - 1);
    } else {
      newDate.setMonth(newDate.getMonth() + 1);
    }
    setCurrentDate(newDate);
  };

  const formatMonthYear = (date: Date) => {
    return date.toLocaleDateString('nl-NL', { month: 'long', year: 'numeric' });
  };

  const days = getDaysInMonth(currentDate);
  const monthNames = ['Ma', 'Di', 'Wo', 'Do', 'Vr', 'Za', 'Zo'];

  return (
    <div className="min-h-screen bg-white">
      <Breadcrumbs items={[
        { name: 'Gemeenschap', href: '/community' },
        { name: 'Evenementen' }
      ]} />
      
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Evenementen Kalender
          </h1>
          <p className="text-gray-600 text-lg">
            Bekijk alle evenementen en activiteiten in de Gentse moskeeën.
          </p>
        </div>

        {/* Controls */}
        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigateMonth('prev')}
                className="p-2 bg-white rounded-lg border border-gray-300 hover:bg-gray-50"
              >
                <ChevronLeftIcon className="h-5 w-5" />
              </button>
              <h2 className="text-xl font-semibold text-gray-900">
                {formatMonthYear(currentDate)}
              </h2>
              <button
                onClick={() => navigateMonth('next')}
                className="p-2 bg-white rounded-lg border border-gray-300 hover:bg-gray-50"
              >
                <ChevronRightIcon className="h-5 w-5" />
              </button>
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode('calendar')}
                className={`px-4 py-2 rounded-lg font-medium ${
                  viewMode === 'calendar'
                    ? 'bg-teal-600 text-white'
                    : 'bg-white text-gray-700 border border-gray-300'
                }`}
              >
                <CalendarIcon className="h-4 w-4 inline mr-2" />
                Kalender
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`px-4 py-2 rounded-lg font-medium ${
                  viewMode === 'list'
                    ? 'bg-teal-600 text-white'
                    : 'bg-white text-gray-700 border border-gray-300'
                }`}
              >
                Lijst
              </button>
            </div>
          </div>
        </div>

        {/* Calendar View */}
        {viewMode === 'calendar' && (
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            {/* Calendar Header */}
            <div className="grid grid-cols-7 bg-gray-50 border-b border-gray-200">
              {monthNames.map((day) => (
                <div key={day} className="p-4 text-center font-medium text-gray-700">
                  {day}
                </div>
              ))}
            </div>
            
            {/* Calendar Body */}
            <div className="grid grid-cols-7">
              {days.map((day, index) => {
                const dayDate = day ? new Date(currentDate.getFullYear(), currentDate.getMonth(), day) : null;
                const dayEvents = dayDate ? getEventsForDate(dayDate) : [];
                const isToday = dayDate && dayDate.toDateString() === new Date().toDateString();
                
                return (
                  <div
                    key={index}
                    className={`min-h-[120px] border-r border-b border-gray-200 p-2 ${
                      day ? 'bg-white' : 'bg-gray-50'
                    } ${isToday ? 'bg-teal-50' : ''}`}
                  >
                    {day && (
                      <>
                        <div className={`text-sm font-medium mb-1 ${isToday ? 'text-teal-600' : 'text-gray-900'}`}>
                          {day}
                        </div>
                        <div className="space-y-1">
                          {dayEvents.slice(0, 2).map((event) => (
                            <div
                              key={event.id}
                              className={`text-xs px-2 py-1 rounded ${getEventTypeColor(event.type)} truncate`}
                              title={event.title}
                            >
                              {event.title}
                            </div>
                          ))}
                          {dayEvents.length > 2 && (
                            <div className="text-xs text-gray-500">
                              +{dayEvents.length - 2} meer
                            </div>
                          )}
                        </div>
                      </>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* List View */}
        {viewMode === 'list' && (
          <div className="space-y-4">
            {events.map((event) => (
              <div key={event.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getEventTypeColor(event.type)}`}>
                        {event.type}
                      </span>
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      {event.title}
                    </h3>
                    <p className="text-gray-600 mb-4">
                      {event.description}
                    </p>
                    <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                      <div className="flex items-center">
                        <CalendarIcon className="h-4 w-4 mr-1" />
                        {new Date(event.date).toLocaleDateString('nl-NL')}
                      </div>
                      <div className="flex items-center">
                        <ClockIcon className="h-4 w-4 mr-1" />
                        {event.time}
                      </div>
                      <div className="flex items-center">
                        <MapPinIcon className="h-4 w-4 mr-1" />
                        {event.location}
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 md:mt-0 md:ml-6">
                    <button className="bg-teal-600 text-white px-6 py-2 rounded-lg hover:bg-teal-700 transition-colors">
                      Meer Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Legend */}
        <div className="mt-8 bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Legenda</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-blue-100 rounded mr-2"></div>
              <span className="text-sm text-gray-700">Gebeden</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-100 rounded mr-2"></div>
              <span className="text-sm text-gray-700">Evenementen</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-purple-100 rounded mr-2"></div>
              <span className="text-sm text-gray-700">Lezingen</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-orange-100 rounded mr-2"></div>
              <span className="text-sm text-gray-700">Gemeenschap</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
