# CI/CD

## Pipelines
- **CI**: lint, typecheck, build, pytest, Playwright (smoke)
- **Preview**: per PR frontend + backend + tijdelijke DB (Neon)
- **Release**: semantisch (Conventional Commits), changelog, tag

## Beveiliging
- CodeQL, Dependabot, secret scanning
- Container/image scans indien Docker

## Gates
- Groen CI verplicht; minimaal 1 review van CODEOWNER
