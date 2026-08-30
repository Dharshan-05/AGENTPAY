# User Profile API (Phase 117)

## Overview

Phase 117 implements profile management for both self-service (own profile) and admin read access (other users' profiles within tenant).

## API Endpoints

| Method | Path | Permission | Description |
|---|---|---|---|
| GET | `/api/v1/users/me/profile` | authenticated | Get own profile |
| PATCH | `/api/v1/users/me/profile` | authenticated | Update own profile |
| GET | `/api/v1/users/{user_id}/profile` | `users:read` | Get user profile (admin) |

## Architecture

```
FastAPI endpoint
  → get_current_user dependency (self-service)
    OR require_permission(users:read) (admin access)
  → UserService.get_user_profile() / update_user_profile()
  → UserProfile ORM (WHERE user_id=? AND tenant_id=?)
```

## Security Controls

| Control | Implementation |
|---|---|
| Self-service | `/me/profile` uses `current_user.user.id` from JWT — no user_id from URL |
| Admin access | `/users/{user_id}/profile` requires `users:read` and scoped to tenant |
| IDOR | Profile lookups always `WHERE user_id=? AND tenant_id=?` |
| Forbidden fields | Request schema only allows display metadata fields |
| Extra fields rejected | `UserProfileUpdateRequest(extra='forbid')` |

## Updatable Fields

Via `PATCH /users/me/profile`:
- `first_name` (max 100 chars)
- `last_name` (max 100 chars)  
- `display_name` (max 150 chars)
- `avatar_url` (must be http/https)
- `phone_number` (max 50 chars)

**Not updatable via profile endpoint** (rejected by `extra='forbid'`):
- `tenant_id`, `user_id`, `id`
- `role`, `roles`, `permissions`
- `status`, `password`
- `timezone`, `locale` (→ use preferences API)

## Response Schema

`UserProfileFullResponse` includes:
- `id`, `user_id`, `tenant_id`
- `first_name`, `last_name`, `display_name`, `avatar_url`, `phone_number`
- `created_at`, `updated_at`

Excluded: `deleted_at`, authentication fields, security internals.
