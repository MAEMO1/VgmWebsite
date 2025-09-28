# RBAC Testmatrix

Gebruik deze matrix als startpunt voor automatische en handmatige tests. Vul verder aan naarmate features groeien.

## Frontend (Vitest / Jest)

| Testcase | Beschrijving | Verwachte uitkomst |
|----------|--------------|--------------------|
| `RBAC guest access` | `hasCapability(null, 'content.view_public')` | `true` |
| | `hasCapability(null, 'profile.manage')` | `false` |
| `Lid permissions` | `hasCapability(lid, 'events.register')` | `true` |
| | `hasCapability(lid, 'events.manage')` | `false` |
| `Moskee beheerder scope` | `hasCapability(manager, 'mosque.manage', { mosqueId: 'own' })` | `true` |
| | `hasCapability(manager, 'mosque.manage', { mosqueId: 'other' })` | `false` |
| `Beheerder` | `hasCapability(admin, 'roles.manage')` | `true` |
| Route guard | `/dashboard` redirect per rol (mock user) | juiste redirect |
| Route guard | `/dashboard/admin` zonder admin | redirect `/auth/signin` |
| Protected component | Render child als capability toegestaan | zichtbaar |
| Protected component | Render fallback wanneer capability ontbreekt | fallback |

## Backend (Pytest)

| Testcase | Beschrijving | Verwachte uitkomst |
|----------|--------------|--------------------|
| Guest public | `has_capability(None, 'content.view_public')` | `True` |
| Guest restricted | `has_capability(None, 'profile.manage')` | `False` |
| Lid toegang | `has_capability(lid, 'events.register')` | `True` |
| | `has_capability(lid, 'events.manage')` | `False` |
| Moskee beheer (eigen) | `has_capability(manager, 'mosque.manage', mosque_id='own')` | `True` |
| Moskee beheer (vreemd) | hetzelfde met ander ID | `False` |
| Admin | willekeurige capability (bijv. `roles.manage`) | `True` |
| Decorator | Function-based view met decorator `@require_capability('mosque.manage')` | 403 indien niet toegestaan |
| DRF perm | API endpoint met `HasCapability('events.manage')` | 403/200 op basis van rol |

## Handmatige tests (bij release)

- Dashboard router: login als elke rol & controleer redirect.
- Inline editing: alleen zichtbaar bij juiste capability; wijzigingen worden gelogd.
- Moskee status: set moskee `suspended` → mutaties geblokkeerd.
- Gebedstijden & donaties: gast vs lid vs beheerder.
- Invitations: token vervalt na gebruik; tweede gebruik → foutmelding.
- 2FA: Admin zonder 2FA → blokkeren/waarschuwen.

## Tips
- Houd `rbac.config.json` als bron -> tests genereren capabilities dynamisch.
- Combineer RBAC tests met feature tests (events, campagnes) om regressies te voorkomen.
- Voeg data builders toe voor user/moskee + fixtures voor clean DB per test.
