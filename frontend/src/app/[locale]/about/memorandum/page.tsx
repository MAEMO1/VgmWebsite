'use client';

import { useTranslations } from 'next-intl';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { 
  DocumentTextIcon, 
  CheckCircleIcon,
  ScaleIcon,
  HeartIcon,
  UsersIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';

export default function MemorandumPage() {
  const t = useTranslations('Memorandum');

  const principles = [
    {
      title: 'Eenheid in Diversiteit',
      description: 'We erkennen en waarderen de diversiteit binnen de moskeegemeenschap en streven naar eenheid in onze gemeenschappelijke doelen.',
      icon: UsersIcon
    },
    {
      title: 'Transparantie en Integriteit',
      description: 'We handelen met volledige transparantie en integriteit in al onze activiteiten en besluitvorming.',
      icon: ScaleIcon
    },
    {
      title: 'Gemeenschapsdienst',
      description: 'We zijn toegewijd aan het dienen van de moskeegemeenschap en de bredere samenleving.',
      icon: HeartIcon
    },
    {
      title: 'Interreligieuze Dialoog',
      description: 'We bevorderen respectvolle dialoog en samenwerking met andere religieuze gemeenschappen.',
      icon: GlobeAltIcon
    }
  ];

  const objectives = [
    {
      category: 'Religieuze Diensten',
      items: [
        'Organiseren van gezamenlijke religieuze evenementen',
        'Coördinatie van gebedstijden en religieuze kalenders',
        'Ondersteuning van religieuze educatie en training',
        'Faciliteren van bedevaarten en religieuze reizen'
      ]
    },
    {
      category: 'Gemeenschapsontwikkeling',
      items: [
        'Bevorderen van sociale cohesie binnen de moskeegemeenschap',
        'Organiseren van culturele en educatieve evenementen',
        'Ondersteuning van jeugdprogramma\'s en activiteiten',
        'Faciliteren van vrouwen- en gezinsprogramma\'s'
      ]
    },
    {
      category: 'Maatschappelijke Betrokkenheid',
      items: [
        'Deelnemen aan interreligieuze dialoog en samenwerking',
        'Bijdragen aan maatschappelijke projecten en initiatieven',
        'Ondersteuning van humanitaire en liefdadigheidsactiviteiten',
        'Bevorderen van burgerparticipatie en integratie'
      ]
    },
    {
      category: 'Bestuur en Beheer',
      items: [
        'Transparant en democratisch bestuur van de vereniging',
        'Efficiënt beheer van middelen en financiën',
        'Ondersteuning van individuele moskeeën in hun ontwikkeling',
        'Faciliteren van netwerken en samenwerking tussen moskeeën'
      ]
    }
  ];

  const values = [
    {
      value: 'Respect',
      description: 'We tonen respect voor alle leden van de gemeenschap, ongeacht hun achtergrond, leeftijd of status.'
    },
    {
      value: 'Gerechtigheid',
      description: 'We streven naar eerlijke en rechtvaardige behandeling van alle leden en zaken.'
    },
    {
      value: 'Mededogen',
      description: 'We tonen mededogen en ondersteuning voor degenen die hulp nodig hebben.'
    },
    {
      value: 'Excellence',
      description: 'We streven naar uitmuntendheid in al onze activiteiten en diensten.'
    },
    {
      value: 'Samenwerking',
      description: 'We geloven in de kracht van samenwerking en teamwork.'
    },
    {
      value: 'Innovatie',
      description: 'We omarmen innovatie en moderne benaderingen om onze doelen te bereiken.'
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Breadcrumbs items={[
        { name: 'Over Ons', href: '/about' },
        { name: 'Memorandum' }
      ]} />

      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <DocumentTextIcon className="w-8 h-8 text-teal-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            VGM Memorandum
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Onze missie, visie, waarden en doelstellingen als Vereniging van Gentse Moskeeën
          </p>
        </div>

        {/* Mission Statement */}
        <div className="bg-teal-50 rounded-2xl p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Onze Missie</h2>
          <p className="text-lg text-gray-700 leading-relaxed">
            De Vereniging van Gentse Moskeeën (VGM) streeft ernaar om de moskeegemeenschap in Gent te verenigen, 
            te ondersteunen en te versterken door middel van samenwerking, educatie en gemeenschapsdienst. 
            We zijn toegewijd aan het bevorderen van islamitische waarden, het ondersteunen van religieuze 
            en educatieve activiteiten, en het bijdragen aan de sociale cohesie en integratie van de moslimgemeenschap 
            in de Gentse samenleving.
          </p>
        </div>

        {/* Vision Statement */}
        <div className="bg-white border border-gray-200 rounded-2xl p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Onze Visie</h2>
          <p className="text-lg text-gray-700 leading-relaxed">
            We streven naar een verenigde, sterke en welvarende moskeegemeenschap in Gent die:
          </p>
          <ul className="mt-4 space-y-3">
            <li className="flex items-start">
              <CheckCircleIcon className="w-6 h-6 text-teal-600 mr-3 mt-0.5" />
              <span className="text-gray-700">Actief bijdraagt aan de sociale en culturele ontwikkeling van Gent</span>
            </li>
            <li className="flex items-start">
              <CheckCircleIcon className="w-6 h-6 text-teal-600 mr-3 mt-0.5" />
              <span className="text-gray-700">Een brug vormt tussen verschillende culturen en religies</span>
            </li>
            <li className="flex items-start">
              <CheckCircleIcon className="w-6 h-6 text-teal-600 mr-3 mt-0.5" />
              <span className="text-gray-700">Kwalitatieve religieuze en educatieve diensten biedt</span>
            </li>
            <li className="flex items-start">
              <CheckCircleIcon className="w-6 h-6 text-teal-600 mr-3 mt-0.5" />
              <span className="text-gray-700">Een voorbeeld is van goed bestuur en transparantie</span>
            </li>
          </ul>
        </div>

        {/* Core Principles */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Kernprincipes</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {principles.map((principle, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-2xl p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-start">
                  <div className="w-12 h-12 bg-teal-100 rounded-xl flex items-center justify-center mr-4">
                    <principle.icon className="w-6 h-6 text-teal-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{principle.title}</h3>
                    <p className="text-gray-600">{principle.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Values */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Onze Waarden</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {values.map((value, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-2xl p-6 hover:shadow-lg transition-shadow">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{value.value}</h3>
                <p className="text-gray-600 text-sm">{value.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Objectives */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Onze Doelstellingen</h2>
          <div className="space-y-8">
            {objectives.map((objective, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-2xl p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">{objective.category}</h3>
                <ul className="space-y-3">
                  {objective.items.map((item, itemIndex) => (
                    <li key={itemIndex} className="flex items-start">
                      <CheckCircleIcon className="w-5 h-5 text-teal-600 mr-3 mt-0.5" />
                      <span className="text-gray-700">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Governance Principles */}
        <div className="bg-gray-50 rounded-2xl p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Bestuursprincipes</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Democratisch Bestuur</h3>
              <ul className="space-y-2 text-gray-700">
                <li>• Transparante besluitvorming</li>
                <li>• Regelmatige verkiezingen</li>
                <li>• Inclusieve participatie</li>
                <li>• Verantwoording aan leden</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Financieel Beheer</h3>
              <ul className="space-y-2 text-gray-700">
                <li>• Transparante financiële rapportage</li>
                <li>• Onafhankelijke audits</li>
                <li>• Efficiënt gebruik van middelen</li>
                <li>• Duurzame financiële planning</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Commitment Statement */}
        <div className="bg-teal-600 text-white rounded-2xl p-8 text-center">
          <h2 className="text-2xl font-bold mb-4">Onze Toewijding</h2>
          <p className="text-lg leading-relaxed">
            Als Vereniging van Gentse Moskeeën verbinden we ons ertoe om deze principes, waarden en doelstellingen 
            na te leven in al onze activiteiten en besluitvorming. We streven ernaar om een voorbeeld te zijn van 
            goed bestuur, gemeenschapsdienst en interreligieuze samenwerking in de stad Gent.
          </p>
          <div className="mt-6">
            <p className="text-sm opacity-90">
              Dit memorandum is goedgekeurd door het VGM-bestuur op 15 januari 2024
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
