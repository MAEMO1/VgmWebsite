import { notFound } from 'next/navigation';
import { getRequestConfig } from 'next-intl/server';

// Can be imported from a shared config
const locales = ['nl', 'en', 'fr', 'tr', 'ar', 'ps'];

export default getRequestConfig(async ({ requestLocale }) => {
  // Validate that the incoming `locale` parameter is valid
  if (!requestLocale || !locales.includes(requestLocale as any)) notFound();

  return {
    messages: (await import(`../messages/${requestLocale}.json`)).default,
    timeZone: 'Europe/Brussels',
  };
});
