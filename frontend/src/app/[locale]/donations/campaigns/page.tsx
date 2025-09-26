'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { CalendarIcon, CurrencyEuroIcon, UsersIcon } from '@heroicons/react/24/outline';

export default function CampaignsPage() {
  const t = useTranslations('Donations');

  const campaigns = [
    {
      id: 1,
      title: 'Moskee Renovatie Project',
      description: 'Ondersteun de renovatie van historische moskeeën in Gent. Dit project omvat het herstellen van minaretten, koepels en gebedsruimtes.',
      target: 50000,
      current: 32500,
      deadline: '2024-12-31',
      category: 'Infrastructuur',
      status: 'active',
      image: '/api/placeholder/400/200',
      updates: [
        {
          date: '2024-01-15',
          title: 'Project gestart',
          description: 'Renovatie van de eerste moskee is begonnen.'
        },
        {
          date: '2024-01-10',
          title: 'Fondsenwerving gestart',
          description: 'Campagne is officieel gelanceerd.'
        }
      ]
    },
    {
      id: 2,
      title: 'Educatie Programma',
      description: 'Financiering van islamitische educatie en Arabische lessen voor kinderen en volwassenen in de Gentse moskeeën.',
      target: 25000,
      current: 18750,
      deadline: '2024-11-30',
      category: 'Educatie',
      status: 'active',
      image: '/api/placeholder/400/200',
      updates: [
        {
          date: '2024-01-12',
          title: 'Nieuwe docenten aangesteld',
          description: 'Twee nieuwe Arabische docenten zijn toegevoegd aan het programma.'
        }
      ]
    },
    {
      id: 3,
      title: 'Gemeenschapscentrum',
      description: 'Bouw van een nieuw gemeenschapscentrum voor sociale activiteiten en evenementen.',
      target: 75000,
      current: 45000,
      deadline: '2024-10-15',
      category: 'Infrastructuur',
      status: 'active',
      image: '/api/placeholder/400/200',
      updates: []
    },
    {
      id: 4,
      title: 'Winterhulp 2024',
      description: 'Ondersteuning van kwetsbare gemeenschapsleden tijdens de wintermaanden.',
      target: 15000,
      current: 15000,
      deadline: '2024-03-31',
      category: 'Noodhulp',
      status: 'completed',
      image: '/api/placeholder/400/200',
      updates: [
        {
          date: '2024-03-31',
          title: 'Campagne voltooid',
          description: 'Doel bereikt! Alle fondsen zijn gebruikt voor winterhulp.'
        }
      ]
    }
  ];

  const categories = ['Alle', 'Infrastructuur', 'Educatie', 'Noodhulp'];
  const [selectedCategory, setSelectedCategory] = useState('Alle');

  const filteredCampaigns = selectedCategory === 'Alle' 
    ? campaigns 
    : campaigns.filter(campaign => campaign.category === selectedCategory);

  return (
    <div className="min-h-screen bg-white">
      <Breadcrumbs items={[
        { name: 'Donaties', href: '/donations' },
        { name: 'Campagnes' }
      ]} />

      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Fondsenwervingscampagnes
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Ondersteun specifieke projecten en initiatieven die de moskeegemeenschap in Gent ten goede komen
          </p>
        </div>

        {/* Category Filter */}
        <div className="mb-8">
          <div className="flex flex-wrap justify-center gap-4">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                  selectedCategory === category
                    ? 'bg-teal-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {/* Campaigns Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredCampaigns.map((campaign) => {
            const progress = (campaign.current / campaign.target) * 100;
            const isCompleted = campaign.status === 'completed';
            const daysLeft = Math.ceil((new Date(campaign.deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
            
            return (
              <div key={campaign.id} className="bg-white border border-gray-200 rounded-2xl overflow-hidden hover:shadow-lg transition-shadow">
                {/* Campaign Image */}
                <div className="h-48 bg-gray-200 flex items-center justify-center relative">
                  <span className="text-gray-500">Campagne Afbeelding</span>
                  {isCompleted && (
                    <div className="absolute top-4 right-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                      Voltooid
                    </div>
                  )}
                  {campaign.status === 'active' && daysLeft > 0 && (
                    <div className="absolute top-4 right-4 bg-teal-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                      {daysLeft} dagen
                    </div>
                  )}
                </div>

                <div className="p-6">
                  {/* Category */}
                  <div className="mb-3">
                    <span className="inline-block bg-teal-100 text-teal-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                      {campaign.category}
                    </span>
                  </div>

                  {/* Title and Description */}
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{campaign.title}</h3>
                  <p className="text-gray-600 mb-4 line-clamp-3">{campaign.description}</p>
                  
                  {/* Progress */}
                  <div className="mb-4">
                    <div className="flex justify-between text-sm text-gray-600 mb-2">
                      <span>€{campaign.current.toLocaleString()}</span>
                      <span>€{campaign.target.toLocaleString()}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full transition-all duration-300 ${
                          isCompleted ? 'bg-green-500' : 'bg-teal-600'
                        }`}
                        style={{ width: `${Math.min(progress, 100)}%` }}
                      ></div>
                    </div>
                    <div className="text-right text-sm text-gray-500 mt-1">
                      {progress.toFixed(1)}% voltooid
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                    <div className="flex items-center">
                      <CalendarIcon className="w-4 h-4 mr-1" />
                      <span>Deadline: {new Date(campaign.deadline).toLocaleDateString('nl-NL')}</span>
                    </div>
                    <div className="flex items-center">
                      <CurrencyEuroIcon className="w-4 h-4 mr-1" />
                      <span>€{campaign.target.toLocaleString()}</span>
                    </div>
                  </div>

                  {/* Action Button */}
                  <button 
                    className={`w-full py-3 rounded-lg font-medium transition-colors ${
                      isCompleted 
                        ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                        : 'bg-teal-600 text-white hover:bg-teal-700'
                    }`}
                    disabled={isCompleted}
                  >
                    {isCompleted ? 'Campagne Voltooid' : 'Steun Campagne'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Empty State */}
        {filteredCampaigns.length === 0 && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CurrencyEuroIcon className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Geen campagnes gevonden</h3>
            <p className="text-gray-500">
              Er zijn momenteel geen campagnes in de geselecteerde categorie.
            </p>
          </div>
        )}

        {/* Call to Action */}
        <div className="mt-16 text-center">
          <div className="bg-teal-50 rounded-2xl p-8 max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Heeft u een idee voor een nieuwe campagne?
            </h2>
            <p className="text-gray-600 mb-6">
              VGM ondersteunt initiatieven die de moskeegemeenschap ten goede komen. 
              Neem contact met ons op om uw idee te bespreken.
            </p>
            <button className="bg-teal-600 text-white px-8 py-3 rounded-lg hover:bg-teal-700 transition-colors">
              Nieuwe Campagne Voorstellen
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
