'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { 
  MagnifyingGlassIcon, 
  MapPinIcon, 
  PhoneIcon, 
  EnvelopeIcon,
  ClockIcon,
  UsersIcon,
  FunnelIcon
} from '@heroicons/react/24/outline';

interface Mosque {
  id: number;
  name: string;
  address: string;
  phone?: string;
  email?: string;
  capacity?: number;
  imamName?: string;
  establishedYear?: number;
  description?: string;
  latitude?: number;
  longitude?: number;
  services?: string[];
  features?: string[];
}

export default function MosqueSearchPage() {
  const t = useTranslations('MosqueSearch');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedServices, setSelectedServices] = useState<string[]>([]);
  const [selectedFeatures, setSelectedFeatures] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState('name');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [mosques, setMosques] = useState<Mosque[]>([]);
  const [loading, setLoading] = useState(true);

  // Mock data - in real app this would come from API
  const mockMosques: Mosque[] = [
    {
      id: 1,
      name: 'Moskee Salahaddien',
      address: 'Sint-Pietersnieuwstraat 120, 9000 Gent',
      phone: '+32 9 123 45 67',
      email: 'info@salahaddien.be',
      capacity: 500,
      imamName: 'Sheikh Ahmed Al-Mansouri',
      establishedYear: 1985,
      description: 'Moskee Salahaddien is een van de oudste en grootste moskeeën in Gent.',
      latitude: 51.0543,
      longitude: 3.7174,
      services: ['Vrijdaggebed', 'Dagelijkse gebeden', 'Koranlessen', 'Arabische lessen'],
      features: ['Parking', 'Vrouwenafdeling', 'Rolstoeltoegankelijk']
    },
    {
      id: 2,
      name: 'Moskee Al-Fath',
      address: 'Korte Meer 11, 9000 Gent',
      phone: '+32 9 234 56 78',
      email: 'info@alfath.be',
      capacity: 350,
      imamName: 'Sheikh Ibrahim Al-Turk',
      establishedYear: 1992,
      description: 'Moskee Al-Fath is gelegen in het centrum van Gent en richt zich op educatie en gemeenschapsopbouw.',
      latitude: 51.0538,
      longitude: 3.7251,
      services: ['Vrijdaggebed', 'Dagelijkse gebeden', 'Jeugdprogramma\'s', 'Vrouwenprogramma\'s'],
      features: ['Parking', 'Vrouwenafdeling', 'Kinderruimte']
    }
  ];

  const services = [
    'Vrijdaggebed',
    'Dagelijkse gebeden',
    'Koranlessen',
    'Arabische lessen',
    'Jeugdprogramma\'s',
    'Vrouwenprogramma\'s',
    'Begrafenisgebeden',
    'Gemeenschapsevenementen'
  ];

  const features = [
    'Parking',
    'Vrouwenafdeling',
    'Rolstoeltoegankelijk',
    'Kinderruimte',
    'Airconditioning',
    'Bibliotheek',
    'Cafetaria'
  ];

  useEffect(() => {
    // Simulate API call
    const loadMosques = async () => {
      setTimeout(() => {
        setMosques(mockMosques);
        setLoading(false);
      }, 1000);
    };
    loadMosques();
  }, []);

  const filteredMosques = mosques.filter(mosque => {
    const matchesSearch = mosque.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         mosque.address.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         mosque.description?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesServices = selectedServices.length === 0 || 
                           selectedServices.every(service => mosque.services?.includes(service));
    
    const matchesFeatures = selectedFeatures.length === 0 || 
                           selectedFeatures.every(feature => mosque.features?.includes(feature));
    
    return matchesSearch && matchesServices && matchesFeatures;
  });

  const sortedMosques = [...filteredMosques].sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return a.name.localeCompare(b.name);
      case 'capacity':
        return (b.capacity || 0) - (a.capacity || 0);
      case 'established':
        return (b.establishedYear || 0) - (a.establishedYear || 0);
      default:
        return 0;
    }
  });

  const handleServiceToggle = (service: string) => {
    setSelectedServices(prev => 
      prev.includes(service) 
        ? prev.filter(s => s !== service)
        : [...prev, service]
    );
  };

  const handleFeatureToggle = (feature: string) => {
    setSelectedFeatures(prev => 
      prev.includes(feature) 
        ? prev.filter(f => f !== feature)
        : [...prev, feature]
    );
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedServices([]);
    setSelectedFeatures([]);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white">
        <Breadcrumbs items={[
          { name: 'Moskeeën', href: '/mosques' },
          { name: 'Zoeken' }
        ]} />
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-64 mx-auto mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-96 mx-auto mb-12"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="bg-gray-200 rounded-2xl h-64"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <Breadcrumbs items={[
        { name: 'Moskeeën', href: '/mosques' },
        { name: 'Zoeken' }
      ]} />

      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Moskee Zoeken
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Vind moskeeën in Gent op basis van locatie, diensten en faciliteiten
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white border border-gray-200 rounded-2xl p-6 sticky top-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
                <button
                  onClick={clearFilters}
                  className="text-sm text-teal-600 hover:text-teal-700"
                >
                  Alles wissen
                </button>
              </div>

              {/* Search */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Zoeken
                </label>
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                    placeholder="Naam, adres, beschrijving..."
                  />
                </div>
              </div>

              {/* Services Filter */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-3">Diensten</h3>
                <div className="space-y-2">
                  {services.map((service) => (
                    <label key={service} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedServices.includes(service)}
                        onChange={() => handleServiceToggle(service)}
                        className="h-4 w-4 text-teal-600 focus:ring-teal-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm text-gray-700">{service}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Features Filter */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-3">Faciliteiten</h3>
                <div className="space-y-2">
                  {features.map((feature) => (
                    <label key={feature} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedFeatures.includes(feature)}
                        onChange={() => handleFeatureToggle(feature)}
                        className="h-4 w-4 text-teal-600 focus:ring-teal-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm text-gray-700">{feature}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Sort */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">Sorteren op</h3>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                >
                  <option value="name">Naam</option>
                  <option value="capacity">Capaciteit</option>
                  <option value="established">Oprichtingsjaar</option>
                </select>
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="lg:col-span-3">
            {/* Results Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  {sortedMosques.length} moskee{ sortedMosques.length !== 1 ? 'ën' : ''} gevonden
                </h2>
                {(selectedServices.length > 0 || selectedFeatures.length > 0) && (
                  <p className="text-sm text-gray-500 mt-1">
                    Gefilterd op {selectedServices.length + selectedFeatures.length} criteria
                  </p>
                )}
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-lg ${
                    viewMode === 'grid' 
                      ? 'bg-teal-100 text-teal-600' 
                      : 'text-gray-400 hover:text-gray-600'
                  }`}
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                  </svg>
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-lg ${
                    viewMode === 'list' 
                      ? 'bg-teal-100 text-teal-600' 
                      : 'text-gray-400 hover:text-gray-600'
                  }`}
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Results Grid/List */}
            {sortedMosques.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <MagnifyingGlassIcon className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Geen moskeeën gevonden</h3>
                <p className="text-gray-500 mb-6">
                  Probeer uw zoekcriteria aan te passen of filters te verwijderen.
                </p>
                <button
                  onClick={clearFilters}
                  className="bg-teal-600 text-white px-6 py-3 rounded-lg hover:bg-teal-700 transition-colors"
                >
                  Filters wissen
                </button>
              </div>
            ) : (
              <div className={viewMode === 'grid' 
                ? 'grid grid-cols-1 md:grid-cols-2 gap-6' 
                : 'space-y-6'
              }>
                {sortedMosques.map((mosque) => (
                  <div key={mosque.id} className={`bg-white border border-gray-200 rounded-2xl overflow-hidden hover:shadow-lg transition-shadow ${
                    viewMode === 'list' ? 'flex' : ''
                  }`}>
                    {/* Image */}
                    <div className={`bg-gray-200 flex items-center justify-center ${
                      viewMode === 'list' ? 'w-48 h-32' : 'h-48'
                    }`}>
                      <span className="text-gray-500">Moskee Afbeelding</span>
                    </div>

                    {/* Content */}
                    <div className={`p-6 ${viewMode === 'list' ? 'flex-1' : ''}`}>
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">{mosque.name}</h3>
                      
                      <div className="flex items-start mb-3">
                        <MapPinIcon className="w-5 h-5 text-gray-400 mr-2 mt-0.5" />
                        <p className="text-gray-600">{mosque.address}</p>
                      </div>

                      {mosque.description && (
                        <p className="text-gray-600 mb-4 line-clamp-2">{mosque.description}</p>
                      )}

                      {/* Details */}
                      <div className="grid grid-cols-2 gap-4 mb-4 text-sm text-gray-600">
                        {mosque.capacity && (
                          <div className="flex items-center">
                            <UsersIcon className="w-4 h-4 mr-1" />
                            <span>{mosque.capacity} personen</span>
                          </div>
                        )}
                        {mosque.establishedYear && (
                          <div className="flex items-center">
                            <ClockIcon className="w-4 h-4 mr-1" />
                            <span>Sinds {mosque.establishedYear}</span>
                          </div>
                        )}
                        {mosque.phone && (
                          <div className="flex items-center">
                            <PhoneIcon className="w-4 h-4 mr-1" />
                            <span>{mosque.phone}</span>
                          </div>
                        )}
                        {mosque.email && (
                          <div className="flex items-center">
                            <EnvelopeIcon className="w-4 h-4 mr-1" />
                            <span>{mosque.email}</span>
                          </div>
                        )}
                      </div>

                      {/* Services */}
                      {mosque.services && mosque.services.length > 0 && (
                        <div className="mb-4">
                          <div className="flex flex-wrap gap-1">
                            {mosque.services.slice(0, 3).map((service) => (
                              <span key={service} className="bg-teal-100 text-teal-800 text-xs px-2 py-1 rounded-full">
                                {service}
                              </span>
                            ))}
                            {mosque.services.length > 3 && (
                              <span className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">
                                +{mosque.services.length - 3} meer
                              </span>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Action */}
                      <button className="w-full bg-teal-600 text-white py-2 rounded-lg hover:bg-teal-700 transition-colors">
                        Bekijk Details
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
