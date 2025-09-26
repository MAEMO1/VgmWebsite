'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { 
  BuildingOfficeIcon, 
  MapPinIcon, 
  PhoneIcon, 
  EnvelopeIcon,
  UserIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

export default function MosqueRegistrationPage() {
  const t = useTranslations('MosqueRegistration');
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    // Basic Information
    mosqueName: '',
    address: '',
    city: 'Gent',
    postalCode: '',
    phone: '',
    email: '',
    website: '',
    
    // Contact Person
    contactName: '',
    contactPhone: '',
    contactEmail: '',
    contactRole: '',
    
    // Mosque Details
    establishedYear: '',
    capacity: '',
    imamName: '',
    imamPhone: '',
    imamEmail: '',
    
    // Services
    services: {
      fridayPrayer: false,
      dailyPrayers: false,
      quranClasses: false,
      arabicClasses: false,
      youthPrograms: false,
      womenPrograms: false,
      janazahServices: false,
      communityEvents: false
    },
    
    // Additional Information
    description: '',
    specialFeatures: '',
    parkingAvailable: false,
    wheelchairAccessible: false,
    womenSection: false,
    childrenArea: false
  });

  const steps = [
    { id: 1, name: 'Basis Informatie', description: 'Moskee gegevens' },
    { id: 2, name: 'Contact Persoon', description: 'Vertegenwoordiger' },
    { id: 3, name: 'Moskee Details', description: 'Imam en capaciteit' },
    { id: 4, name: 'Diensten', description: 'Aangeboden diensten' },
    { id: 5, name: 'Bevestiging', description: 'Controle en verzenden' }
  ];

  const handleInputChange = (field: string, value: any) => {
    if (field.startsWith('services.')) {
      const serviceKey = field.split('.')[1];
      setFormData(prev => ({
        ...prev,
        services: {
          ...prev.services,
          [serviceKey]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  const nextStep = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission
    console.log('Form submitted:', formData);
    alert('Registratie succesvol verzonden! We nemen binnen 2 werkdagen contact met u op.');
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Moskee Naam *
              </label>
              <input
                type="text"
                value={formData.mosqueName}
                onChange={(e) => handleInputChange('mosqueName', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                placeholder="Bijv. Centrale Moskee Gent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Adres *
              </label>
              <input
                type="text"
                value={formData.address}
                onChange={(e) => handleInputChange('address', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                placeholder="Straat en huisnummer"
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Postcode *
                </label>
                <input
                  type="text"
                  value={formData.postalCode}
                  onChange={(e) => handleInputChange('postalCode', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  placeholder="9000"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stad
                </label>
                <input
                  type="text"
                  value={formData.city}
                  onChange={(e) => handleInputChange('city', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  readOnly
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Telefoon
                </label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  placeholder="+32 9 123 45 67"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  E-mail
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  placeholder="info@moskee.be"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Website
              </label>
              <input
                type="url"
                value={formData.website}
                onChange={(e) => handleInputChange('website', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                placeholder="https://www.moskee.be"
              />
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Naam Contact Persoon *
              </label>
              <input
                type="text"
                value={formData.contactName}
                onChange={(e) => handleInputChange('contactName', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                placeholder="Volledige naam"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Functie/Rol
              </label>
              <input
                type="text"
                value={formData.contactRole}
                onChange={(e) => handleInputChange('contactRole', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                placeholder="Bijv. Voorzitter, Secretaris, Imam"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Telefoon Contact Persoon
                </label>
                <input
                  type="tel"
                  value={formData.contactPhone}
                  onChange={(e) => handleInputChange('contactPhone', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  placeholder="+32 9 123 45 67"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  E-mail Contact Persoon
                </label>
                <input
                  type="email"
                  value={formData.contactEmail}
                  onChange={(e) => handleInputChange('contactEmail', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  placeholder="contact@moskee.be"
                />
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Oprichtingsjaar
                </label>
                <input
                  type="number"
                  value={formData.establishedYear}
                  onChange={(e) => handleInputChange('establishedYear', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  placeholder="1985"
                  min="1900"
                  max="2025"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Capaciteit
                </label>
                <input
                  type="number"
                  value={formData.capacity}
                  onChange={(e) => handleInputChange('capacity', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  placeholder="500"
                  min="1"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Imam Naam
              </label>
              <input
                type="text"
                value={formData.imamName}
                onChange={(e) => handleInputChange('imamName', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                placeholder="Volledige naam van de imam"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Imam Telefoon
                </label>
                <input
                  type="tel"
                  value={formData.imamPhone}
                  onChange={(e) => handleInputChange('imamPhone', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  placeholder="+32 9 123 45 67"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Imam E-mail
                </label>
                <input
                  type="email"
                  value={formData.imamEmail}
                  onChange={(e) => handleInputChange('imamEmail', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  placeholder="imam@moskee.be"
                />
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Aangeboden Diensten</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(formData.services).map(([key, value]) => (
                  <label key={key} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={(e) => handleInputChange(`services.${key}`, e.target.checked)}
                      className="h-4 w-4 text-teal-600 focus:ring-teal-500 border-gray-300 rounded"
                    />
                    <span className="ml-3 text-sm text-gray-700">
                      {key === 'fridayPrayer' && 'Vrijdaggebed'}
                      {key === 'dailyPrayers' && 'Dagelijkse gebeden'}
                      {key === 'quranClasses' && 'Koranlessen'}
                      {key === 'arabicClasses' && 'Arabische lessen'}
                      {key === 'youthPrograms' && 'Jeugdprogramma\'s'}
                      {key === 'womenPrograms' && 'Vrouwenprogramma\'s'}
                      {key === 'janazahServices' && 'Begrafenisgebeden'}
                      {key === 'communityEvents' && 'Gemeenschapsevenementen'}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Faciliteiten</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.parkingAvailable}
                    onChange={(e) => handleInputChange('parkingAvailable', e.target.checked)}
                    className="h-4 w-4 text-teal-600 focus:ring-teal-500 border-gray-300 rounded"
                  />
                  <span className="ml-3 text-sm text-gray-700">Parking beschikbaar</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.wheelchairAccessible}
                    onChange={(e) => handleInputChange('wheelchairAccessible', e.target.checked)}
                    className="h-4 w-4 text-teal-600 focus:ring-teal-500 border-gray-300 rounded"
                  />
                  <span className="ml-3 text-sm text-gray-700">Rolstoeltoegankelijk</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.womenSection}
                    onChange={(e) => handleInputChange('womenSection', e.target.checked)}
                    className="h-4 w-4 text-teal-600 focus:ring-teal-500 border-gray-300 rounded"
                  />
                  <span className="ml-3 text-sm text-gray-700">Vrouwenafdeling</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.childrenArea}
                    onChange={(e) => handleInputChange('childrenArea', e.target.checked)}
                    className="h-4 w-4 text-teal-600 focus:ring-teal-500 border-gray-300 rounded"
                  />
                  <span className="ml-3 text-sm text-gray-700">Kinderruimte</span>
                </label>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Beschrijving
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                placeholder="Beschrijf uw moskee, geschiedenis, speciale kenmerken..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Speciale Kenmerken
              </label>
              <textarea
                value={formData.specialFeatures}
                onChange={(e) => handleInputChange('specialFeatures', e.target.value)}
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                placeholder="Bijzondere architectuur, historische waarde, speciale programma's..."
              />
            </div>
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <div className="bg-teal-50 rounded-lg p-6">
              <div className="flex items-center mb-4">
                <CheckCircleIcon className="w-8 h-8 text-teal-600 mr-3" />
                <h3 className="text-lg font-medium text-gray-900">Controleer uw gegevens</h3>
              </div>
              <p className="text-gray-600">
                Controleer alle ingevulde gegevens voordat u de registratie verzendt. 
                We nemen binnen 2 werkdagen contact met u op voor verdere stappen.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900">Moskee Informatie</h4>
                <p className="text-gray-600">{formData.mosqueName}</p>
                <p className="text-gray-600">{formData.address}, {formData.postalCode} {formData.city}</p>
                {formData.phone && <p className="text-gray-600">Tel: {formData.phone}</p>}
                {formData.email && <p className="text-gray-600">E-mail: {formData.email}</p>}
              </div>

              <div>
                <h4 className="font-medium text-gray-900">Contact Persoon</h4>
                <p className="text-gray-600">{formData.contactName}</p>
                {formData.contactRole && <p className="text-gray-600">Functie: {formData.contactRole}</p>}
                {formData.contactPhone && <p className="text-gray-600">Tel: {formData.contactPhone}</p>}
                {formData.contactEmail && <p className="text-gray-600">E-mail: {formData.contactEmail}</p>}
              </div>

              {formData.imamName && (
                <div>
                  <h4 className="font-medium text-gray-900">Imam</h4>
                  <p className="text-gray-600">{formData.imamName}</p>
                  {formData.imamPhone && <p className="text-gray-600">Tel: {formData.imamPhone}</p>}
                  {formData.imamEmail && <p className="text-gray-600">E-mail: {formData.imamEmail}</p>}
                </div>
              )}

              <div>
                <h4 className="font-medium text-gray-900">Diensten</h4>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(formData.services)
                    .filter(([_, value]) => value)
                    .map(([key, _]) => (
                      <span key={key} className="bg-teal-100 text-teal-800 text-xs px-2 py-1 rounded-full">
                        {key === 'fridayPrayer' && 'Vrijdaggebed'}
                        {key === 'dailyPrayers' && 'Dagelijkse gebeden'}
                        {key === 'quranClasses' && 'Koranlessen'}
                        {key === 'arabicClasses' && 'Arabische lessen'}
                        {key === 'youthPrograms' && 'Jeugdprogramma\'s'}
                        {key === 'womenPrograms' && 'Vrouwenprogramma\'s'}
                        {key === 'janazahServices' && 'Begrafenisgebeden'}
                        {key === 'communityEvents' && 'Gemeenschapsevenementen'}
                      </span>
                    ))}
                </div>
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
        { name: 'Registratie' }
      ]} />

      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Moskee Registratie
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Registreer uw moskee bij de Vereniging van Gentse Moskeeën en word onderdeel van onze gemeenschap
          </p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                  currentStep >= step.id
                    ? 'bg-teal-600 border-teal-600 text-white'
                    : 'border-gray-300 text-gray-500'
                }`}>
                  {currentStep > step.id ? (
                    <CheckCircleIcon className="w-6 h-6" />
                  ) : (
                    <span className="text-sm font-medium">{step.id}</span>
                  )}
                </div>
                <div className="ml-3 hidden sm:block">
                  <p className={`text-sm font-medium ${
                    currentStep >= step.id ? 'text-teal-600' : 'text-gray-500'
                  }`}>
                    {step.name}
                  </p>
                  <p className="text-xs text-gray-500">{step.description}</p>
                </div>
                {index < steps.length - 1 && (
                  <div className={`hidden sm:block w-16 h-0.5 mx-4 ${
                    currentStep > step.id ? 'bg-teal-600' : 'bg-gray-300'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white border border-gray-200 rounded-2xl p-8">
          {renderStepContent()}

          {/* Navigation Buttons */}
          <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={prevStep}
              disabled={currentStep === 1}
              className={`px-6 py-3 rounded-lg font-medium ${
                currentStep === 1
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Vorige
            </button>

            {currentStep < steps.length ? (
              <button
                type="button"
                onClick={nextStep}
                className="px-6 py-3 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 transition-colors"
              >
                Volgende
              </button>
            ) : (
              <button
                type="submit"
                className="px-6 py-3 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 transition-colors"
              >
                Registratie Verzenden
              </button>
            )}
          </div>
        </form>

        {/* Information Box */}
        <div className="mt-8 bg-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-medium text-blue-900 mb-2">Wat gebeurt er na registratie?</h3>
          <ul className="text-blue-800 space-y-2">
            <li>• We nemen binnen 2 werkdagen contact met u op</li>
            <li>• We plannen een bezoek aan uw moskee</li>
            <li>• We beoordelen de registratie en VGM-lidmaatschap</li>
            <li>• Bij goedkeuring wordt uw moskee toegevoegd aan onze directory</li>
            <li>• U krijgt toegang tot VGM-diensten en evenementen</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
