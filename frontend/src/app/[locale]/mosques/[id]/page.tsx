'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { apiClient } from '@/api/client';
import { notFound } from 'next/navigation';
import type { Mosque } from '@/types/api';
import { 
  MapPinIcon, 
  PhoneIcon, 
  EnvelopeIcon, 
  ClockIcon, 
  UsersIcon, 
  CalendarIcon,
  PhotoIcon,
  VideoCameraIcon,
  DocumentTextIcon,
  UserGroupIcon,
  HeartIcon,
  StarIcon
} from '@heroicons/react/24/outline';

export default function MosqueDetailPage({ params }: { params: { id: string } }) {
  const [activeTab, setActiveTab] = useState('overview');

  const { data: mosque, isLoading, isError } = useQuery<Mosque>({
    queryKey: ['mosque', params.id],
    queryFn: () => apiClient.get<Mosque>(`/api/mosques/${params.id}`),
    enabled: !!params.id,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (isError || !mosque) {
    notFound();
  }

  const tabs = [
    { id: 'overview', name: 'Overzicht', icon: DocumentTextIcon },
    { id: 'prayer-times', name: 'Gebedstijden', icon: ClockIcon },
    { id: 'events', name: 'Evenementen', icon: CalendarIcon },
    { id: 'board', name: 'Bestuur', icon: UserGroupIcon },
    { id: 'history', name: 'Geschiedenis', icon: StarIcon },
    { id: 'media', name: 'Media', icon: PhotoIcon }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Beschrijving</h3>
              <p className="text-gray-600 leading-relaxed">{mosque.description}</p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Faciliteiten</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {/* Note: API data doesn't have features array, so we show basic info */}
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-teal-500 rounded-full mr-3"></div>
                  <span className="text-gray-700">Vrijdaggebed</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-teal-500 rounded-full mr-3"></div>
                  <span className="text-gray-700">Dagelijkse gebeden</span>
                </div>
                {mosque.capacity && (
                  <div className="flex items-center">
                    <div className="w-2 h-2 bg-teal-500 rounded-full mr-3"></div>
                    <span className="text-gray-700">Capaciteit: {mosque.capacity} personen</span>
                  </div>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2">Contact Informatie</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center">
                    <MapPinIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <span>{mosque.address}</span>
                  </div>
                  <div className="flex items-center">
                    <PhoneIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <span>{mosque.phone}</span>
                  </div>
                  <div className="flex items-center">
                    <EnvelopeIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <span>{mosque.email}</span>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2">Moskee Informatie</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center">
                    <UsersIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <span>Capaciteit: {mosque.capacity} personen</span>
                  </div>
                  <div className="flex items-center">
                    <CalendarIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <span>Opgericht: {mosque.established_year}</span>
                  </div>
                  <div className="flex items-center">
                    <UserGroupIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <span>Imam: {mosque.imam_name}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'prayer-times':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Dagelijkse Gebedstijden</h3>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                {[
                  { name: 'Fajr', time: '05:30' },
                  { name: 'Dhuhr', time: '12:30' },
                  { name: 'Asr', time: '15:45' },
                  { name: 'Maghrib', time: '18:15' },
                  { name: 'Isha', time: '19:45' }
                ].map((prayer) => (
                  <div key={prayer.name} className="bg-gray-50 rounded-lg p-4 text-center">
                    <div className="text-sm text-gray-600 mb-1">{prayer.name}</div>
                    <div className="text-2xl font-bold text-gray-900">{prayer.time}</div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="bg-teal-50 border border-teal-200 rounded-lg p-4">
              <h4 className="font-semibold text-teal-900 mb-2">Belangrijke Informatie</h4>
              <ul className="text-sm text-teal-800 space-y-1">
                <li>• Gebedstijden worden dagelijks bijgewerkt</li>
                <li>• Vrijdaggebed begint om 13:00</li>
                <li>• Ramadan tijden worden apart aangegeven</li>
                <li>• Voor vragen over gebedstijden, neem contact op</li>
                <li>• * Bovenstaande tijden zijn voorbeeldtijden</li>
              </ul>
            </div>
          </div>
        );

      case 'events':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Aankomende Evenementen</h3>
              <div className="space-y-4">
                <div className="bg-gray-50 rounded-lg p-6 text-center">
                  <p className="text-gray-600 mb-4">
                    Evenementen voor deze moskee worden binnenkort geladen.
                  </p>
                  <div className="space-y-3">
                    <div className="bg-white border border-gray-200 rounded-lg p-4">
                      <div className="flex flex-col md:flex-row md:items-start md:justify-between">
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900 mb-1">Vrijdaggebed</h4>
                          <p className="text-gray-600 text-sm mb-2">Wekelijks vrijdaggebed</p>
                          <div className="flex items-center text-sm text-gray-500">
                            <CalendarIcon className="h-4 w-4 mr-1" />
                            <span>Elke vrijdag</span>
                            <ClockIcon className="h-4 w-4 ml-4 mr-1" />
                            <span>13:00</span>
                          </div>
                        </div>
                        <button className="mt-2 md:mt-0 bg-teal-600 text-white px-4 py-2 rounded-md hover:bg-teal-700 transition-colors text-sm">
                          Meer Info
                        </button>
                      </div>
                    </div>
                  </div>
                  <p className="text-sm text-gray-500 mt-4">
                    * Dit zijn voorbeeldevenementen. Werkelijke evenementen worden binnenkort geladen.
                  </p>
                </div>
              </div>
            </div>
          </div>
        );

      case 'board':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Bestuursleden</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-1">Voorzitter</h4>
                  <p className="text-teal-600 font-medium mb-2">Bestuursvoorzitter</p>
                  <div className="flex items-center text-sm text-gray-600">
                    <EnvelopeIcon className="h-4 w-4 mr-1" />
                    <span>contact@{mosque.name.toLowerCase().replace(/\s+/g, '')}.be</span>
                  </div>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-1">Secretaris</h4>
                  <p className="text-teal-600 font-medium mb-2">Bestuurssecretaris</p>
                  <div className="flex items-center text-sm text-gray-600">
                    <EnvelopeIcon className="h-4 w-4 mr-1" />
                    <span>secretaris@{mosque.name.toLowerCase().replace(/\s+/g, '')}.be</span>
                  </div>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-1">Penningmeester</h4>
                  <p className="text-teal-600 font-medium mb-2">Financieel beheerder</p>
                  <div className="flex items-center text-sm text-gray-600">
                    <EnvelopeIcon className="h-4 w-4 mr-1" />
                    <span>financieel@{mosque.name.toLowerCase().replace(/\s+/g, '')}.be</span>
                  </div>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-1">Imam</h4>
                  <p className="text-teal-600 font-medium mb-2">Spiritueel leider</p>
                  <div className="flex items-center text-sm text-gray-600">
                    <EnvelopeIcon className="h-4 w-4 mr-1" />
                    <span>{mosque.imam_name || 'imam@moskee.be'}</span>
                  </div>
                </div>
              </div>
              <p className="text-sm text-gray-500 mt-4">
                * Dit zijn voorbeeldbestuursleden. Werkelijke bestuursinformatie wordt binnenkort geladen.
              </p>
            </div>
          </div>
        );

      case 'history':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Geschiedenis van de Moskee</h3>
              <div className="space-y-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center">
                      <span className="text-teal-600 font-semibold">{mosque.established_year || '1985'}</span>
                    </div>
                  </div>
                  <div className="ml-4 flex-1">
                    <h4 className="font-semibold text-gray-900 mb-1">Oprichting van de moskee</h4>
                    <p className="text-gray-600">De moskee werd opgericht en heeft sindsdien een belangrijke rol gespeeld in de lokale gemeenschap.</p>
                  </div>
                </div>
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center">
                      <span className="text-teal-600 font-semibold">2000</span>
                    </div>
                  </div>
                  <div className="ml-4 flex-1">
                    <h4 className="font-semibold text-gray-900 mb-1">Uitbreiding van faciliteiten</h4>
                    <p className="text-gray-600">De moskee werd uitgebreid met nieuwe faciliteiten voor de groeiende gemeenschap.</p>
                  </div>
                </div>
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center">
                      <span className="text-teal-600 font-semibold">2015</span>
                    </div>
                  </div>
                  <div className="ml-4 flex-1">
                    <h4 className="font-semibold text-gray-900 mb-1">Modernisering</h4>
                    <p className="text-gray-600">De moskee werd gemoderniseerd met nieuwe technologieën en verbeterde faciliteiten.</p>
                  </div>
                </div>
              </div>
              <p className="text-sm text-gray-500 mt-4">
                * Dit zijn voorbeeldgebeurtenissen. Werkelijke geschiedenis wordt binnenkort geladen.
              </p>
            </div>
          </div>
        );

      case 'media':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Foto&apos;s</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {mosque.photos.map((photo, index) => (
                  <div key={index} className="bg-gray-200 rounded-lg h-48 flex items-center justify-center">
                    <PhotoIcon className="h-12 w-12 text-gray-400" />
                  </div>
                ))}
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Video&apos;s</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {mosque.videos.map((video, index) => (
                  <div key={index} className="bg-gray-200 rounded-lg h-48 flex items-center justify-center">
                    <VideoCameraIcon className="h-12 w-12 text-gray-400" />
                  </div>
                ))}
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Documenten</h3>
              <div className="space-y-2">
                {mosque.documents.map((doc, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-50 rounded-lg p-3">
                    <div className="flex items-center">
                      <DocumentTextIcon className="h-5 w-5 text-gray-400 mr-3" />
                      <span className="text-gray-900">{doc.name}</span>
                    </div>
                    <button className="text-teal-600 hover:text-teal-700 font-medium">
                      Download
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <Breadcrumbs items={[
        { name: 'Moskeeën', href: '/mosques' },
        { name: mosque.name }
      ]} />
      
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            {mosque.name}
          </h1>
          <div className="flex items-center text-gray-600">
            <MapPinIcon className="h-5 w-5 mr-2" />
            <span>{mosque.address}</span>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 overflow-x-auto">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`${
                    activeTab === tab.id
                      ? 'border-teal-500 text-teal-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 flex items-center`}
                >
                  <tab.icon className="h-4 w-4 mr-2" />
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-lg">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
}