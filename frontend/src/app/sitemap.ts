import { MetadataRoute } from 'next';

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://vgm-gent.be';
  const locales = ['nl', 'ar', 'en'];
  
  const staticRoutes = [
    '',
    '/mosques',
    '/mosques/search',
    '/mosques/register',
    '/events',
    '/events/register',
    '/news',
    '/donations',
    '/prayer-times',
    '/ramadan',
    '/janazah',
    '/admin',
    '/notifications'
  ];

  const sitemap: MetadataRoute.Sitemap = [];

  // Add static routes for all locales
  staticRoutes.forEach(route => {
    locales.forEach(locale => {
      sitemap.push({
        url: `${baseUrl}/${locale}${route}`,
        lastModified: new Date(),
        changeFrequency: route === '' ? 'daily' : 'weekly',
        priority: route === '' ? 1 : 0.8
      });
    });
  });

  // Add dynamic mosque routes (example)
  // In production, this would fetch from the database
  const mosqueIds = [1, 2, 3, 4, 5]; // Example mosque IDs
  
  mosqueIds.forEach(mosqueId => {
    locales.forEach(locale => {
      sitemap.push({
        url: `${baseUrl}/${locale}/mosques/${mosqueId}`,
        lastModified: new Date(),
        changeFrequency: 'weekly',
        priority: 0.7
      });
    });
  });

  return sitemap;
}
