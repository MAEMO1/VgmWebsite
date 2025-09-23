# VGM Frontend

Next.js 14 frontend voor de VGM (Vereniging van Gentse Moskeeën) website.

## Features

- **Next.js 14** met App Router
- **TypeScript** voor type safety
- **Tailwind CSS** voor styling
- **React Query** voor data fetching
- **Next-intl** voor internationalisatie (6 talen)
- **RTL Support** voor Arabisch en Pashto
- **Google Maps** integratie
- **Responsive design** voor alle devices

## Talen

- Nederlands (NL) - Default
- Engels (EN)
- Frans (FR)
- Turks (TR)
- Arabisch (AR) - RTL
- Pashto (PS) - RTL

## Snel Starten

### Vereisten

- Node.js 20+
- pnpm 9+

### Installatie

```bash
# Dependencies installeren
pnpm install

# Environment variabelen instellen
cp .env.local.example .env.local
# Edit .env.local met je waarden

# Development server starten
pnpm dev
```

### Environment Variabelen

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your-google-maps-api-key
NEXT_PUBLIC_DEFAULT_LOCALE=nl
NEXT_PUBLIC_SUPPORTED_LOCALES=nl,en,fr,tr,ar,ps
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn
```

## Scripts

```bash
# Development
pnpm dev

# Build voor productie
pnpm build

# Productie server starten
pnpm start

# Linting
pnpm lint

# Type checking
pnpm type-check

# Tests
pnpm test

# E2E tests
pnpm test:e2e

# API client genereren
pnpm gen:client
```

## Project Structuur

```
src/
├── app/                 # Next.js App Router
│   ├── [locale]/       # Internationalized routes
│   ├── api/            # API routes
│   └── globals.css     # Global styles
├── components/         # React components
│   ├── layout/         # Layout components
│   ├── home/           # Homepage components
│   └── ramadan/        # Ramadan specific components
├── api/                # API client
├── hooks/              # Custom React hooks
├── lib/                # Utility functions
├── types/              # TypeScript types
└── utils/              # Helper functions
```

## Internationalisatie

### Nieuwe vertalingen toevoegen

1. Voeg de key toe aan `messages/nl.json`
2. Voeg dezelfde key toe aan andere taalbestanden
3. Gebruik de key in je component:

```jsx
import { useTranslations } from 'next-intl'

function MyComponent() {
  const t = useTranslations('MyComponent')
  return <h1>{t('title')}</h1>
}
```

### RTL Support

Voor Arabisch en Pashto wordt automatisch RTL toegepast:

```jsx
// CSS classes die RTL ondersteunen
<div className="mr-4"> // margin-right in LTR, margin-left in RTL
<div className="ml-4"> // margin-left in LTR, margin-right in RTL
```

## API Integration

### OpenAPI Client

De frontend gebruikt een gegenereerde API client:

```bash
# Client genereren na backend wijzigingen
pnpm gen:client
```

### Gebruik in components

```jsx
import { useGetMosques } from '@/api/hooks'

function MosquesList() {
  const { data: mosques, isLoading } = useGetMosques()
  
  if (isLoading) return <div>Loading...</div>
  
  return (
    <div>
      {mosques?.map(mosque => (
        <div key={mosque.id}>{mosque.name}</div>
      ))}
    </div>
  )
}
```

## Styling

### Tailwind CSS

We gebruiken Tailwind CSS met custom configuratie:

```jsx
// Custom colors
<div className="bg-primary-600 text-white">
<div className="bg-secondary-500 text-white">

// Responsive design
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">

// RTL support
<div className="mr-4 rtl:ml-4">
```

### Custom Components

```jsx
// Gebruik van custom component classes
<button className="btn-primary">Primary Button</button>
<input className="input-field" />
<div className="card">Card Content</div>
```

## Google Maps

### Iftar Map Component

```jsx
import { IftarMap } from '@/components/ramadan/IftarMap'

function RamadanPage() {
  return <IftarMap />
}
```

### API Key Setup

1. Ga naar [Google Cloud Console](https://console.cloud.google.com)
2. Maak een project aan
3. Schakel Maps JavaScript API in
4. Maak een API key aan
5. Voeg de key toe aan je environment variabelen

## Deployment

### Vercel

De frontend is geconfigureerd voor deployment op Vercel:

1. Push code naar GitHub
2. Import project in Vercel
3. Stel environment variabelen in
4. Deploy automatisch

Zie `docs/VERCEL_DEPLOYMENT.md` voor details.

### Environment Variabelen voor Productie

```env
NEXT_PUBLIC_API_BASE_URL=https://your-backend-api.com
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your-production-api-key
NEXT_PUBLIC_DEFAULT_LOCALE=nl
NEXT_PUBLIC_SUPPORTED_LOCALES=nl,en,fr,tr,ar,ps
```

## Performance

### Optimalisaties

- **Image Optimization**: Next.js Image component
- **Code Splitting**: Automatisch via Next.js
- **Caching**: React Query voor API calls
- **Bundle Analysis**: `pnpm build` toont bundle size

### Monitoring

- **Vercel Analytics**: Automatisch ingeschakeld
- **Sentry**: Error tracking (optioneel)
- **Core Web Vitals**: Automatisch gemeten

## Troubleshooting

### Veelvoorkomende Problemen

**Build errors**
```bash
# Dependencies herinstalleren
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

**API calls falen**
- Controleer `NEXT_PUBLIC_API_BASE_URL`
- Controleer CORS instellingen in backend
- Controleer network tab in browser dev tools

**Google Maps laadt niet**
- Controleer `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`
- Controleer dat Maps JavaScript API is ingeschakeld
- Controleer browser console voor errors

**Internationalisatie werkt niet**
- Controleer dat alle taalbestanden bestaan
- Controleer dat keys consistent zijn
- Controleer browser locale instellingen

## Contributing

1. Fork het project
2. Maak een feature branch
3. Commit je wijzigingen
4. Push naar de branch
5. Open een Pull Request

### Code Style

- Gebruik TypeScript strict mode
- Volg ESLint regels
- Gebruik Prettier voor formatting
- Schrijf tests voor nieuwe features

## Licentie

© VGM. Alle rechten voorbehouden.
