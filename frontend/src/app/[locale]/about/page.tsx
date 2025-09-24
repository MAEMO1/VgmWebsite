'use client';

import { useTranslations } from 'next-intl';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { UsersIcon, BuildingOfficeIcon, HeartIcon, AcademicCapIcon } from '@heroicons/react/24/outline';

export default function AboutPage() {
  const t = useTranslations('About');

  const stats = [
    { number: '21', label: 'Moskeeën', description: 'Aangesloten bij VGM' },
    { number: '2016', label: 'Opgericht', description: 'Sinds 2016 actief' },
    { number: '1', label: 'Koepel', description: 'Overkoepelende organisatie' }
  ];

  const pillars = [
    {
      icon: BuildingOfficeIcon,
      title: 'Belangenbehartiging',
      description: 'We behartigen de belangen van alle moskeeën in Gent en zorgen voor een sterke stem in de samenleving.'
    },
    {
      icon: UsersIcon,
      title: 'Samenwerking',
      description: 'We stimuleren samenwerking tussen moskeeën en organiseren gezamenlijke activiteiten en evenementen.'
    },
    {
      icon: HeartIcon,
      title: 'Gemeenschapsopbouw',
      description: 'We werken aan een sterke, verenigde moslimgemeenschap in Gent door educatie en sociale programma&apos;s.'
    }
  ];

  const boardMembers = [
    { name: 'Ahmed Al-Rashid', position: 'Voorzitter', status: 'Actief' },
    { name: 'Fatima Hassan', position: 'Secretaris', status: 'Actief' },
    { name: 'Mohammed Ali', position: 'Penningmeester', status: 'Actief' },
    { name: 'Aisha Ibrahim', position: 'Lid', status: 'Actief' },
    { name: 'Omar Khalil', position: 'Lid', status: 'Actief' }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Breadcrumbs items={[
        { name: 'Over Ons' }
      ]} />
      
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900 mb-6">
            Wie zijn we
          </h1>
          <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
            De Vereniging van Gentse Moskeeën (VGM) is een overkoepelende organisatie die 21 moskeeën in Gent verenigt. 
            We werken samen aan een sterke, verenigde moslimgemeenschap en behartigen de belangen van onze leden.
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-4xl font-bold text-blue-600 mb-2">{stat.number}</div>
              <div className="text-xl font-semibold text-gray-900 mb-1">{stat.label}</div>
              <div className="text-gray-600">{stat.description}</div>
            </div>
          ))}
        </div>

        {/* Mission Pillars */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            Onze Drie Pilaren
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {pillars.map((pillar, index) => (
              <div key={index} className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <pillar.icon className="h-8 w-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">{pillar.title}</h3>
                <p className="text-gray-600 leading-relaxed">{pillar.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Board Members */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            Bestuur 2022-2026
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {boardMembers.map((member, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-lg p-6 text-center">
                <div className="w-20 h-20 bg-gray-200 rounded-full mx-auto mb-4"></div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{member.name}</h3>
                <p className="text-blue-600 font-medium mb-2">{member.position}</p>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  {member.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Memorandum Section */}
        <div className="bg-gray-50 rounded-lg p-8 mb-16">
          <div className="text-center">
            <AcademicCapIcon className="h-12 w-12 text-blue-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Memorandum 2025-2030
            </h2>
            <p className="text-gray-600 mb-6 max-w-3xl mx-auto">
              Ons memorandum bevat onze visie en plannen voor de komende jaren. 
              Het document behandelt belangrijke thema&apos;s zoals religieuze dienst, onderwijs, 
              armoedebestrijding, huisvesting, werk en politie.
            </p>
            <button className="bg-blue-600 text-white px-8 py-3 rounded-md hover:bg-blue-700 transition-colors">
              Download PDF
            </button>
          </div>
        </div>

        {/* Contact CTA */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Neem Contact Op
          </h2>
          <p className="text-gray-600 mb-6">
            Heeft u vragen of wilt u meer informatie over de VGM? Neem gerust contact met ons op.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-gray-900 text-white px-8 py-3 rounded-md hover:bg-gray-800 transition-colors">
              Contact Pagina
            </button>
            <button className="border border-gray-300 text-gray-700 px-8 py-3 rounded-md hover:bg-gray-50 transition-colors">
              E-mail Sturen
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
