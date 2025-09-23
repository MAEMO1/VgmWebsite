# Testen & Kwaliteit

## Backend
- **Unit**: serializers, permissions, services
- **Integratie**: endpoints, DB transactiegedrag
- **Tools**: pytest, coverage, ruff, black, mypy

## Frontend
- **Unit/Component**: React Testing Library
- **E2E**: Playwright (auth, donatieflow, RTL)
- **Static**: ESLint, TS strict, Prettier

## Targets (indicatief)
- Coverage ≥ 80% kernpakketten
- Playwright smoke suite draait in CI (headless)
- Accessibility checks (axe) in kritieke paden
