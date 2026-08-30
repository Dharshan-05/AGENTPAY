# Role Management (Phase 112)

## Overview

Phase 112 implements tenant-scoped role CRUD and user-role assignment backed by the existing `roles` and `user_roles` database tables.

## API Endpoints

| Method | Path | Permission | Description |
|---|---|---|---|
| GET | `/api/v1/roles` | `roles:read` | List tenant roles |
| GET | `/api/v1/roles/{role_id}` | `roles:read` | Get role |
| POST | `/api/v1/roles` | `roles:create` | Create role |
| PATCH | `/api/v1/roles/{role_id}` | `roles:update` | Update role |
| GET | `/api/v1/users/{user_id}/roles` | `roles:read` | List user roles |
| POST | `/api/v1/users/{user_id}/roles` | `roles:assign` | Assign role to user |
| DELETE | `/api/v1/users/{user_id}/roles/{role_id}` | `roles:revoke` | Remove user role |

## Service: AuthorizationService

**File:** `app/application/services/authorization.py`

### Methods

```python
list_roles(db, tenant_id) → list[Role]
get_role(db, tenant_id, role_id) → Role | None
create_role(db, tenant_id, name, description) → Role
update_role(db, tenant_id, role_id, updates) → Role
assign_role_to_user(db, tenant_id, user_id, role_id) → UserRole
remove_role_from_user(db, tenant_id, user_id, role_id) → None
list_user_roles(db, tenant_id, user_id) → list[Role]
```

## Security Constraints

- All queries include `WHERE tenant_id = :tenant_id` — no cross-tenant leakage.
- `body.tenant_id` must match `current_user.tenant_id` on creation or HTTP 403 is returned.
- System roles (`is_system=True`) cannot be modified or deleted.
- Duplicate role names within a tenant raise `ValueError` → HTTP 409.
- Role assignment deduplication — duplicate assignments raise `ValueError` → HTTP 409.

## Database Tables Used

| Table | Purpose |
|---|---|
| `roles` | Tenant-scoped role records |
| `user_roles` | User→Role assignment records |
