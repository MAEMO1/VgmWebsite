'use client';

import Link from 'next/link';
import { useTranslations, useLocale } from 'next-intl';

export function Footer() {
  const t = useTranslations('Footer');
  const locale = useLocale();

  return (
    <footer className="bg-gray-50 border-t border-gray-200">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-2">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {t('about.title')}
            </h3>
            <p className="text-gray-600 mb-4">
              {t('about.description')}
            </p>
            <div className="flex space-x-4">
              <Link
                href={`/${locale}/privacy`}
                className="text-gray-500 hover:text-gray-700 text-sm"
              >
                {t('links.privacy')}
              </Link>
              <Link
                href={`/${locale}/terms`}
                className="text-gray-500 hover:text-gray-700 text-sm"
              >
                {t('links.terms')}
              </Link>
              <Link
                href={`/${locale}/contact`}
                className="text-gray-500 hover:text-gray-700 text-sm"
              >
                {t('links.contact')}
              </Link>
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {t('quickLinks.title')}
            </h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href={`/${locale}/mosques`}
                  className="text-gray-500 hover:text-gray-700 text-sm"
                >
                  {t('quickLinks.mosques')}
                </Link>
              </li>
              <li>
                <Link
                  href={`/${locale}/events`}
                  className="text-gray-500 hover:text-gray-700 text-sm"
                >
                  {t('quickLinks.events')}
                </Link>
              </li>
              <li>
                <Link
                  href={`/${locale}/ramadan`}
                  className="text-gray-500 hover:text-gray-700 text-sm"
                >
                  {t('quickLinks.ramadan')}
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {t('contact.title')}
            </h3>
            <div className="space-y-2 text-sm text-gray-600">
              <p>{t('contact.address')}</p>
              <p>{t('contact.phone')}</p>
              <p>{t('contact.email')}</p>
            </div>
          </div>
        </div>
        
        <div className="mt-8 pt-8 border-t border-gray-200">
          <p className="text-center text-sm text-gray-500">
            © {new Date().getFullYear()} VGM - Vereniging van Gentse Moskeeën. {t('rights')}
          </p>
        </div>
      </div>
    </footer>
  );
}
