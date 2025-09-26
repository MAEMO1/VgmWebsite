'use client';

import { useTranslations } from 'next-intl';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { 
  UserIcon, 
  EnvelopeIcon, 
  PhoneIcon,
  AcademicCapIcon,
  BriefcaseIcon
} from '@heroicons/react/24/outline';

interface BoardMember {
  id: number;
  name: string;
  position: string;
  role: string;
  email?: string;
  phone?: string;
  bio: string;
  experience: string[];
  image?: string;
  term: string;
}

export default function BoardPage() {
  const t = useTranslations('Board');

  const boardMembers: BoardMember[] = [
    {
      id: 1,
      name: 'Dr. Ahmed Al-Rashid',
      position: 'Voorzitter',
      role: 'Voorzitter van de VGM',
      email: 'voorzitter@vgm-gent.be',
      phone: '+32 9 123 45 67',
      bio: 'Dr. Ahmed Al-Rashid is al meer dan 15 jaar actief in de moskeegemeenschap van Gent. Hij heeft een doctoraat in Islamitische Studies en is gespecialiseerd in interreligieuze dialoog.',
      experience: [
        'Doctoraat in Islamitische Studies (KU Leuven)',
        '15+ jaar ervaring in moskeebestuur',
        'Expert in interreligieuze dialoog',
        'Actief in gemeenschapsontwikkeling'
      ],
      term: '2023-2026'
    },
    {
      id: 2,
      name: 'Fatima Hassan',
      position: 'Vice-Voorzitter',
      role: 'Vice-Voorzitter en Vrouwenvertegenwoordiger',
      email: 'vice-voorzitter@vgm-gent.be',
      phone: '+32 9 234 56 78',
      bio: 'Fatima Hassan is een ervaren bestuurder met een achtergrond in sociale wetenschappen. Ze zet zich in voor vrouwenrechten en jeugdontwikkeling binnen de moskeegemeenschap.',
      experience: [
        'Master in Sociale Wetenschappen (UGent)',
        '10+ jaar ervaring in NGO-bestuur',
        'Specialist in vrouwen- en jeugdprogramma\'s',
        'Actief in sociale cohesie projecten'
      ],
      term: '2023-2026'
    },
    {
      id: 3,
      name: 'Sheikh Ibrahim Al-Turk',
      position: 'Religieuze Adviseur',
      role: 'Hoofdimam en Religieuze Adviseur',
      email: 'imam@vgm-gent.be',
      phone: '+32 9 345 67 89',
      bio: 'Sheikh Ibrahim Al-Turk is de hoofdimam van Moskee Al-Fath en dient als religieuze adviseur voor de VGM. Hij heeft uitgebreide kennis van islamitische jurisprudentie en moderne uitdagingen.',
      experience: [
        'Graduaat in Islamitische Wetenschappen (Al-Azhar)',
        '20+ jaar ervaring als imam',
        'Expert in islamitische jurisprudentie',
        'Actief in religieuze educatie'
      ],
      term: '2023-2026'
    },
    {
      id: 4,
      name: 'Mohammed Benali',
      position: 'Secretaris',
      role: 'Secretaris en Communicatieverantwoordelijke',
      email: 'secretaris@vgm-gent.be',
      phone: '+32 9 456 78 90',
      bio: 'Mohammed Benali is verantwoordelijk voor de dagelijkse administratie en communicatie van de VGM. Hij heeft een achtergrond in bedrijfskunde en is gespecialiseerd in projectmanagement.',
      experience: [
        'Master in Bedrijfskunde (UGent)',
        '8+ jaar ervaring in projectmanagement',
        'Expert in communicatie en PR',
        'Actief in digitale transformatie'
      ],
      term: '2023-2026'
    },
    {
      id: 5,
      name: 'Aisha Mahmoud',
      position: 'Penningmeester',
      role: 'Penningmeester en Financieel Verantwoordelijke',
      email: 'penningmeester@vgm-gent.be',
      phone: '+32 9 567 89 01',
      bio: 'Aisha Mahmoud is verantwoordelijk voor de financiële zaken van de VGM. Ze heeft een achtergrond in accountancy en is gespecialiseerd in non-profit financiële management.',
      experience: [
        'Bachelor in Accountancy (Hogeschool Gent)',
        '12+ jaar ervaring in financiële management',
        'Expert in non-profit financiën',
        'Actief in fondsenwerving'
      ],
      term: '2023-2026'
    },
    {
      id: 6,
      name: 'Yusuf Özkan',
      position: 'Jeugdvertegenwoordiger',
      role: 'Jeugdvertegenwoordiger en Evenementencoördinator',
      email: 'jeugd@vgm-gent.be',
      phone: '+32 9 678 90 12',
      bio: 'Yusuf Özkan vertegenwoordigt de jongeren binnen de VGM en coördineert jeugdactiviteiten en evenementen. Hij heeft een achtergrond in pedagogiek en is gepassioneerd over jeugdontwikkeling.',
      experience: [
        'Bachelor in Pedagogiek (Hogeschool Gent)',
        '5+ jaar ervaring in jeugdwerk',
        'Expert in evenementenorganisatie',
        'Actief in mentorschap en begeleiding'
      ],
      term: '2023-2026'
    }
  ];

  const committees = [
    {
      name: 'Religieuze Commissie',
      description: 'Verantwoordelijk voor religieuze zaken, gebedstijden en religieuze educatie',
      members: ['Sheikh Ibrahim Al-Turk', 'Dr. Ahmed Al-Rashid'],
      chair: 'Sheikh Ibrahim Al-Turk'
    },
    {
      name: 'Educatie Commissie',
      description: 'Organiseert educatieve programma\'s, lessen en workshops',
      members: ['Fatima Hassan', 'Yusuf Özkan', 'Aisha Mahmoud'],
      chair: 'Fatima Hassan'
    },
    {
      name: 'Evenementen Commissie',
      description: 'Plant en organiseert gemeenschapsevenementen en activiteiten',
      members: ['Yusuf Özkan', 'Mohammed Benali', 'Dr. Ahmed Al-Rashid'],
      chair: 'Yusuf Özkan'
    },
    {
      name: 'Financiële Commissie',
      description: 'Beheert financiën, donaties en fondsenwerving',
      members: ['Aisha Mahmoud', 'Mohammed Benali', 'Fatima Hassan'],
      chair: 'Aisha Mahmoud'
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Breadcrumbs items={[
        { name: 'Over Ons', href: '/about' },
        { name: 'Bestuur' }
      ]} />

      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            VGM Bestuur
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Ontmoet de bestuursleden en commissies die de Vereniging van Gentse Moskeeën leiden
          </p>
        </div>

        {/* Board Members */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">
            Bestuursleden
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {boardMembers.map((member) => (
              <div key={member.id} className="bg-white border border-gray-200 rounded-2xl p-6 hover:shadow-lg transition-shadow">
                {/* Profile Image */}
                <div className="text-center mb-6">
                  <div className="w-24 h-24 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <UserIcon className="w-12 h-12 text-teal-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900">{member.name}</h3>
                  <p className="text-teal-600 font-medium">{member.position}</p>
                  <p className="text-sm text-gray-500">Termijn: {member.term}</p>
                </div>

                {/* Contact Info */}
                <div className="space-y-2 mb-4">
                  {member.email && (
                    <div className="flex items-center text-sm text-gray-600">
                      <EnvelopeIcon className="w-4 h-4 mr-2" />
                      <a href={`mailto:${member.email}`} className="hover:text-teal-600">
                        {member.email}
                      </a>
                    </div>
                  )}
                  {member.phone && (
                    <div className="flex items-center text-sm text-gray-600">
                      <PhoneIcon className="w-4 h-4 mr-2" />
                      <a href={`tel:${member.phone}`} className="hover:text-teal-600">
                        {member.phone}
                      </a>
                    </div>
                  )}
                </div>

                {/* Bio */}
                <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                  {member.bio}
                </p>

                {/* Experience */}
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Ervaring</h4>
                  <ul className="space-y-1">
                    {member.experience.slice(0, 2).map((exp, index) => (
                      <li key={index} className="text-xs text-gray-600 flex items-start">
                        <div className="w-1.5 h-1.5 bg-teal-500 rounded-full mr-2 mt-1.5 flex-shrink-0"></div>
                        {exp}
                      </li>
                    ))}
                    {member.experience.length > 2 && (
                      <li className="text-xs text-gray-500">
                        +{member.experience.length - 2} meer...
                      </li>
                    )}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Committees */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">
            Commissies
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {committees.map((committee, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-2xl p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-start mb-4">
                  <div className="w-12 h-12 bg-teal-100 rounded-xl flex items-center justify-center mr-4">
                    <BriefcaseIcon className="w-6 h-6 text-teal-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{committee.name}</h3>
                    <p className="text-sm text-gray-600">Voorzitter: {committee.chair}</p>
                  </div>
                </div>
                
                <p className="text-gray-600 text-sm mb-4">
                  {committee.description}
                </p>
                
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Leden</h4>
                  <div className="flex flex-wrap gap-2">
                    {committee.members.map((member, memberIndex) => (
                      <span key={memberIndex} className="bg-teal-100 text-teal-800 text-xs px-2 py-1 rounded-full">
                        {member}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Contact Information */}
        <div className="bg-teal-50 rounded-2xl p-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Contact met het Bestuur
            </h2>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              Heeft u vragen, suggesties of wilt u contact opnemen met het bestuur? 
              We staan open voor feedback en zijn bereikbaar voor alle leden van de gemeenschap.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="mailto:bestuur@vgm-gent.be"
                className="inline-flex items-center px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
              >
                <EnvelopeIcon className="w-5 h-5 mr-2" />
                E-mail Bestuur
              </a>
              <a
                href="/contact"
                className="inline-flex items-center px-6 py-3 bg-white text-teal-600 border-2 border-teal-600 rounded-lg hover:bg-teal-50 transition-colors"
              >
                Contact Formulier
              </a>
            </div>
          </div>
        </div>

        {/* Board Meeting Information */}
        <div className="mt-12 bg-white border border-gray-200 rounded-2xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Bestuursvergaderingen
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Reguliere Vergaderingen</h3>
              <ul className="space-y-2 text-gray-600">
                <li>• Maandelijks op de eerste donderdag van de maand</li>
                <li>• Tijd: 19:00 - 21:00</li>
                <li>• Locatie: VGM Hoofdkantoor</li>
                <li>• Open voor alle VGM-leden</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Agenda Items</h3>
              <ul className="space-y-2 text-gray-600">
                <li>• Financiële rapportage</li>
                <li>• Evenementen planning</li>
                <li>• Gemeenschapszaken</li>
                <li>• Nieuwe initiatieven</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
