# RBAC Architecture (Phase 111)

## Overview

Phase 111 establishes the domain foundation for the AGENTPAY Role-Based Access Control (RBAC) system. All authorization decisions are deterministic, fail-closed, and tenant-isolated.

## Domain Abstractions

### AuthorizationContext
**File:** `app/domain/authorization/context.py`

An immutable, frozen dataclass carrying the verified principal identity for authorization evaluation.

```python
@dataclass(frozen=True)
class AuthorizationContext:
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    session_id: uuid.UUID
```

**Invariants:**
- All fields are UUIDs from the verified JWT/session — never from client input.
- Zero-value UUIDs are rejected at construction.
- Immutable: any mutation attempt raises `FrozenInstanceError`.
- `session_id` is excluded from `repr()` for safety.

### AuthorizationDecision
**File:** `app/domain/authorization/decision.py`

An immutable value object representing the outcome of a single authorization check.

```python
@dataclass(frozen=True)
class AuthorizationDecision:
    allowed: bool       # True = allow; False = deny (default)
    reason: str         # Internal; never surfaced to clients
    permission: str     # The evaluated permission name
```

**Factory methods:**
- `AuthorizationDecision.allow(permission)` — explicit grant
- `AuthorizationDecision.deny(permission)` — default-deny

### PermissionsRegistry
**File:** `app/domain/authorization/permissions_registry.py`

Canonical typed string constants for all permission names. Format: `resource:action`.

```python
PAYMENTS_READ = "payments:read"
ROLES_ASSIGN  = "roles:assign"
# ...
ALL_PERMISSIONS: frozenset[str]  # Complete canonical registry
```

No client-supplied permission strings are ever evaluated. Only registry constants are used.

### PermissionDeniedError / ResourceNotFoundOrForbiddenError
**File:** `app/domain/exceptions/auth_exceptions.py`

```python
class PermissionDeniedError(AgentPayError):    # → HTTP 403
class ResourceNotFoundOrForbiddenError(AgentPayError):  # → HTTP 404 (IDOR-safe)
```

## Security Properties

| Property | Guarantee |
|---|---|
| Default deny | `frozenset` lookup; not found = deny |
| Fail closed | `PermissionDeniedError` raised on deny |
| Tenant isolation | `tenant_id` always from verified session |
| Immutability | All domain objects are frozen dataclasses |
| 401 vs 403 | Auth failure → 401; authz failure → 403 |
