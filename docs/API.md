# API

## Schema genereren (backend)
```bash
python backend/manage.py spectacular --file backend/schema.yaml
```

## Types & hooks genereren (frontend)

Gebruik `orval` of `openapi-typescript`:

```bash
pnpm gen:client
```

* Output: `frontend/src/api/*`
* Bevat: TS types, React Query hooks, fetcher met auth‑cookie

## Authenticatie

* Session‑based (Django)
* CSRF: frontend haalt CSRF cookie op via `/api/csrf/`; requests sturen `X-CSRFToken`.

## Conventies

* 2xx: success; 4xx: client fouten; 5xx: server
* Gestandaardiseerde error‑payload met code, message, details
