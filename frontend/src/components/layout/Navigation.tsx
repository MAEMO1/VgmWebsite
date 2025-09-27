'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useTranslations, useLocale } from 'next-intl';
import { Bars3Icon, XMarkIcon, ChevronDownIcon } from '@heroicons/react/24/outline';
import NotificationBell from '@/components/notifications/NotificationBell';

export function Navigation() {
  const [isOpen, setIsOpen] = useState(false);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  const t = useTranslations('Navigation');
  const locale = useLocale();

  const navigation = [
    { name: t('home'), href: `/${locale}` },
    { 
      name: t('mosques'), 
      href: `/${locale}/mosques`,
      dropdown: [
        { name: 'Alle Moskeeën', href: `/${locale}/mosques` },
        { name: 'Moskee Zoeken', href: `/${locale}/mosques/search` },
        { name: 'Gebedstijden', href: `/${locale}/prayer-times` },
      ]
    },
    { 
      name: t('community'), 
      href: `/${locale}/community`,
      dropdown: [
        { name: 'Evenementen', href: `/${locale}/events` },
        { name: 'Begrafenisgebeden', href: `/${locale}/janazah` },
        { name: 'Donaties', href: `/${locale}/donations` },
        { name: 'Nieuws', href: `/${locale}/news` },
      ]
    },
    { 
      name: t('about'), 
      href: `/${locale}/about`,
      dropdown: [
        { name: 'Wie zijn we', href: `/${locale}/about` },
        { name: 'Bestuur', href: `/${locale}/about/board` },
        { name: 'Memorandum', href: `/${locale}/about/memorandum` },
        { name: 'Contact', href: `/${locale}/contact` },
      ]
    },
    { name: 'Gebedstijden', href: `/${locale}/prayer-times` },
  ];

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link href={`/${locale}`} className="flex items-center space-x-3">
                <Image
                  src="/logo.svg"
                  alt="VGM Logo"
                  width={32}
                  height={32}
                />
                <div>
                  <div className="text-lg font-semibold text-gray-900">
                    VGM
                  </div>
                  <div className="text-xs text-gray-500 -mt-1">
                    Vereniging van Gentse Moskeeën
                  </div>
                </div>
              </Link>
            </div>
            <div className="hidden sm:ml-8 sm:flex sm:space-x-8">
              {navigation.map((item) => (
                <div key={item.name} className="relative">
                  {item.dropdown ? (
                    <div className="relative">
                      <button
                        onClick={() => setOpenDropdown(openDropdown === item.name ? null : item.name)}
                        className="text-gray-600 hover:text-gray-900 whitespace-nowrap py-2 px-1 border-b-2 border-transparent hover:border-gray-300 font-medium text-sm transition-colors duration-200 flex items-center"
                      >
                        {item.name}
                        <ChevronDownIcon className="ml-1 h-4 w-4" />
                      </button>
                      {openDropdown === item.name && (
                        <div className="absolute top-full left-0 mt-1 w-48 bg-white rounded-md shadow-lg border border-gray-200 py-1 z-50">
                          {item.dropdown.map((dropdownItem) => (
                            <Link
                              key={dropdownItem.name}
                              href={dropdownItem.href}
                              className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                              onClick={() => setOpenDropdown(null)}
                            >
                              {dropdownItem.name}
                            </Link>
                          ))}
                        </div>
                      )}
                    </div>
                  ) : (
                    <Link
                      href={item.href}
                      className="text-gray-600 hover:text-gray-900 whitespace-nowrap py-2 px-1 border-b-2 border-transparent hover:border-gray-300 font-medium text-sm transition-colors duration-200"
                    >
                      {item.name}
                    </Link>
                  )}
                </div>
              ))}
            </div>
          </div>
          
          <div className="hidden sm:ml-6 sm:flex sm:items-center sm:space-x-4">
            <NotificationBell />
            <Link
              href={`/${locale}/login`}
              className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium transition-colors duration-200"
            >
              Inloggen
            </Link>
            <Link
              href={`/${locale}/register`}
              className="bg-teal-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors duration-200"
            >
              Registreren
            </Link>
          </div>

          <div className="-mr-2 flex items-center sm:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="bg-white inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-gray-500"
            >
              <span className="sr-only">Open main menu</span>
              {isOpen ? (
                <XMarkIcon className="block h-6 w-6" aria-hidden="true" />
              ) : (
                <Bars3Icon className="block h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>

      {isOpen && (
        <div className="sm:hidden bg-white border-t border-gray-200">
          <div className="pt-2 pb-3 space-y-1">
            {navigation.map((item) => (
              <div key={item.name}>
                <Link
                  href={item.href}
                  className="text-gray-600 hover:text-gray-900 hover:bg-gray-50 block pl-3 pr-4 py-2 text-base font-medium transition-colors duration-200"
                  onClick={() => setIsOpen(false)}
                >
                  {item.name}
                </Link>
                {item.dropdown && (
                  <div className="pl-6 space-y-1">
                    {item.dropdown.map((dropdownItem) => (
                      <Link
                        key={dropdownItem.name}
                        href={dropdownItem.href}
                        className="text-gray-500 hover:text-gray-700 hover:bg-gray-50 block pl-3 pr-4 py-1 text-sm transition-colors duration-200"
                        onClick={() => setIsOpen(false)}
                      >
                        {dropdownItem.name}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
}
