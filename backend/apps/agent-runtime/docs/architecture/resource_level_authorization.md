# Resource-Level Authorization (Phase 115)

## Overview

Phase 115 provides IDOR-safe, tenant-isolated resource fetching helpers. All resource lookups include `tenant_id` in the database query — never fetch first and check after.

## Functions

**File:** `app/api/dependencies/resource_auth.py`

### `get_authorized_resource()`

```python
async def get_authorized_resource(
    db: AsyncSession,
    model: type[T],
    resource_id: uuid.UUID,
    tenant_id: uuid.UUID,
    *,
    raise_if_missing: bool = True,
) -> T | None
```

Queries: `SELECT * FROM <table> WHERE id = :id AND tenant_id = :tenant_id`

- Returns the resource if found and tenant matches.
- Returns `None` if `raise_if_missing=False` and not found.
- Raises `ResourceNotFoundOrForbiddenError` (→ HTTP 404) if not found and `raise_if_missing=True`.

### `get_authorized_resource_with_soft_delete()`

Same as above with an additional `AND deleted_at IS NULL` filter for soft-deletable models.

### `assert_resource_tenant()`

```python
def assert_resource_tenant(resource: Any, tenant_id: uuid.UUID) -> None
```

Defense-in-depth check after resource retrieval. Raises `ResourceNotFoundOrForbiddenError` if tenant mismatch detected.

## Usage in Endpoints

```python
from app.api.dependencies.resource_auth import get_authorized_resource


@router.get("/payments/{payment_id}")
async def get_payment(
    payment_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission("payments:read"))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> PaymentResponse:
    payment = await get_authorized_resource(db, PaymentOrder, payment_id, current_user.tenant_id)
    return PaymentResponse.model_validate(payment)
```

## IDOR Protection Design

The critical protection: **never fetch a resource then check tenant_id**. Instead, **always filter by both id AND tenant_id in the query**.

```
❌ WRONG (vulnerable to IDOR):
    payment = db.get(PaymentOrder, payment_id)
    if payment.tenant_id != current_user.tenant_id:
        raise 403

✅ CORRECT (IDOR-safe):
    payment = db.execute(
        SELECT * FROM payment_orders
        WHERE id = :id AND tenant_id = :tenant_id
    )
```

## IDOR Response Semantics

Cross-tenant resources return **HTTP 404** (not 403). This prevents revealing whether a resource exists in another tenant.

| Scenario | Status | Reason |
|---|---|---|
| Resource found, same tenant | 200 | Normal access |
| Resource not found | 404 | Does not exist |
| Resource exists in different tenant | 404 | IDOR protection — existence not revealed |
