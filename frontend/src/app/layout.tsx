import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { Providers } from './providers';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { PerformanceOptimizations } from '@/components/PerformanceOptimizations';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'VGM - Vereniging van Gentse Moskeeën',
  description: 'Enterprise-grade beheersysteem voor Gentse moskeeën',
  keywords: ['moskee', 'gent', 'islam', 'gemeenschap', 'evenementen', 'donaties'],
  authors: [{ name: 'VGM Team' }],
  robots: 'index, follow',
  openGraph: {
    title: 'VGM - Vereniging van Gentse Moskeeën',
    description: 'Enterprise-grade beheersysteem voor Gentse moskeeën',
    type: 'website',
    locale: 'nl_BE',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default async function RootLayout({
  children,
  params: { locale },
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  const messages = await getMessages();

  return (
    <html lang={locale} dir={locale === 'ar' || locale === 'ps' ? 'rtl' : 'ltr'}>
      <body className={inter.className}>
        <PerformanceOptimizations />
        <ErrorBoundary>
          <NextIntlClientProvider messages={messages}>
            <Providers>{children}</Providers>
          </NextIntlClientProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
