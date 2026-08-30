# AGENTPAY Authorization Matrix (Phase 111–115)

## Permission Format

All permissions follow the convention: `resource:action`

Permissions are defined as typed string constants in `app/domain/authorization/permissions_registry.py`.

No client-supplied permission strings are ever trusted.

---

## Authorization Matrix

| Domain | Permission | Description |
|--------|-----------|-------------|
| **Identity** | `users:read` | Read user accounts |
| | `users:create` | Create user accounts |
| | `users:update` | Update user accounts |
| | `users:delete` | Delete user accounts |
| **Role Administration** | `roles:read` | List and view roles |
| | `roles:create` | Create new roles |
| | `roles:update` | Update existing roles |
| | `roles:assign` | Assign roles to users |
| | `roles:revoke` | Remove role assignments |
| **Permission Administration** | `permissions:read` | View registered permissions |
| | `permissions:assign` | Assign permissions to roles |
| | `permissions:revoke` | Revoke permissions from roles |
| **Payments** | `payments:read` | Read payment orders |
| | `payments:create` | Create payment orders |
| | `payments:update` | Update payment orders |
| | `payments:refund` | Initiate refunds |
| | `payments:cancel` | Cancel payments |
| **Transactions** | `transactions:read` | Read payment transactions |
| **Reviews** | `reviews:read` | Read review queue |
| | `reviews:approve` | Approve review queue items |
| | `reviews:reject` | Reject review queue items |
| **Audit** | `audit_logs:read` | Read global audit logs |
| **Security** | `security_events:read` | Read security events |
| **Agents** | `agents:read` | Read agent records |
| | `agents:create` | Create agents |
| | `agents:update` | Update agents |
| | `agents:delete` | Delete agents |
| | `agents:execute` | Execute agent actions |
| **Merchants** | `merchants:read` | Read merchant records |
| | `merchants:create` | Create merchants |
| | `merchants:update` | Update merchants |

---

## Authorization Decision Flow

```
Request
  ↓
[get_current_user] — Verifies JWT signature, session, user status
  ↓
[require_permission("permission:name")] — Enforces authorization
  ↓
[AuthorizationService.resolve_permissions()] — DB JOIN: user→roles→permissions
  ↓
[AuthorizationDecision.allow() / .deny()] — Deterministic, immutable decision
  ↓
[PermissionDeniedError → HTTP 403] if denied
  ↓
[Endpoint handler]
  ↓
[get_authorized_resource()] — Tenant-isolated resource fetch (WHERE id=? AND tenant_id=?)
  ↓
[ResourceNotFoundOrForbiddenError → HTTP 404] if cross-tenant IDOR
```

---

## Security Controls

| Control | Implementation |
|---------|---------------|
| Default deny | `frozenset` permission lookup; not found = deny |
| Fail closed | `PermissionDeniedError` on missing or empty permission |
| Tenant isolation | `AuthorizationContext.tenant_id` from verified session |
| IDOR protection | All resources queried with `id AND tenant_id` |
| Privilege escalation | System roles immutable; permission assignment requires permission |
| Cross-tenant | Role/resource lookup always scoped to `tenant_id` |
| 401 vs 403 | Auth failure → 401; permission failure → 403 |
