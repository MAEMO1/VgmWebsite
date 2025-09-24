'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useLocale } from 'next-intl';

export function Footer() {
  const locale = useLocale();

  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Logo and Description */}
          <div className="md:col-span-1">
            <div className="flex items-center mb-4">
              <Image
                src="/logo.svg"
                alt="VGM Logo"
                width={40}
                height={40}
                className="mr-3"
              />
              <span className="text-xl font-bold">VGM</span>
            </div>
            <p className="text-gray-300 mb-4">
              De koepelorganisatie voor de Gentse moskeegemeenschap, die samenwerking en gemeenschapsontwikkeling bevordert.
            </p>
            <div className="text-gray-300 text-sm">
              <p>Gent, België</p>
              <p>info@vgm-gent.be</p>
            </div>
          </div>

          {/* VGM Links */}
          <div>
            <h3 className="text-lg font-semibold mb-4">VGM</h3>
            <ul className="space-y-2">
              <li>
                <Link href={`/${locale}/about`} className="text-gray-300 hover:text-white transition-colors">
                  Over Ons
                </Link>
              </li>
              <li>
                <Link href={`/${locale}/news`} className="text-gray-300 hover:text-white transition-colors">
                  Nieuws
                </Link>
              </li>
              <li>
                <Link href={`/${locale}/contact`} className="text-gray-300 hover:text-white transition-colors">
                  Contact
                </Link>
              </li>
              <li>
                <Link href={`/${locale}/mosques/register`} className="text-gray-300 hover:text-white transition-colors">
                  Moskee Registratie
                </Link>
              </li>
            </ul>
          </div>

          {/* Moskeeën Links */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Moskeeën</h3>
            <ul className="space-y-2">
              <li>
                <Link href={`/${locale}/mosques`} className="text-gray-300 hover:text-white transition-colors">
                  Alle Moskeeën
                </Link>
              </li>
              <li>
                <Link href={`/${locale}/mosques/register`} className="text-gray-300 hover:text-white transition-colors">
                  Registratie Proces
                </Link>
              </li>
              <li>
                <Link href={`/${locale}/janazah`} className="text-gray-300 hover:text-white transition-colors">
                  Begrafenisgebeden
                </Link>
              </li>
            </ul>
          </div>

          {/* Gemeenschap Links */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Gemeenschap</h3>
            <ul className="space-y-2">
              <li>
                <Link href={`/${locale}/events`} className="text-gray-300 hover:text-white transition-colors">
                  Evenementen
                </Link>
              </li>
              <li>
                <Link href={`/${locale}/donations`} className="text-gray-300 hover:text-white transition-colors">
                  Donatie Campagnes
                </Link>
              </li>
              <li>
                <Link href={`/${locale}/login`} className="text-gray-300 hover:text-white transition-colors">
                  Inloggen
                </Link>
              </li>
              <li>
                <Link href={`/${locale}/register`} className="text-gray-300 hover:text-white transition-colors">
                  Registreren
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="border-t border-gray-700 mt-12 pt-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <h4 className="text-lg font-semibold mb-2">Evenementen</h4>
              <p className="text-gray-300 mb-4">
                Ontdek gemeenschapsevenementen, educatieve workshops en culturele bijeenkomsten in de Gentse moskeeën.
              </p>
              <Link
                href={`/${locale}/events`}
                className="inline-flex items-center text-teal-400 hover:text-teal-300 transition-colors"
              >
                Bekijk Evenementen →
              </Link>
            </div>
            <div className="text-center">
              <h4 className="text-lg font-semibold mb-2">Begrafenisgebeden</h4>
              <p className="text-gray-300 mb-4">
                Meld begrafenisgebeden aan bij moskeeën in Gent voor gemeenschapsondersteuning tijdens rouwperiodes.
              </p>
              <Link
                href={`/${locale}/janazah`}
                className="inline-flex items-center text-teal-400 hover:text-teal-300 transition-colors"
              >
                Meld Gebed →
              </Link>
            </div>
            <div className="text-center">
              <h4 className="text-lg font-semibold mb-2">Donaties</h4>
              <p className="text-gray-300 mb-4">
                Steun VGM en lokale moskeeprojecten door donaties voor gemeenschapsontwikkeling en religieuze diensten.
              </p>
              <Link
                href={`/${locale}/donations`}
                className="inline-flex items-center text-teal-400 hover:text-teal-300 transition-colors"
              >
                Doneer Nu →
              </Link>
            </div>
          </div>
        </div>

        {/* Copyright */}
        <div className="border-t border-gray-700 mt-8 pt-8 text-center">
          <p className="text-gray-400">
            © 2025 Vereniging van Gentse Moskeeën. Alle rechten voorbehouden.
          </p>
        </div>
      </div>
    </footer>
  );
}