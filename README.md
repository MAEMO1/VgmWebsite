# VGM Platform – Vereniging van Gentse Moskeeën

Dit project bundelt een Flask-API en een Next.js-frontend om moskeegegevens, evenementen, donaties en Ramadan-informatie voor Gent te beheren. De focus ligt op meertaligheid (NL/EN/FR/TR/AR/PS), betalingsverwerking via Stripe en tooling voor beheerders.

## Inhoud
- [Belangrijkste features](#belangrijkste-features)
- [Architectuur](#architectuur)
- [Snel starten](#snel-starten)
- [Omgevingsvariabelen](#omgevingsvariabelen)
- [Development workflow](#development-workflow)
- [Testen & Kwaliteit](#testen--kwaliteit)
- [Bijdragen](#bijdragen)
- [Licentie](#licentie)

## Belangrijkste features
- **Moskee directory** met kaartweergave (Google Maps)
- **Evenementen & Ramadan iftar** kaart + kalender
- **Donaties** met Stripe Payment Intents
- **Bestandsbeheer** voor moskeeën (uploads, galerij)
- **Notificaties & analytics** voor admins (API endpoints + frontend componenten)
- **Geavanceerde zoekfunctie** over moskeeën, nieuws, evenementen en campagnes

## Architectuur
- **Frontend**: Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, React Query, next-intl
- **Backend**: Flask 3 met sqlite (instance database) en RESTful endpoints (`app.py`), Stripe SDK, file uploads
- **Legacy**: er staat nog een oudere Flask/SQLAlchemy app (`main.py`, `routes/`, `templates/`) die gradueel wordt uitgefaseerd
- **Infra**: Dockerfiles voor backend/frontend, GitHub Actions workflow (`.github/workflows/deploy.yml`)

> Let op: documentatie in `docs/` verwijst nog deels naar een eerdere Django-architectuur. Gebruik dit README als bron van waarheid totdat die documenten zijn bijgewerkt.

## Snel starten

### Vereisten
- Python 3.11+
- Node.js 18+
- npm (of pnpm/yarn)

### 1) Dependencies installeren
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cd frontend
npm install
cd ..
```

### 2) Omgevingsvariabelen instellen
```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local
```
Vul je eigen waarden in (Stripe sleutel, Google Maps API key, enz.).

### 3) Database initialiseren
De nieuwe Flask-API maakt en seedt de sqlite-database automatisch bij de eerste start (`instance/vgm_website.db`). Wil je opnieuw beginnen, verwijder dan het bestand of roep `python app.py --initdb` (in aanbouw).

### 4) Project starten
```bash
# Terminal 1 – API (Flask)
python app.py

# Terminal 2 – Frontend (Next.js)
cd frontend
npm run dev
```
Frontend draait op `http://localhost:3000`, de API op `http://localhost:5001`.

## Omgevingsvariabelen

`.env` (backend):
```
DATABASE_URL=sqlite:///instance/vgm_website.db
SESSION_SECRET=change-me
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
PORT=5001
```

`frontend/.env.local`:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:5001
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=<your-key>
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
NEXT_PUBLIC_DEFAULT_LOCALE=nl
NEXT_PUBLIC_SUPPORTED_LOCALES=nl,en,fr,tr,ar,ps
```

## Development workflow
- Backend code leeft primair in `app.py` en `/services`. Houd `main.py` en `routes/` alleen aan als je legacy paginas nodig hebt.
- Frontend haalt data op via `frontend/src/api/client.ts` en React Query hooks.
- Gebruik `uvicorn`/`gunicorn` in productie (zie `Dockerfile`/`render.yaml`).
- OpenAPI-schema (`openapi.json`) en orval-config helpen bij typegeneratie.

## Testen & Kwaliteit
- **Backend**: pytest (nog te schrijven), black/ruff ingesteld via `pyproject.toml`
- **Frontend**: Jest + React Testing Library, Playwright E2E (scripts staan in `package.json`)
- Draai lokaal `npm run lint` en `npm run test` voordat je push verricht.

## Bijdragen
- Gebruik feature branches, schrijf korte changelog/commit beschrijvingen.
- Synchroniseer met het team over het uitfaseren van de legacy Flask-app voordat je grote refactors doet.
- Houd de TODO-lijst (`TODO.md`) bij voor resterende P1–P3 items.

## Licentie

© VGM. Interne bedrijfssoftware; niet bedoeld voor publieke distributie.
