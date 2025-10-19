'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/api/client';
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

export default function MosquesPage() {
  const t = useTranslations('Mosques');
  const router = useRouter();
  const [mosques, setMosques] = useState<Mosque[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedMosque, setSelectedMosque] = useState<Mosque | null>(null);
  const [viewMode, setViewMode] = useState<'list' | 'map'>('list');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCapacity, setFilterCapacity] = useState<number | null>(null);

  useEffect(() => {
    loadMosques();
  }, []);

  const loadMosques = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get<Mosque[]>('/api/mosques');
      setMosques(response);
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
    const matchesSearch = mosque.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         mosque.address.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         mosque.imam_name?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCapacity = filterCapacity === null || 
                           (mosque.capacity && mosque.capacity >= filterCapacity);
    
    return matchesSearch && matchesCapacity;
  });

  const formatCapacity = (capacity?: number | null) => {
    if (!capacity) return 'N/A';
    return `${capacity} people`;
  };

  const formatYear = (year?: number | null) => {
    if (!year) return 'N/A';
    return year.toString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Error</h1>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => {
              setError('');
              loadMosques();
            }}
            className="btn btn-primary"
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
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              {t('title')}
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              {t('description')}
            </p>
          </div>

          {/* Controls */}
          <div className="flex flex-col lg:flex-row gap-4 mb-6">
            {/* Search */}
            <div className="flex-1">
              <input
                type="text"
                placeholder={t('searchPlaceholder')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
              />
            </div>

            {/* Capacity Filter */}
            <div className="lg:w-48">
              <select
                value={filterCapacity || ''}
                onChange={(e) => setFilterCapacity(e.target.value ? parseInt(e.target.value) : null)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
              >
                <option value="">All Capacities</option>
                <option value="100">100+ people</option>
                <option value="200">200+ people</option>
                <option value="300">300+ people</option>
                <option value="400">400+ people</option>
                <option value="500">500+ people</option>
              </select>
            </div>

            {/* View Toggle */}
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode('list')}
                className={`px-4 py-2 rounded-md font-medium ${
                  viewMode === 'list'
                    ? 'bg-primary text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                📋 List
              </button>
              <button
                onClick={() => setViewMode('map')}
                className={`px-4 py-2 rounded-md font-medium ${
                  viewMode === 'map'
                    ? 'bg-primary text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <MapIcon className="w-5 h-5 text-teal-600" />
                  <span>Map</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {viewMode === 'map' ? (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Mosque Locations
            </h2>
            <GoogleMaps
              mosques={filteredMosques}
              onMosqueSelect={handleMosqueSelect}
              selectedMosqueId={selectedMosque?.id}
              height="600px"
              showSearch={true}
            />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredMosques.map((mosque) => (
              <div
                key={mosque.id}
                className="bg-white rounded-lg shadow-md overflow-hidden cursor-pointer transition-all duration-200 hover:shadow-lg"
                onClick={() => router.push(`/mosques/${mosque.id}`)}
              >
                <div className="p-6">
                  <div className="mb-4">
                    <h3 className="text-xl font-bold text-gray-900 mb-2">
                      {mosque.name}
                    </h3>
                    <p className="text-gray-600 text-sm mb-2">
                      <div className="flex items-center space-x-2 text-gray-600">
                        <MapPinIcon className="w-4 h-4" />
                        <span>{mosque.address}</span>
                      </div>
                    </p>
                    {mosque.imam_name && (
                      <p className="text-gray-600 text-sm mb-2">
                      <div className="flex items-center space-x-2 text-gray-600">
                        <UserIcon className="w-4 h-4" />
                        <span>Imam: {mosque.imam_name}</span>
                      </div>
                      </p>
                    )}
                  </div>

                  <div className="space-y-2 mb-4">
                    {mosque.phone && (
                      <p className="text-sm text-gray-600">
                      <div className="flex items-center space-x-2 text-gray-600">
                        <PhoneIcon className="w-4 h-4" />
                        <span>{mosque.phone}</span>
                      </div>
                      </p>
                    )}
                    {mosque.email && (
                      <p className="text-sm text-gray-600">
                      <div className="flex items-center space-x-2 text-gray-600">
                        <EnvelopeIcon className="w-4 h-4" />
                        <span>{mosque.email}</span>
                      </div>
                      </p>
                    )}
                    {mosque.website && (
                      <p className="text-sm text-gray-600">
                        🌐 {mosque.website}
                      </p>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                    <div>
                      <span className="text-gray-500">Capacity:</span>
                      <p className="font-medium">{formatCapacity(mosque.capacity)}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Established:</span>
                      <p className="font-medium">{formatYear(mosque.established_year)}</p>
                    </div>
                  </div>

                  {mosque.description && (
                    <p className="text-gray-700 text-sm mb-4 line-clamp-3">
                      {mosque.description}
                    </p>
                  )}

                  <div className="flex gap-2">
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
        )}

        {filteredMosques.length === 0 && (
          <div className="text-center py-12">
            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <BuildingOfficeIcon className="w-10 h-10 text-gray-400" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              No Mosques Found
            </h2>
            <p className="text-gray-600">
              Try adjusting your search criteria or filters.
            </p>
          </div>
        )}
      </div>

      {/* Selected Mosque Modal */}
      {selectedMosque && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold text-gray-900">
                  {selectedMosque.name}
                </h2>
                <button
                  onClick={() => setSelectedMosque(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Contact Information
                  </h3>
                  <div className="space-y-2">
                    <p className="text-gray-600">
                      <div className="flex items-center space-x-2 text-gray-600">
                        <MapPinIcon className="w-4 h-4" />
                        <span>{selectedMosque.address}</span>
                      </div>
                    </p>
                    {selectedMosque.phone && (
                      <p className="text-gray-600">
                        📞 {selectedMosque.phone}
                      </p>
                    )}
                    {selectedMosque.email && (
                      <p className="text-gray-600">
                      <div className="flex items-center space-x-2 text-gray-600">
                        <EnvelopeIcon className="w-4 h-4" />
                        <span>{selectedMosque.email}</span>
                      </div>
                      </p>
                    )}
                    {selectedMosque.website && (
                      <p className="text-gray-600">
                        🌐 {selectedMosque.website}
                      </p>
                    )}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Mosque Details
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-gray-500">Capacity:</span>
                      <p className="font-medium">{formatCapacity(selectedMosque.capacity)}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Established:</span>
                      <p className="font-medium">{formatYear(selectedMosque.established_year)}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Imam:</span>
                      <p className="font-medium">{selectedMosque.imam_name || 'N/A'}</p>
                    </div>
                  </div>
                </div>

                {selectedMosque.description && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Description
                    </h3>
                    <p className="text-gray-700">
                      {selectedMosque.description}
                    </p>
                  </div>
                )}

                <div className="flex gap-4 pt-4">
                  <button
                    onClick={() => {
                      setSelectedMosque(null);
                      setViewMode('map');
                    }}
                    className="flex-1 bg-primary hover:bg-primary-dark text-white font-medium py-3 px-4 rounded-md transition-colors"
                  >
                    View on Map
                  </button>
                  <button
                    onClick={() => setSelectedMosque(null)}
                    className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-3 px-4 rounded-md transition-colors"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}