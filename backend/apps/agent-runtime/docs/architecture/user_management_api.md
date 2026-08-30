# User Management API (Phase 116)

## Overview

Phase 116 implements a production-grade, tenant-isolated User Management API. All operations enforce authorization through the Phase 111–115 RBAC system.

## API Endpoints

| Method | Path | Permission | Description |
|---|---|---|---|
| GET | `/api/v1/users` | `users:read` | List tenant users (keyset paginated) |
| GET | `/api/v1/users/me` | authenticated | Get authenticated user |
| GET | `/api/v1/users/{user_id}` | `users:read` | Get user by ID |
| PATCH | `/api/v1/users/{user_id}/status` | `users:update` | Update user status |

## Architecture

```
FastAPI endpoint
  → require_permission() dependency
  → UserService (app/application/services/user_service.py)
  → SQLAlchemy + AsyncSession (tenant-filtered queries)
```

## Tenant Isolation

Every query includes `WHERE tenant_id = :authenticated_tenant_id`. The `tenant_id` always comes from the verified JWT session — never from the request body or query parameters.

Cross-tenant access returns HTTP 404 (IDOR protection — existence is not revealed).

## Security Controls

| Control | Implementation |
|---|---|
| Default deny | All admin endpoints require explicit permission via `require_permission()` |
| IDOR protection | `WHERE id=? AND tenant_id=?` always |
| Secret redaction | `UserResponse` never includes `password_hash`, `failed_login_attempts`, `locked_until` |
| Mass assignment | `UserStatusUpdateRequest(extra='forbid')` |
| Privilege escalation | `users:update` required to change any user's status |

## Pagination

Uses **keyset pagination** (`cursor_created_at` + `cursor_id`), not OFFSET.

Query: `ORDER BY created_at DESC, id DESC` with `WHERE (created_at < cursor OR (created_at = cursor AND id < cursor_id))`.

Maximum page size: 100. Default: 20.

## Response Schema

`UserResponse` safe fields:
- `id`, `tenant_id`, `email`, `status`
- `email_verified_at`, `last_login_at`
- `created_at`, `updated_at`
- `profile` (embedded minimal profile)

Excluded: `password_hash`, `failed_login_attempts`, `locked_until`, session data, tokens.
