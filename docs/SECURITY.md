# Security

## Headers
- `Content-Security-Policy`: strikte bronnen (self, CDN whitelists)
- `Strict-Transport-Security`: max-age >= 6 maanden
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`

## AuthN/Z
- Session‑based auth, secure & HttpOnly cookies, `SameSite=Lax` (prod)
- CSRF bescherming op alle state‑changing endpoints
- RBAC: rol + objectpermissions in DRF
- 2FA (TOTP): registratie + back‑up codes

## Rate limiting & Audit
- Throttling per endpointklasse (login/betalingen strenger)
- Audit log events: login, rolwijziging, betaling, export/delete verzoeken

## Secrets & rotatie
- Gebruik `.env` + secret manager in productie
- Idempotency keys voor Stripe; webhook‑signatures valideren

## Privacy
- Minimale dataverzameling, Data Subject Rights, logging‑retentiebeleid
