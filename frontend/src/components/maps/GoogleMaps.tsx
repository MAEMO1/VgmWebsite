'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Loader } from '@googlemaps/js-api-loader';
import type { Mosque } from '@/types/api';

interface GoogleMapsProps {
  mosques: Mosque[];
  onMosqueSelect?: (mosque: Mosque) => void;
  selectedMosqueId?: number;
  height?: string;
  showSearch?: boolean;
}

export default function GoogleMaps({
  mosques,
  onMosqueSelect,
  selectedMosqueId,
  height = '400px',
  showSearch = true
}: GoogleMapsProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<google.maps.Map | null>(null);
  const [markers, setMarkers] = useState<google.maps.Marker[]>([]);
  const [infoWindow, setInfoWindow] = useState<google.maps.InfoWindow | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initMap = async () => {
      try {
        setLoading(true);
        setError(null);

        const loader = new Loader({
          apiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '',
          version: 'weekly',
          libraries: ['places']
        });

        const { Map } = await loader.importLibrary('maps');
        const { Marker } = await loader.importLibrary('marker');

        if (!mapRef.current) return;

        // Initialize map centered on Gent, Belgium
        const mapInstance = new Map(mapRef.current, {
          center: { lat: 51.0543, lng: 3.7174 },
          zoom: 13,
          mapTypeId: 'roadmap',
          styles: [
            {
              featureType: 'poi',
              elementType: 'labels',
              stylers: [{ visibility: 'off' }]
            }
          ]
        });

        setMap(mapInstance);

        // Initialize info window
        const infoWindowInstance = new google.maps.InfoWindow();
        setInfoWindow(infoWindowInstance);

        // Create markers for each mosque
        const newMarkers: google.maps.Marker[] = [];
        
        mosques.forEach((mosque) => {
          if (mosque.latitude && mosque.longitude) {
            const marker = new Marker({
              position: { lat: mosque.latitude, lng: mosque.longitude },
              map: mapInstance,
              title: mosque.name,
              icon: {
                url: '/images/mosque-marker.png',
                scaledSize: new google.maps.Size(40, 40),
                anchor: new google.maps.Point(20, 40)
              }
            });

            // Create info window content
            const infoContent = `
              <div class="p-4 max-w-sm">
                <h3 class="text-lg font-bold text-gray-900 mb-2">${mosque.name}</h3>
                <p class="text-sm text-gray-600 mb-2">${mosque.address}</p>
                ${mosque.phone ? `<p class="text-sm text-gray-600 mb-1">📞 ${mosque.phone}</p>` : ''}
                ${mosque.email ? `<p class="text-sm text-gray-600 mb-1">✉️ ${mosque.email}</p>` : ''}
                ${mosque.website ? `<p class="text-sm text-gray-600 mb-1">🌐 ${mosque.website}</p>` : ''}
                ${mosque.capacity ? `<p class="text-sm text-gray-600 mb-1">👥 Capacity: ${mosque.capacity}</p>` : ''}
                ${mosque.imam_name ? `<p class="text-sm text-gray-600 mb-2">🕌 Imam: ${mosque.imam_name}</p>` : ''}
                ${mosque.description ? `<p class="text-sm text-gray-700 mb-3">${mosque.description}</p>` : ''}
                <button 
                  onclick="window.selectMosque(${mosque.id})"
                  class="bg-primary text-white px-3 py-1 rounded text-sm hover:bg-primary-dark"
                >
                  View Details
                </button>
              </div>
            `;

            // Add click listener to marker
            marker.addListener('click', () => {
              infoWindowInstance.setContent(infoContent);
              infoWindowInstance.open(mapInstance, marker);
              
              if (onMosqueSelect) {
                onMosqueSelect(mosque);
              }
            });

            newMarkers.push(marker);
          }
        });

        setMarkers(newMarkers);

        // Add search functionality if enabled
        if (showSearch) {
          const { SearchBox } = await loader.importLibrary('places');
          const searchBox = new SearchBox(
            document.getElementById('search-box') as HTMLInputElement
          );

          searchBox.addListener('places_changed', () => {
            const places = searchBox.getPlaces();
            if (places.length === 0) return;

            const place = places[0];
            if (place.geometry && place.geometry.location) {
              mapInstance.setCenter(place.geometry.location);
              mapInstance.setZoom(15);
            }
          });
        }

        setLoading(false);
      } catch (error) {
        console.error('Error initializing Google Maps:', error);
        setError('Failed to load Google Maps');
        setLoading(false);
      }
    };

    initMap();
  }, [mosques, onMosqueSelect, showSearch]);

  // Update selected mosque marker
  useEffect(() => {
    if (map && markers.length > 0 && selectedMosqueId) {
      const selectedMosque = mosques.find(m => m.id === selectedMosqueId);
      if (selectedMosque) {
        map.setCenter({ lat: selectedMosque.latitude, lng: selectedMosque.longitude });
        map.setZoom(16);
      }
    }
  }, [selectedMosqueId, map, markers, mosques]);

  // Expose selectMosque function globally for info window buttons
  useEffect(() => {
    (window as any).selectMosque = (mosqueId: number) => {
      const mosque = mosques.find(m => m.id === mosqueId);
      if (mosque && onMosqueSelect) {
        onMosqueSelect(mosque);
      }
    };

    return () => {
      delete (window as any).selectMosque;
    };
  }, [mosques, onMosqueSelect]);

  if (loading) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading map...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <div className="text-center">
          <div className="text-red-600 text-4xl mb-4">🗺️</div>
          <p className="text-red-600 mb-2">{error}</p>
          <p className="text-gray-600 text-sm">
            Please check your Google Maps API key configuration
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      {showSearch && (
        <div className="mb-4">
          <input
            id="search-box"
            type="text"
            placeholder="Search for mosques or locations..."
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
          />
        </div>
      )}
      
      <div
        ref={mapRef}
        className="w-full rounded-lg shadow-md"
        style={{ height }}
      />
      
      <div className="mt-4 text-sm text-gray-600">
        <p>📍 Click on mosque markers to view details</p>
        <p>🔍 Use the search box to find specific locations</p>
      </div>
    </div>
  );
}
