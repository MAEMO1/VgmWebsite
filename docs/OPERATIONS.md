# Operations

## Omgevingen
- Dev → Preview → Prod
- Feature‑preview per PR

## Database
- Migraties versieneren; `makemigrations --check` in CI
- Backups: dag/nacht, hersteltesten
- Read‑replica's (optioneel)

## Observability
- Sentry (frontend/backend)
- Structured logging (request id, user id)
- Health endpoints: liveness/readiness

## Webhooks
- Betalingen (Stripe): retry/backoff, idempotency, outbox‑pattern
