# VGM Quick Start Guide

Snelle startgids voor het deployen van de VGM website naar Vercel.

## 🚀 Snelle Start (5 minuten)

### 1. Vercel Project Aanmaken
```bash
# Run het setup script
./scripts/setup-vercel.sh
```

### 2. Environment Variables Instellen
In je Vercel dashboard:
- Ga naar Project Settings > Environment Variables
- Voeg de volgende variabelen toe:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-backend-api.com
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your-google-maps-api-key
NEXT_PUBLIC_DEFAULT_LOCALE=nl
NEXT_PUBLIC_SUPPORTED_LOCALES=nl,en,fr,tr,ar,ps
```

### 3. Deployen
```bash
# Deploy naar productie
./scripts/deploy-vercel.sh
```

### 4. Controleren
```bash
# Check deployment status
./scripts/check-deployment.sh
```

## 📋 Checklist

### Pre-deployment
- [ ] Vercel account aangemaakt
- [ ] GitHub repository geïmporteerd
- [ ] Environment variables ingesteld
- [ ] Backend API draait
- [ ] Google Maps API key beschikbaar

### Post-deployment
- [ ] Website bereikbaar
- [ ] Alle talen werken
- [ ] Google Maps laadt
- [ ] API calls werken
- [ ] Mobile responsive

## 🔧 Troubleshooting

### Veelvoorkomende Problemen

**Build fails**
```bash
# Check dependencies
cd frontend && pnpm install
cd frontend && pnpm build
```

**API calls falen**
- Controleer `NEXT_PUBLIC_API_BASE_URL`
- Controleer CORS instellingen in backend

**Google Maps laadt niet**
- Controleer `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`
- Controleer domain restrictions

## 📞 Support

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [VGM Development Team](mailto:dev@vgm.be)
