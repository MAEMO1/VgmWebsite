# VGM Platform – Vereniging van Gentse Moskeeën

Enterprise-grade beheersysteem voor Gentse moskeeën. Het platform centraliseert administratie (directory, evenementen, notificaties, donaties) met behoud van lokale autonomie per moskee. Focus op performance, security, meertaligheid (NL/EN/FR/TR/AR/PS, RTL) en productie‑rijpe backend.

## Inhoud
- [Belangrijkste features](#belangrijkste-features)
- [Architectuur](#architectuur)
- [Snel starten](#snel-starten)
- [Omgevingsvariabelen](#omgevingsvariabelen)
- [Development workflow](#development-workflow)
- [Testen & Kwaliteit](#testen--kwaliteit)
- [Security & Privacy](#security--privacy)
- [Documentatie](#documentatie)
- [Bijdragen](#bijdragen)
- [Licentie](#licentie)

## Belangrijkste features
- **Moskee Directory** met profielen en kaartweergave
- **Evenementenbeheer** + persoonlijke kalender
- **Begrafenisgebeden** (gespecialiseerde flow)
- **Donaties** via Stripe Connect (platform fee 5%)
- **Notificaties** (in‑app + e‑mail, realtime via websockets)
- **Dashboards**: gebruiker, moskee‑manager, platform‑admin
- **Meertaligheid** (6 talen) + **RTL** (AR/PS)
- **WCAG AA** en responsief ontwerp

## Architectuur
- **Frontend**: Next.js 14 (App Router), React 18, TypeScript, Tailwind, React Query
- **Backend**: Django 4.2 + DRF (+ Channels voor realtime), PostgreSQL, Redis
- **API‑contract**: OpenAPI (drf‑spectacular) → type‑veilige TS‑client
- **Infra**: CI/CD via GitHub Actions, previews per PR, Sentry/monitoring

> Zie: `docs/ARCHITECTURE.md` voor details (componenten, datamodellen, indexes).

## Snel starten

### Vereisten
- Node.js 20 + pnpm 9
- Python 3.12
- PostgreSQL 16
- Redis 7
- (Aanbevolen) VS Code Devcontainer of Docker

### 1) Repo clonen & dependencies
```bash
pnpm -v          # verwacht 9.x
python --version # 3.12.x

# Frontend
cd frontend && pnpm install && cd ..

# Backend
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 2) Omgevingsvariabelen

Kopieer voorbeeldbestanden en vul waarden in:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

Zie sectie **Omgevingsvariabelen** hieronder.

### 3) Database & migrations

```bash
# Vergeet niet: stel DATABASE_URL in je backend .env in
python backend/manage.py migrate
python backend/manage.py createsuperuser
```

### 4) Starten (lokaal)

In 2 terminals:

```bash
# Backend
python backend/manage.py runserver

# Frontend
cd frontend && pnpm dev
```

Frontend draait standaard op `http://localhost:3000`, backend op `http://localhost:8000`.

## Omgevingsvariabelen

**Backend (`backend/.env`):**

```
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:3000

DATABASE_URL=postgres://postgres:postgres@localhost:5432/vgm
REDIS_URL=redis://localhost:6379/0

EMAIL_HOST=smtp.example.org
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=secret
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=no-reply@vgm.example.org

STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PLATFORM_FEE_PERCENT=5

MAPS_BACKEND_API_KEY=xxx  # indien backend geocoding aanroept
```

**Frontend (`frontend/.env.local`):**

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_DEFAULT_LOCALE=nl
NEXT_PUBLIC_SUPPORTED_LOCALES=nl,en,fr,tr,ar,ps
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=xxx
NEXT_PUBLIC_SENTRY_DSN=
```

## Development workflow

* **OpenAPI first**: backend past endpoints aan → schema wordt gegenereerd → frontend types/hooks worden opnieuw gegenereerd.
* **Cursor AI**: richtlijnen en playbooks in `.cursor/rules/`. Start features met Composer‑playbooks.
* **Conventional Commits** voor nette changelogs en semantische releases.
* **E2E previews** per PR (frontend + backend + tijdelijke database).

Details: `docs/DEVELOPMENT.md`, `docs/CI-CD.md`, `.cursor/rules/*`.

## Testen & Kwaliteit

* **Backend**: Pytest, coverage, ruff/black/mypy
* **Frontend**: ESLint/Prettier/TS strict, React Testing Library, Playwright (E2E)
* **Accessibility**: axe checks
* **i18n**: key‑sync check (alle 6 talen up‑to‑date)

Zie: `docs/TESTING.md`.

## Security & Privacy

* Headers: CSP, HSTS, XFO, XCTO, RP
* Auth: session‑based, CSRF, RBAC, 2FA (TOTP)
* Rate limiting & audit logging
* GDPR: DSR endpoints (export/delete), consent

Zie: `docs/SECURITY.md` en `docs/GDPR.md`.

## Documentatie

Start bij:

* `docs/OVERVIEW.md` – productoverzicht
* `docs/ARCHITECTURE.md` – technische architectuur
* `docs/API.md` – schema & clientgeneratie
* `docs/I18N.md` – meertaligheid & RTL
* `docs/STRIPE.md` – betaalstromen
* `docs/NOTIFICATIONS.md` – notificatie‑ontwerp
* `docs/ADR/*` – beslissingen

## Bijdragen

Lees `docs/CONTRIBUTING.md` en `docs/ONBOARDING.md`.
PR‑template en CODEOWNERS zijn aanwezig; CI moet groen zijn.

## Licentie

© VGM. Alle rechten voorbehouden (interne bedrijfssoftware).
