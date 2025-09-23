# Development

## Monorepo
- `frontend/` – Next.js + TS + Tailwind
- `backend/` – Django + DRF (+ Channels)
- `.cursor/rules/` – AI‑regels en playbooks

## Werkwijze
1. **Issue → Branch** (trunk‑based, korte branches)
2. **Composer (Cursor)**: kies een playbook (`.cursor/rules/90-composer-playbooks.md`)
3. **OpenAPI first**: backend schema bijwerken → client regenereren
4. **Tests**: unit/integratie + E2E (Playwright)
5. **PR**: template invullen; CI groen vereist

## OpenAPI → Client
- Backend: `python manage.py spectacular --file schema.yaml`
- Frontend: `pnpm gen:client` (configureer `orval` of `openapi-typescript`)
- Hooks importeren: `import { useGetMosques } from '@/api/hooks'`

## Run scripts (suggestie)
- Backend: `make dev` of `python manage.py runserver`
- Frontend: `pnpm dev`
- Tests: `pytest`, `pnpm test`, `pnpm test:e2e`
