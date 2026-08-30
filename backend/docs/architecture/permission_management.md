# Permission Management (Phase 113)

## Overview

Phase 113 implements permission resolution, `has_permission()` / `require_permission()` policy evaluation, and role-permission assignment. Permissions are global (not tenant-scoped). Roles are tenant-scoped.

## API Endpoints

| Method | Path | Permission | Description |
|---|---|---|---|
| GET | `/api/v1/permissions` | `permissions:read` | List all permissions |
| GET | `/api/v1/permissions/{id}` | `permissions:read` | Get permission |
| GET | `/api/v1/roles/{role_id}/permissions` | `permissions:assign` | List role permissions |
| POST | `/api/v1/roles/{role_id}/permissions` | `permissions:assign` | Assign permission to role |
| DELETE | `/api/v1/roles/{role_id}/permissions/{permission_id}` | `permissions:revoke` | Revoke permission from role |

## Permission Resolution (N+1-Safe)

`resolve_permissions()` uses a single JOIN query:

```sql
SELECT DISTINCT p.name
FROM permissions p
JOIN role_permissions rp ON rp.permission_id = p.id
JOIN roles r ON r.id = rp.role_id
JOIN user_roles ur ON ur.role_id = r.id
  AND ur.tenant_id = :tenant_id
  AND ur.user_id = :user_id
WHERE r.tenant_id = :tenant_id
  AND r.status = 'active'
  AND r.deleted_at IS NULL
```

Result is a `frozenset[str]` of canonical permission names.

## Authorization Service Methods

```python
resolve_permissions(db, context) → frozenset[str]
has_permission(db, context, permission) → AuthorizationDecision
require_permission(db, context, permission) → None  # or raises PermissionDeniedError
list_permissions(db) → list[Permission]
get_permission(db, permission_id) → Permission | None
grant_role_permission(db, tenant_id, role_id, permission_id) → RolePermission
revoke_role_permission(db, tenant_id, role_id, permission_id) → None
list_role_permissions(db, tenant_id, role_id) → list[Permission]
```

## Security Model

- **Default deny**: `frozenset` membership check; absent = deny.
- **Fail closed**: `require_permission()` always raises `PermissionDeniedError` on non-allow.
- **Empty permission**: Always denied — no accidental empty-string grants.
- **Cross-tenant**: `grant_role_permission()` first validates `role.tenant_id`; cross-tenant role → `ValueError`.
- **Privilege escalation**: Assigning permissions requires `permissions:assign` itself.

## Database Tables Used

| Table | Purpose |
|---|---|
| `permissions` | Global permission registry |
| `role_permissions` | Role→Permission assignment records |
