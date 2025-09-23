# VGM – AI Projectoverzicht
Doel: bouw een veilig, performant, meertalig platform. Respecteer WCAG AA, RBAC, 2FA, CSP/HSTS, GDPR.

Architectuur:
- Frontend: Next.js 14, TS strict, Tailwind, React Query
- Backend: Django + DRF (+ Channels), Postgres, Redis
- API: OpenAPI via drf-spectacular → TS client; **geen tRPC**.

AI-gedrag:
- Schrijf tests en update OpenAPI + client bij elke wijziging.
- Voeg i18n-keys toe; houd alle 6 talen in sync.
- Bewaak CSRF/cookies/permissions; geen nieuwe stack zonder ADR.
Definition of Done:
- Lint/typecheck/tests/CI groen; schema & i18n bijgewerkt; changelog/notes.
