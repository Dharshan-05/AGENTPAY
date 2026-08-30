# User Preferences (Phase 118)

## Overview

Phase 118 introduces tenant-scoped user preference management stored in a flexible JSONB structure. Every user is guaranteed to have default preferences on first access.

## API Endpoints

| Method | Path | Permission | Description |
|---|---|---|---|
| GET | `/api/v1/users/me/preferences` | authenticated | Get own effective preferences |
| PATCH | `/api/v1/users/me/preferences` | authenticated | Update own preferences |

## Database Design

Table: `user_preferences`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PRIMARY KEY | UUIDv7 identifier |
| `user_id` | `UUID` | FK → `users.id` RESTRICT, UNIQUE | Associated user |
| `tenant_id` | `UUID` | NOT NULL, INDEX | Multi-tenancy isolation |
| `preferences` | `JSONB` | NOT NULL, DEFAULT `'{}'::jsonb` | Preference key-value bag |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT `now()` | Audit timestamp |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT `now()` | Audit timestamp |

Migration: `alembic/versions/037_user_preferences.py` (parent: `036_database_indexing_strategy`).

## Default Preference Values

When a preference record is created, or when reading effective preferences, missing keys fall back to:

```json
{
  "locale": "en",
  "timezone": "UTC",
  "notification_email": true,
  "notification_push": true,
  "notification_sms": false,
  "ui_theme": "system",
  "ui_language": "en",
  "accessibility_high_contrast": false,
  "accessibility_reduce_motion": false
}
```

## Security & Validation Controls

| Control | Implementation |
|---|---|
| Multi-tenancy | All database operations scope `WHERE user_id=? AND tenant_id=?` |
| IDOR protection | Preferences update first verifies user existence in tenant before applying patch |
| Prohibited fields | `UserPreferencesUpdateRequest` strictly rejects `role`, `roles`, `permissions`, `tenant_id`, `status`, `user_id`, `password`, `authentication` |
| Extra fields | `extra='forbid'` rejects any non-whitelisted JSON keys |
| BCP-47 validation | `locale` validated via regex: `^[a-z]{2}(-[A-Z]{2})?$` |
| Timezone validation | `timezone` must be non-empty string |
| UI Theme validation | `ui_theme` restricted to `'light'`, `'dark'`, `'system'` |

## Read & Patch Behavior

1. **GET**: returns `effective_preferences()` — stored JSON merged over defaults
2. **PATCH**: merges provided non-null fields into existing JSONB object in DB
