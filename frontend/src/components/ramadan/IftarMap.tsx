'use client';

import { useEffect, useRef, useState } from 'react';
import { useTranslations } from 'next-intl';

declare global {
  interface Window {
    google: any;
    initMap: () => void;
  }
}

export function IftarMap() {
  const t = useTranslations('IftarMap');
  const mapRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<any>(null);
  const [markers, setMarkers] = useState<any[]>([]);
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    // Load Google Maps script
    if (!window.google) {
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&callback=initMap`;
      script.async = true;
      script.defer = true;
      document.head.appendChild(script);

      window.initMap = () => {
        if (mapRef.current) {
          const belgium = { lat: 50.8503, lng: 4.3517 };
          const newMap = new window.google.maps.Map(mapRef.current, {
            zoom: 8,
            center: belgium,
            styles: [
              {
                featureType: 'poi',
                elementType: 'labels',
                stylers: [{ visibility: 'off' }],
              },
            ],
          });
          setMap(newMap);
        }
      };
    } else if (mapRef.current && !map) {
      const belgium = { lat: 50.8503, lng: 4.3517 };
      const newMap = new window.google.maps.Map(mapRef.current, {
        zoom: 8,
        center: belgium,
        styles: [
          {
            featureType: 'poi',
            elementType: 'labels',
            stylers: [{ visibility: 'off' }],
          },
        ],
      });
      setMap(newMap);
    }
  }, [map]);

  useEffect(() => {
    // Fetch events data
    const fetchEvents = async () => {
      try {
        const response = await fetch('/api/proxy/ramadan/iftar-map');
        if (response.ok) {
          const data = await response.json();
          setEvents(data.events_json || []);
        }
      } catch (error) {
        console.error('Error fetching events:', error);
      }
    };

    fetchEvents();
  }, []);

  useEffect(() => {
    if (map && events.length > 0) {
      // Clear existing markers
      markers.forEach(marker => marker.setMap(null));
      const newMarkers: any[] = [];

      const bounds = new window.google.maps.LatLngBounds();
      let hasValidMarkers = false;

      events.forEach(event => {
        if (event.latitude && event.longitude) {
          hasValidMarkers = true;
          const position = {
            lat: parseFloat(event.latitude),
            lng: parseFloat(event.longitude),
          };
          bounds.extend(position);

          const marker = new window.google.maps.Marker({
            position: position,
            map: map,
            title: event.mosque_name,
          });

          const content = `
            <div class="p-4">
              <h6 class="font-semibold text-lg">${event.mosque_name}</h6>
              <p class="text-sm text-gray-600">${event.date} ${event.start_time}</p>
              <p class="text-sm text-gray-600">${event.location}</p>
              ${event.is_family_friendly ? 
                '<span class="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full mt-2">Gezinsvriendelijk</span>' : 
                ''}
            </div>
          `;

          const infowindow = new window.google.maps.InfoWindow({ content });
          marker.addListener('click', () => infowindow.open(map, marker));
          newMarkers.push(marker);
        }
      });

      setMarkers(newMarkers);

      if (hasValidMarkers) {
        map.fitBounds(bounds);
        const listener = window.google.maps.event.addListener(map, 'idle', () => {
          if (map.getZoom() > 12) map.setZoom(12);
          window.google.maps.event.removeListener(listener);
        });
      }
    }
  }, [map, events, markers]);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              {t('map.title')}
            </h2>
            <div
              ref={mapRef}
              className="w-full h-96 rounded-lg border border-gray-200"
              style={{ minHeight: '400px' }}
            />
          </div>
        </div>
        
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {t('events.title')}
            </h3>
            {events.length > 0 ? (
              <div className="space-y-3">
                {events.slice(0, 5).map((event, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-3">
                    <h4 className="font-medium text-gray-900">{event.mosque_name}</h4>
                    <p className="text-sm text-gray-600">{event.date} {event.start_time}</p>
                    <p className="text-sm text-gray-600">{event.location}</p>
                    {event.is_family_friendly && (
                      <span className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full mt-2">
                        {t('events.familyFriendly')}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">
                {t('events.noEvents')}
              </p>
            )}
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {t('prayerTimes.title')}
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Fajr</span>
                <span className="text-gray-600">--:--</span>
              </div>
              <div className="flex justify-between">
                <span>Dhuhr</span>
                <span className="text-gray-600">--:--</span>
              </div>
              <div className="flex justify-between">
                <span>Asr</span>
                <span className="text-gray-600">--:--</span>
              </div>
              <div className="flex justify-between">
                <span>Maghrib</span>
                <span className="text-gray-600">--:--</span>
              </div>
              <div className="flex justify-between">
                <span>Isha</span>
                <span className="text-gray-600">--:--</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
