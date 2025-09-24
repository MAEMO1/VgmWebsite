'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { getAllMosques } from '@/data/mosques';
import { MagnifyingGlassIcon, MapPinIcon, PhoneIcon, CalendarIcon, UsersIcon, Squares2X2Icon, ListBulletIcon } from '@heroicons/react/24/outline';

// Mosque interface is now imported from the data file

export default function MosquesPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCity, setSelectedCity] = useState('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // Get real mosque data
  const mosques = getAllMosques();

  const cities = ['all', 'Gent', 'Andere'];

  const filteredMosques = mosques.filter(mosque => {
    const matchesSearch = mosque.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         mosque.address.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCity = selectedCity === 'all' || mosque.address.includes(selectedCity);
    return matchesSearch && matchesCity;
  });

  return (
    <div className="min-h-screen bg-white">
      <Breadcrumbs items={[
        { name: 'Moskeeën' }
      ]} />
      
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Onze Moskeeën
          </h1>
          <p className="text-gray-600 text-lg">
            Ontdek alle aangesloten moskeeën in Gent en hun diensten.
          </p>
        </div>

        {/* Search and Filters */}
        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Zoeken
              </label>
              <div className="relative">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Naam of adres..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Stad
              </label>
              <select
                value={selectedCity}
                onChange={(e) => setSelectedCity(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                {cities.map((city) => (
                  <option key={city} value={city}>
                    {city === 'all' ? 'Alle steden' : city}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <div className="flex gap-2">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-md ${
                    viewMode === 'grid'
                      ? 'bg-teal-600 text-white'
                      : 'bg-white text-gray-700 border border-gray-300'
                  }`}
                >
                  <Squares2X2Icon className="h-5 w-5" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-md ${
                    viewMode === 'list'
                      ? 'bg-teal-600 text-white'
                      : 'bg-white text-gray-700 border border-gray-300'
                  }`}
                >
                  <ListBulletIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Results Count */}
        <div className="mb-6">
          <p className="text-gray-600">
            {filteredMosques.length} moskee{filteredMosques.length !== 1 ? 'ën' : ''} gevonden
          </p>
        </div>

        {/* Mosques Grid/List */}
        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredMosques.map((mosque) => (
              <div key={mosque.id} className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
                {/* Mosque Image */}
                <div className="h-48 bg-gray-200 flex items-center justify-center">
                  <div className="w-20 h-20 bg-teal-100 rounded-full flex items-center justify-center">
                    <svg className="w-10 h-10 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                </div>
                
                <div className="p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {mosque.name}
                  </h3>
                  
                  <div className="flex items-center mb-3">
                    <MapPinIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <span className="text-sm text-gray-600">{mosque.address}</span>
                  </div>
                  
                  <div className="flex items-center mb-3">
                    <PhoneIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <span className="text-sm text-gray-600">{mosque.phone}</span>
                  </div>
                  
                  <div className="flex items-center mb-4">
                    <CalendarIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <span className="text-sm text-gray-600">{mosque.events.length} evenementen</span>
                  </div>
                  
                  <div className="flex flex-wrap gap-1 mb-4">
                    {mosque.features.slice(0, 3).map((feature, index) => (
                      <span key={index} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-teal-100 text-teal-800">
                        {feature}
                      </span>
                    ))}
                    {mosque.features.length > 3 && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        +{mosque.features.length - 3}
                      </span>
                    )}
                  </div>
                  
                  <Link
                    href={`/mosques/${mosque.id}`}
                    className="w-full bg-teal-600 text-white px-4 py-2 rounded-md hover:bg-teal-700 transition-colors"
                  >
                    Meer informatie
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {filteredMosques.map((mosque) => (
              <div key={mosque.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      {mosque.name}
                    </h3>
                    
                    <p className="text-gray-600 mb-4">
                      {mosque.description}
                    </p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div className="flex items-center text-gray-600">
                        <MapPinIcon className="h-4 w-4 mr-2" />
                        <span>{mosque.address}</span>
                      </div>
                      <div className="flex items-center text-gray-600">
                        <PhoneIcon className="h-4 w-4 mr-2" />
                        <span>{mosque.phone}</span>
                      </div>
                      <div className="flex items-center text-gray-600">
                        <UsersIcon className="h-4 w-4 mr-2" />
                        <span>Capaciteit: {mosque.capacity}</span>
                      </div>
                      <div className="flex items-center text-gray-600">
                        <CalendarIcon className="h-4 w-4 mr-2" />
                        <span>{mosque.events.length} evenementen</span>
                      </div>
                    </div>
                    
                    <div className="flex flex-wrap gap-2">
                      {mosque.features.map((feature, index) => (
                        <span key={index} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-teal-100 text-teal-800">
                          {feature}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="mt-4 md:mt-0 md:ml-6">
                    <Link
                      href={`/mosques/${mosque.id}`}
                      className="bg-teal-600 text-white px-6 py-2 rounded-md hover:bg-teal-700 transition-colors"
                    >
                      Meer Details
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {filteredMosques.length === 0 && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <MagnifyingGlassIcon className="h-8 w-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Geen moskeeën gevonden
            </h3>
            <p className="text-gray-500">
              Probeer een andere zoekterm of filter.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
