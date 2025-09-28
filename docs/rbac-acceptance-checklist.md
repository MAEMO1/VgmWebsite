# RBAC Acceptatie-Checklist per Pagina / Tab

Gebruik dit als Definition of Done. Vink per rol af zodra de pagina aan de eisen voldoet.

## Publieke Pagina's

### Homepage (`/`)
- **Gast**: Hero, moskee-overzicht, publieke events, CTA registreren.
- **Lid**: Gevolgde moskeeën, persoonlijke events, dashboard-shortcut.
- **Moskee-beheerder**: Eigen moskee statistieken + beheerknoppen (`mosque.manage:own`).
- **Beheerder**: Platformstatistieken, admin-dashboard toegang.

### Moskee Directory (`/moskeeen`)
- **Gast**: Lijst + filters, basiscontact, publieke events.
- **Lid**: Favorieten, leden-evenementen, notificatievoorkeuren.
- **Moskee-beheerder**: Beheerknop & inline editing voor eigen moskee.
- **Beheerder**: Beheer alle moskeeën, approval-workflows, analytics.

### Moskee Pagina (`/moskee/[id]`)
- **Informatie**: Gast basisinfo; Lid+ extra details/favoriet; Beheerder inline editing volgens scope.
- **Geschiedenis**: Gast publiek; Lid+ uitgebreide content; Moskee-beheerder contentbeheer (eigen moskee).
- **Gebedstijden**: Gast standaard tijden; Lid+ notificatie-instellingen; Beheerder bewerken & speciale dagen.
- **Nieuws**: Gast publieke posts; Lid+ interacties; Moskee-beheerder creëren/schedulen (eigen moskee).
- **Evenementen**: Gast publieke events; Lid+ registratie + private events; Moskee-beheerder CRUD + analytics.
- **Donaties**: Gast campagnes bekijken; Lid+ doneren & historie; Moskee-beheerder campagnebeheer; Beheerder fees & platform-analyse.

## Authenticatie
- **Sign In (`/auth/signin`)**: Gast login, 2FA waar vereist, resetlink zichtbaar.
- **Signup Personal (`/auth/signup/personal`)**: E-mailverificatie → rol `LID`.
- **Signup Mosque (`/auth/signup/mosque`)**: Moskee status `pending` → admin-approval → rol `MOSKEE_BEHEERDER`.
- **Invite (`/invite/[token]`)**: Token → pending → admin/tweede beheerder bevestigt → actief.

## Dashboards
- **/dashboard** router: Gast → signin; Lid → `/dashboard/main`; Moskee-beheerder → `/dashboard/mosque-dashboard`; Beheerder → `/dashboard/admin`.
- **User Dashboard (`/dashboard/main`)**: Profiel, notificaties, kalender, donaties (Lid+).
- **Moskee Dashboard (`/dashboard/mosque-dashboard`)**: Overzicht, events, leden, campagnes, begrafenisgebeden, profiel (alleen eigen moskee).
- **Admin Dashboard (`/dashboard/admin`)**: Platform-overzicht, moskee-management, gebruikers/rollen, events, donaties, instellingen, audit.

## Community
- **Evenementen (`/gemeenschap/evenementen`)**: Gast publieke kalender; Lid registratie; Moskee-beheerder nieuw event; Admin cross-moskee beheer.
- **Begrafenisgebeden (`/begrafenisgebeden`)**: Gast lijst; Lid indienen; Moskee-beheerder goedkeuren/plannen; Admin coördinatie.
- **Campagnes (`/gemeenschap/campagnes`)**: Gast campagnes; Lid doneren/recurring; Moskee-beheerder campagnebeheer; Admin fee-management & analytics.

## Speciaal
- **Profiel (`/dashboard/profiel`)**: Lid+ accountbeheer; extra shortcuts per rol.
- **Notificaties (`/notificaties`)**: Lid+ notificaties; Moskee-beheerder moskee-notificaties; Admin platformnotificaties.
- **Moskee beheer (`/moskee-beheer/[id]`)**: Alleen eigen moskee (beheerder) + platform admins.
- **Juridische pagina's**: Altijd toegankelijk.

## Statusmachines
- Moskee: `pending → active → suspended` (mutaties blokkeren bij `suspended`).
- Content: `draft → scheduled → published → archived` (publish vereist relevante capability).

## Security / Governance
- 2FA verplicht voor `BEHEERDER`, aanbevolen (liefst verplicht) voor `MOSKEE_BEHEERDER`.
- Emailverificatie vereist voor `LID` en hoger.
- Inline bewerkingen loggen (audit trail).
- Rate limiting voor auth, invites, opmerkingen en inzendingen.
- Privacy voor begrafenisgebeden: publiek/leden/intern niveau + bewaartermijn.
