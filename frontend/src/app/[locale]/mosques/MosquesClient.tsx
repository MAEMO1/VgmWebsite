'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import GoogleMaps from '@/components/maps/GoogleMaps';
import type { Mosque } from '@/types/api';
import { 
  MapIcon, 
  BuildingOfficeIcon, 
  MapPinIcon, 
  EnvelopeIcon,
  PhoneIcon,
  UserIcon
} from '@heroicons/react/24/outline';

export default function MosquesClient() {
  const t = useTranslations('Mosques');
  const router = useRouter();
  const [mosques, setMosques] = useState<Mosque[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedMosque, setSelectedMosque] = useState<Mosque | null>(null);
  const [viewMode, setViewMode] = useState<'list' | 'map'>('list');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadMosques();
  }, []);

  const loadMosques = async () => {
    try {
      setLoading(true);
      // Use local API route for Vercel deployment
      const response = await fetch('/api/mosques');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      setMosques(data.data || data);
    } catch (error) {
      console.error('Error loading mosques:', error);
      setError('Failed to load mosques');
    } finally {
      setLoading(false);
    }
  };

  const handleMosqueSelect = (mosque: Mosque) => {
    // Navigate to mosque detail page
    router.push(`/mosques/${mosque.id}`);
  };

  const filteredMosques = mosques.filter(mosque => {
    const matchesSearch = !searchTerm || 
      mosque.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      mosque.address.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (mosque.description && mosque.description.toLowerCase().includes(searchTerm.toLowerCase()));
    
    return matchesSearch;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={loadMosques}
            className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              {t('title')}
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              {t('subtitle')}
            </p>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
            {/* Search */}
            <div className="flex-1 max-w-md">
              <input
                type="text"
                placeholder={t('searchPlaceholder')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>


            {/* View Toggle */}
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('list')}
                className={`px-4 py-2 rounded-md transition-colors ${
                  viewMode === 'list' 
                    ? 'bg-white text-primary shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <BuildingOfficeIcon className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('map')}
                className={`px-4 py-2 rounded-md transition-colors ${
                  viewMode === 'map' 
                    ? 'bg-white text-primary shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <MapIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="mb-4">
          <p className="text-gray-600">
            {filteredMosques.length} van {mosques.length} moskeeën
          </p>
        </div>

        {/* Content */}
        {viewMode === 'list' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredMosques.map((mosque) => (
              <div
                key={mosque.id}
                className="bg-white rounded-lg shadow-md overflow-hidden cursor-pointer transition-all duration-200 hover:shadow-lg"
                onClick={() => router.push(`/mosques/${mosque.id}`)}
              >
                <div className="h-48 bg-gray-200 flex items-center justify-center">
                  <BuildingOfficeIcon className="w-16 h-16 text-gray-400" />
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {mosque.name}
                  </h3>
                  <div className="space-y-2 text-gray-600">
                    <div className="flex items-center">
                      <MapPinIcon className="w-4 h-4 mr-2" />
                      <span className="text-sm">{mosque.address}</span>
                    </div>
                    <div className="flex items-center">
                      <UserIcon className="w-4 h-4 mr-2" />
                      <span className="text-sm">{mosque.imam_name}</span>
                    </div>
                    <div className="flex items-center">
                      <BuildingOfficeIcon className="w-4 h-4 mr-2" />
                      <span className="text-sm">{mosque.capacity} personen</span>
                    </div>
                  </div>
                  <p className="text-gray-600 text-sm mt-3 line-clamp-2">
                    {mosque.description}
                  </p>
                  <div className="flex gap-2 mt-4">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        router.push(`/mosques/${mosque.id}`);
                      }}
                      className="flex-1 bg-primary hover:bg-primary-dark text-white font-medium py-2 px-4 rounded-md transition-colors"
                    >
                      View Details
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedMosque(mosque);
                        setViewMode('map');
                      }}
                      className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-2 px-4 rounded-md transition-colors"
                    >
                      View on Map
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <GoogleMaps
              mosques={filteredMosques}
              selectedMosqueId={selectedMosque?.id}
              onMosqueSelect={handleMosqueSelect}
            />
          </div>
        )}

        {filteredMosques.length === 0 && (
          <div className="text-center py-12">
            <BuildingOfficeIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Geen moskeeën gevonden
            </h3>
            <p className="text-gray-600">
              Probeer uw zoekcriteria aan te passen.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
