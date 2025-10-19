'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useLocale } from 'next-intl';
import { MapPinIcon, EnvelopeIcon } from '@heroicons/react/24/outline';

export function Footer() {
  const locale = useLocale();

  return (
    <footer className="bg-gray-800 text-white">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* VGM Information */}
          <div className="md:col-span-1">
            <div className="flex items-center mb-4">
              <Image
                src="/logo-transparent.png"
                alt="VGM Logo"
                width={40}
                height={40}
                className="mr-3"
              />
              <span className="text-xl font-bold">VGM</span>
            </div>
            <p className="text-gray-300 mb-6 leading-relaxed">
              Welkom bij de Vereniging van Gentse Moskeeën - uw centrale platform voor moskee-informatie, evenementen en gemeenschapsdiensten.
            </p>
            <div className="space-y-2 text-gray-300">
              <div className="flex items-center">
                <MapPinIcon className="w-4 h-4 mr-2" />
                <span>Gent, België</span>
              </div>
              <div className="flex items-center">
                <EnvelopeIcon className="w-4 h-4 mr-2" />
                <span>info@vgmgent.be</span>
              </div>
            </div>
          </div>

          {/* VGM & Moskeeën Links */}
          <div className="md:col-span-1">
            <div className="grid grid-cols-2 gap-8">
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
                      Moskee Registreren
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
                      Registratieproces
                    </Link>
                  </li>
                  <li>
                    <Link href={`/${locale}/janazah`} className="text-gray-300 hover:text-white transition-colors">
                      Begrafenisgebeden
                    </Link>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          {/* Gemeenschap Links */}
          <div className="md:col-span-1">
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
