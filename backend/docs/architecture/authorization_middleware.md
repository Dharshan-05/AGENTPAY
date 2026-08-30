# Authorization Middleware (Phase 114)

## Overview

Phase 114 provides a `require_permission()` FastAPI dependency factory for enforcing authorization at endpoint boundaries. Authentication and authorization are strictly separated.

## The `require_permission()` Factory

**File:** `app/api/dependencies/authorization.py`

```python
from app.api.dependencies.authorization import require_permission

@router.get("/payments")
async def list_payments(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission("payments:read"))],
) -> ...:
    ...
```

`require_permission(permission)` returns an async FastAPI dependency that:
1. Calls `get_current_user()` — verifies JWT, session, and user status (→ 401 on failure).
2. Builds `AuthorizationContext` from verified session data (never from client input).
3. Calls `AuthorizationService.require_permission()` → raises `PermissionDeniedError` (→ 403) on deny.
4. Returns `AuthenticatedUser` to the endpoint handler on allow.

## HTTP Status Semantics

| Scenario | Status |
|---|---|
| No JWT / expired JWT | 401 Unauthorized |
| Revoked session | 401 Unauthorized |
| Disabled/locked user account | 403 Forbidden |
| Valid JWT, missing permission | 403 Forbidden |
| Valid JWT, permission present | 200/201/204 |

**Key rule**: A valid JWT never implies authorization. Identity (401) and authorization (403) are always separate checks.

## Security Properties

- **Fail closed**: Any non-allow decision raises `PermissionDeniedError` — no accidental grants.
- **Tenant context**: `AuthorizationContext.tenant_id` always comes from the verified session, never from the request body, query string, or headers.
- **No wildcard**: No `*` permission; every check requires an exact canonical name from the registry.
- **Multiple roles**: All role permissions are unioned at resolution time; user gets the maximum of all assigned roles.

## Architecture Flow

```
HTTP Request
  ↓
[get_current_user] ──────────────────────── 401 if auth fails
  ↓
[AuthorizationContext(user_id, tenant_id, session_id)]
  ↓
[AuthorizationService.resolve_permissions()] — single DB JOIN
  ↓
[permission in frozenset?] ────────────────── 403 if false
  ↓
[Endpoint handler receives AuthenticatedUser]
```
