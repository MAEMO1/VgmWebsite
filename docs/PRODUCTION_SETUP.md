# VGM Production Setup Guide

Complete gids voor het opzetten van de VGM website in productie.

## Stap 1: Vercel Project Aanmaken

### 1.1 Vercel Account
1. Ga naar [vercel.com](https://vercel.com)
2. Klik op "Sign Up" en maak een account aan
3. Verifieer je e-mailadres

### 1.2 GitHub Repository
1. Zorg dat je code in een GitHub repository staat
2. Repository moet publiek zijn of je moet Vercel toegang geven

### 1.3 Project Import
1. In Vercel dashboard, klik op "New Project"
2. Selecteer "Import Git Repository"
3. Kies je VGM repository
4. Configureer het project:
   - **Project Name**: `vgm-website`
   - **Framework Preset**: `Next.js`
   - **Root Directory**: `frontend`
   - **Build Command**: `pnpm build`
   - **Output Directory**: `.next`
   - **Install Command**: `pnpm install`

## Stap 2: Environment Variables

### 2.1 Verplichte Variabelen
Ga naar Settings > Environment Variables en voeg toe:

```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=https://your-backend-api.com
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# Internationalization
NEXT_PUBLIC_DEFAULT_LOCALE=nl
NEXT_PUBLIC_SUPPORTED_LOCALES=nl,en,fr,tr,ar,ps

# Optional
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn
```

### 2.2 Environment Variabelen per Omgeving
- **Production**: Alle variabelen
- **Preview**: Test variabelen
- **Development**: Lokale variabelen

## Stap 3: Custom Domain

### 3.1 Domain Toevoegen
1. Ga naar Settings > Domains
2. Klik op "Add Domain"
3. Voer je domain in: `vgm.be` of `www.vgm.be`

### 3.2 DNS Configuratie
Voeg de volgende DNS records toe:

```
Type: A
Name: @
Value: 76.76.19.61

Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

### 3.3 SSL Certificate
- Vercel regelt automatisch SSL certificaten
- Let's Encrypt certificaten worden automatisch vernieuwd

## Stap 4: Backend API Setup

### 4.1 Django Backend Deployen
Je backend moet draaien op een aparte server:

```bash
# Voorbeeld met Railway, Heroku, of DigitalOcean
# Zorg dat je backend CORS correct is ingesteld
CORS_ALLOWED_ORIGINS = [
    "https://vgm.be",
    "https://www.vgm.be",
    "https://vgm-website.vercel.app"
]
```

### 4.2 Database Setup
```bash
# PostgreSQL database
DATABASE_URL=postgresql://user:password@host:port/database

# Redis voor caching
REDIS_URL=redis://user:password@host:port
```

## Stap 5: Google Maps API

### 5.1 API Key Aanmaken
1. Ga naar [Google Cloud Console](https://console.cloud.google.com)
2. Maak een nieuw project aan: "VGM Website"
3. Schakel Maps JavaScript API in
4. Maak een API key aan
5. Beperk de key tot je domain

### 5.2 API Key Beperkingen
```
HTTP referrers (web sites):
- https://vgm.be/*
- https://www.vgm.be/*
- https://vgm-website.vercel.app/*
```

## Stap 6: Monitoring & Analytics

### 6.1 Vercel Analytics
1. Ga naar Analytics in je Vercel dashboard
2. Schakel Web Analytics in
3. Bekijk performance metrics

### 6.2 Sentry Error Tracking
1. Maak een account aan op [sentry.io](https://sentry.io)
2. Maak een nieuw project aan
3. Voeg de DSN toe aan environment variables

### 6.3 Performance Monitoring
```jsx
// In _app.tsx
import { Analytics } from '@vercel/analytics/react'

export default function App({ Component, pageProps }) {
  return (
    <>
      <Component {...pageProps} />
      <Analytics />
    </>
  )
}
```

## Stap 7: CI/CD Pipeline

### 7.1 GitHub Actions
Maak `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Vercel
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'pnpm'
      
      - name: Install pnpm
        run: npm install -g pnpm
      
      - name: Install dependencies
        run: cd frontend && pnpm install
      
      - name: Build
        run: cd frontend && pnpm build
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          working-directory: ./frontend
```

### 7.2 Secrets Instellen
In GitHub repository settings:
- `VERCEL_TOKEN`: Vercel API token
- `ORG_ID`: Vercel organization ID
- `PROJECT_ID`: Vercel project ID

## Stap 8: Security

### 8.1 Security Headers
De `next.config.js` bevat al:
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Referrer-Policy: strict-origin-when-cross-origin

### 8.2 Content Security Policy
```js
// In next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline' https://maps.googleapis.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.vgm.be;"
  }
]
```

## Stap 9: Performance Optimalisatie

### 9.1 Image Optimization
```jsx
import Image from 'next/image'

<Image
  src="/images/mosque.jpg"
  alt="Mosque"
  width={500}
  height={300}
  priority
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,..."
/>
```

### 9.2 Code Splitting
```jsx
import dynamic from 'next/dynamic'

const IftarMap = dynamic(() => import('@/components/ramadan/IftarMap'), {
  loading: () => <div>Loading map...</div>,
  ssr: false
})
```

### 9.3 Caching
```js
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

## Stap 10: Testing

### 10.1 Pre-deployment Tests
```bash
# Linting
cd frontend && pnpm lint

# Type checking
cd frontend && pnpm type-check

# Build test
cd frontend && pnpm build

# E2E tests
cd frontend && pnpm test:e2e
```

### 10.2 Post-deployment Tests
1. Test alle pagina's
2. Test alle talen
3. Test RTL layout
4. Test mobile responsiveness
5. Test Google Maps
6. Test API calls

## Stap 11: Go-live Checklist

### 11.1 Pre-launch
- [ ] Domain geconfigureerd
- [ ] SSL certificaat actief
- [ ] Environment variables ingesteld
- [ ] Backend API draait
- [ ] Google Maps API key werkt
- [ ] Alle talen getest
- [ ] Mobile responsive
- [ ] Performance geoptimaliseerd
- [ ] Security headers actief
- [ ] Monitoring ingesteld

### 11.2 Launch
- [ ] DNS records geüpdatet
- [ ] Vercel deployment succesvol
- [ ] Website bereikbaar
- [ ] Alle functionaliteiten werken
- [ ] Analytics actief
- [ ] Error tracking actief

### 11.3 Post-launch
- [ ] Performance monitoren
- [ ] Error logs controleren
- [ ] User feedback verzamelen
- [ ] SEO optimaliseren
- [ ] Content bijwerken

## Troubleshooting

### Veelvoorkomende Problemen

**Domain werkt niet**
- Controleer DNS records
- Wacht 24-48 uur voor DNS propagation
- Controleer SSL certificaat status

**API calls falen**
- Controleer CORS instellingen
- Controleer environment variables
- Controleer backend status

**Google Maps laadt niet**
- Controleer API key
- Controleer domain restrictions
- Controleer browser console

**Build errors**
- Controleer Node.js versie
- Controleer dependencies
- Controleer environment variables

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [Vercel Community](https://github.com/vercel/vercel/discussions)
- [VGM Development Team](mailto:dev@vgm.be)
