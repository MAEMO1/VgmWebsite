# Vercel Deployment Guide

Deze gids helpt je bij het deployen van de VGM frontend naar Vercel.

## Vereisten

1. **Vercel Account**: Maak een account aan op [vercel.com](https://vercel.com)
2. **GitHub Repository**: Zorg dat je code in een GitHub repository staat
3. **Backend API**: Zorg dat je Django backend draait en toegankelijk is

## Stap 1: Vercel Project Aanmaken

1. Ga naar [vercel.com](https://vercel.com) en log in
2. Klik op "New Project"
3. Importeer je GitHub repository
4. Selecteer de `frontend` folder als root directory

## Stap 2: Environment Variables Instellen

In je Vercel dashboard, ga naar Settings > Environment Variables en voeg de volgende variabelen toe:

### Verplichte Variabelen

```env
NEXT_PUBLIC_API_BASE_URL=https://your-backend-api.com
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your-google-maps-api-key
NEXT_PUBLIC_DEFAULT_LOCALE=nl
NEXT_PUBLIC_SUPPORTED_LOCALES=nl,en,fr,tr,ar,ps
```

### Optionele Variabelen

```env
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn
```

## Stap 3: Build Settings

Vercel detecteert automatisch Next.js, maar je kunt de volgende instellingen controleren:

- **Framework Preset**: Next.js
- **Root Directory**: `frontend`
- **Build Command**: `pnpm build`
- **Output Directory**: `.next`
- **Install Command**: `pnpm install`

## Stap 4: Custom Domain (Optioneel)

1. Ga naar Settings > Domains
2. Voeg je custom domain toe
3. Volg de DNS instructies

## Stap 5: Deployment

1. Push je code naar de `main` branch
2. Vercel zal automatisch een deployment starten
3. Bekijk de deployment status in je dashboard

## Stap 6: Preview Deployments

Elke pull request krijgt automatisch een preview deployment:
- URL: `https://your-project-git-branch.vercel.app`
- Automatisch geüpdatet bij nieuwe commits

## Stap 7: Production Deployment

1. Merge je pull request naar `main`
2. Vercel deployt automatisch naar production
3. URL: `https://your-project.vercel.app`

## Troubleshooting

### Build Errors

**Error: Module not found**
```bash
# Zorg dat alle dependencies geïnstalleerd zijn
cd frontend
pnpm install
```

**Error: Environment variables not found**
- Controleer dat alle `NEXT_PUBLIC_*` variabelen zijn ingesteld
- Zorg dat ze beginnen met `NEXT_PUBLIC_`

### Runtime Errors

**Error: API calls failing**
- Controleer `NEXT_PUBLIC_API_BASE_URL`
- Zorg dat je backend CORS correct is ingesteld
- Controleer dat je backend draait

**Error: Google Maps not loading**
- Controleer `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`
- Zorg dat de API key geldig is
- Controleer dat Maps JavaScript API is ingeschakeld

## Performance Optimalisatie

### Image Optimization
```jsx
import Image from 'next/image'

<Image
  src="/images/mosque.jpg"
  alt="Mosque"
  width={500}
  height={300}
  priority
/>
```

### Code Splitting
```jsx
import dynamic from 'next/dynamic'

const IftarMap = dynamic(() => import('@/components/ramadan/IftarMap'), {
  loading: () => <p>Loading...</p>,
  ssr: false
})
```

### Caching
```jsx
// In next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 's-maxage=60, stale-while-revalidate=300',
          },
        ],
      },
    ]
  },
}
```

## Monitoring

### Vercel Analytics
1. Ga naar Analytics in je Vercel dashboard
2. Schakel Web Analytics in
3. Bekijk performance metrics

### Error Tracking
```jsx
// In _app.tsx
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
})
```

## Security

### Headers
De `next.config.js` bevat al security headers:
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Referrer-Policy: strict-origin-when-cross-origin

### Environment Variables
- Gebruik nooit secrets in `NEXT_PUBLIC_*` variabelen
- Alle `NEXT_PUBLIC_*` variabelen zijn zichtbaar in de browser

## CI/CD

### GitHub Actions
```yaml
# .github/workflows/vercel.yml
name: Vercel
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          working-directory: ./frontend
```

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [Vercel Community](https://github.com/vercel/vercel/discussions)
