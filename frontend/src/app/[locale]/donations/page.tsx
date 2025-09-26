'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { HeartIcon, CreditCardIcon, BanknotesIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';

export default function DonationsPage() {
  const t = useTranslations('Donations');
  const [activeTab, setActiveTab] = useState('general');

  const tabs = [
    { id: 'general', name: 'Algemene Donaties' },
    { id: 'campaigns', name: 'Campagnes' },
    { id: 'zakat', name: 'Zakat' },
    { id: 'sadaqah', name: 'Sadaqah' }
  ];

  const donationMethods = [
    {
      name: 'Online Donatie',
      description: 'Veilige online betaling via Stripe',
      icon: CreditCardIcon,
      features: ['Visa/Mastercard', 'Bancontact', 'iDEAL', 'Veilig & Snel']
    },
    {
      name: 'Bankoverschrijving',
      description: 'Directe overschrijving naar VGM rekening',
      icon: BanknotesIcon,
      features: ['BE12 3456 7890 1234', 'VGM Gent', 'Structured Message', 'Gratis']
    },
    {
      name: 'Contant',
      description: 'Contante donaties bij moskeeën',
      icon: HeartIcon,
      features: ['Bij alle VGM moskeeën', 'Directe ondersteuning', 'Lokale projecten', 'Persoonlijk contact']
    }
  ];

  const campaigns = [
    {
      id: 1,
      title: 'Moskee Renovatie Project',
      description: 'Ondersteun de renovatie van historische moskeeën in Gent',
      target: 50000,
      current: 32500,
      deadline: '2024-12-31',
      image: '/api/placeholder/400/200'
    },
    {
      id: 2,
      title: 'Educatie Programma',
      description: 'Financiering van islamitische educatie en Arabische lessen',
      target: 25000,
      current: 18750,
      deadline: '2024-11-30',
      image: '/api/placeholder/400/200'
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Breadcrumbs items={[
        { name: 'Donaties' }
      ]} />

      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Steun de VGM Gemeenschap
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Uw donaties helpen bij het onderhouden van moskeeën, educatieve programma's en gemeenschapsdiensten in Gent
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-teal-500 text-teal-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'general' && (
          <div className="space-y-12">
            {/* Donation Methods */}
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-8">Donatie Methoden</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {donationMethods.map((method, index) => (
                  <div key={index} className="bg-white border border-gray-200 rounded-2xl p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-center mb-4">
                      <div className="w-12 h-12 bg-teal-100 rounded-xl flex items-center justify-center mr-4">
                        <method.icon className="w-6 h-6 text-teal-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{method.name}</h3>
                        <p className="text-gray-600">{method.description}</p>
                      </div>
                    </div>
                    <ul className="space-y-2 mb-6">
                      {method.features.map((feature, i) => (
                        <li key={i} className="flex items-center text-sm text-gray-600">
                          <div className="w-1.5 h-1.5 bg-teal-500 rounded-full mr-2"></div>
                          {feature}
                        </li>
                      ))}
                    </ul>
                    <button className="w-full bg-teal-600 text-white py-3 rounded-lg hover:bg-teal-700 transition-colors">
                      {method.name === 'Online Donatie' ? 'Doneer Nu' : 'Meer Info'}
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Security Info */}
            <div className="bg-teal-50 rounded-2xl p-8">
              <div className="flex items-start">
                <ShieldCheckIcon className="w-8 h-8 text-teal-600 mr-4 mt-1" />
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Veilige Donaties</h3>
                  <p className="text-gray-600 mb-4">
                    Alle donaties worden veilig verwerkt en gebruikt voor de doelen die u kiest. 
                    VGM is transparant over het gebruik van donaties en biedt regelmatige updates over projecten.
                  </p>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li>• SSL beveiligde betalingen</li>
                    <li>• Transparante financiële rapportage</li>
                    <li>• Directe projectondersteuning</li>
                    <li>• Belastingaftrekbaar (België)</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'campaigns' && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-8">Actieve Campagnes</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {campaigns.map((campaign) => {
                const progress = (campaign.current / campaign.target) * 100;
                return (
                  <div key={campaign.id} className="bg-white border border-gray-200 rounded-2xl overflow-hidden hover:shadow-lg transition-shadow">
                    <div className="h-48 bg-gray-200 flex items-center justify-center">
                      <span className="text-gray-500">Campagne Afbeelding</span>
                    </div>
                    <div className="p-6">
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">{campaign.title}</h3>
                      <p className="text-gray-600 mb-4">{campaign.description}</p>
                      
                      {/* Progress Bar */}
                      <div className="mb-4">
                        <div className="flex justify-between text-sm text-gray-600 mb-2">
                          <span>€{campaign.current.toLocaleString()}</span>
                          <span>€{campaign.target.toLocaleString()}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-teal-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${Math.min(progress, 100)}%` }}
                          ></div>
                        </div>
                        <div className="text-right text-sm text-gray-500 mt-1">
                          {progress.toFixed(1)}% voltooid
                        </div>
                      </div>

                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-500">
                          Deadline: {new Date(campaign.deadline).toLocaleDateString('nl-NL')}
                        </span>
                        <button className="bg-teal-600 text-white px-6 py-2 rounded-lg hover:bg-teal-700 transition-colors">
                          Steun Campagne
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {activeTab === 'zakat' && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <HeartIcon className="w-8 h-8 text-teal-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Zakat Donaties</h2>
            <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
              Zakat is een van de vijf zuilen van de islam. VGM helpt bij het correct verdelen van Zakat 
              aan degenen die er recht op hebben volgens islamitische principes.
            </p>
            <div className="bg-teal-50 rounded-2xl p-8 max-w-4xl mx-auto">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Zakat Calculator</h3>
              <p className="text-gray-600 mb-6">
                Bereken uw Zakat verplichting op basis van uw bezittingen en vermogen.
              </p>
              <button className="bg-teal-600 text-white px-8 py-3 rounded-lg hover:bg-teal-700 transition-colors">
                Zakat Berekenen
              </button>
            </div>
          </div>
        )}

        {activeTab === 'sadaqah' && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <HeartIcon className="w-8 h-8 text-teal-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Sadaqah Donaties</h2>
            <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
              Sadaqah zijn vrijwillige liefdadigheidsdonaties die buiten de verplichte Zakat vallen. 
              Deze donaties helpen bij het ondersteunen van gemeenschapsprojecten en noodhulp.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
              <div className="bg-white border border-gray-200 rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Reguliere Sadaqah</h3>
                <p className="text-gray-600 mb-4">
                  Ondersteun lopende gemeenschapsprojecten en educatieve programma's.
                </p>
                <button className="w-full bg-teal-600 text-white py-3 rounded-lg hover:bg-teal-700 transition-colors">
                  Doneer Sadaqah
                </button>
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Noodhulp</h3>
                <p className="text-gray-600 mb-4">
                  Steun noodhulpprojecten voor gemeenschapsleden in moeilijke tijden.
                </p>
                <button className="w-full bg-teal-600 text-white py-3 rounded-lg hover:bg-teal-700 transition-colors">
                  Noodhulp Steunen
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
