# Architectuur

## High-level
- **Frontend**: Next.js 14 (App Router), React 18, TypeScript, Tailwind, React Query
- **Backend**: Django + DRF, Channels (websockets), PostgreSQL, Redis
- **Integraties**: Stripe Connect, Google Maps, e-mail/SMS providers
- **Observability**: logging, Sentry (optioneel), health endpoints

## Data & Modellen (kern)
- `User`, `Mosque`, `Membership` (rollen: guest, member, manager, admin)
- `Event`, `EventRegistration`, `FuneralPrayer`
- `DonationCampaign`, `Payment` (Stripe)
- `NotificationPreference`, `Notification`
- `BoardMember`, `AdminSettings`

## Indexering (Postgres)
Zie `docs/DB.md` voor SQL‑indices (geografie, events, notificaties, membership).

## Realtime
- Django Channels met Redis broker
- Namespaces: `notifications:*`, `events:*`
- Auth via sessiecookie, alleen geauthenticeerde sockets

## API‑contract
- DRF + drf‑spectacular → `openapi.json`
- TS‑client + React Query hooks (generatie via orval/openapi‑typescript)
- Geen tRPC (ADR‑0001)

## Security
- CSP/HSTS/XFO/XCTO/Referrer‑Policy
- CSRF + SameSite/secure cookies
- RBAC op endpoint‑ en objectniveau
- Rate limiting + audit logging

## I18n/RTL
- 6 talen (NL, EN, FR, TR, AR, PS)
- RTL voor AR/PS
- Key‑gebaseerde vertalingen + sync tooling (zie `docs/I18N.md`)
