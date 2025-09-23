# Database & Indexen (PostgreSQL)

## Geografische queries
```sql
CREATE INDEX idx_mosque_location
  ON mosque_app_mosque USING GIST(location);
```

## User ↔ Moskee lookup

```sql
CREATE INDEX idx_membership_user_mosque
  ON mosque_app_membership(user_id, mosque_id);
```

## Event filtering

```sql
CREATE INDEX idx_event_date_mosque
  ON events(start_date, mosque_id);
```

## Notificatievoorkeuren

```sql
CREATE INDEX idx_notification_user_type
  ON notifications(user_id, notification_type);
```

## Full‑text & trigram (zoek)

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_mosque_name_trgm ON mosque_app_mosque
  USING GIN (name gin_trgm_ops);
```
