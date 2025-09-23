# Backend (Django/DRF)
- drf-spectacular verplicht; update schema bij endpoint-wijziging.
- Permissions: IsAuthenticated standaard + objectniveau.
- CSRF op state-changing views; cookies secure/HttpOnly/SameSite.
- Channels: sessie-auth op websocket; weiger anonieme sockets.
- Migrations: geen modelwijziging zonder migratie + test.
