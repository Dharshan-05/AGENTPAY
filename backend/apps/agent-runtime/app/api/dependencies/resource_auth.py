"""AGENTPAY Resource-Level Authorization Helpers (Phase 115).

Provides utilities for IDOR-safe, tenant-isolated resource fetching.

Security model:
- All resources are fetched with BOTH `id` AND `tenant_id` in the WHERE clause.
- Cross-tenant access always returns None (never leaks existence).
- Return 404 for missing or cross-tenant resources (IDOR protection).
- Authorization permission check is separate from resource existence check.

Usage in endpoints:

    payment = await get_authorized_resource(
        db=db,
        model=PaymentOrder,
        resource_id=payment_id,
        tenant_id=current_user.tenant_id,
    )
    # If None → raises ResourceNotFoundOrForbiddenError (404)
"""

from __future__ import annotations

import uuid
from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.auth_exceptions import ResourceNotFoundOrForbiddenError

T = TypeVar("T")


async def get_authorized_resource(
    db: AsyncSession,
    model: type[T],
    resource_id: uuid.UUID,
    tenant_id: uuid.UUID,
    *,
    raise_if_missing: bool = True,
) -> T | None:
    """Fetch a tenant-isolated resource by ID with built-in IDOR protection.

    Queries: SELECT * FROM <table> WHERE id = :id AND tenant_id = :tenant_id

    This prevents IDOR by NEVER fetching a resource and then checking
    tenant_id after retrieval.

    Args:
        db:               Active async database session.
        model:            SQLAlchemy ORM model class. Must have `id` and `tenant_id`.
        resource_id:      The resource UUID to fetch.
        tenant_id:        The tenant UUID from the authenticated session (never from client).
        raise_if_missing: If True, raises ResourceNotFoundOrForbiddenError when not found.

    Returns:
        The ORM instance if found and tenant matches; None otherwise.

    Raises:
        ResourceNotFoundOrForbiddenError: If resource not found and raise_if_missing is True.
    """
    stmt = select(model).where(
        model.id == resource_id,  # type: ignore[attr-defined]
        model.tenant_id == tenant_id,  # type: ignore[attr-defined]
    )
    result = await db.execute(stmt)
    instance = result.scalar_one_or_none()

    if instance is None and raise_if_missing:
        raise ResourceNotFoundOrForbiddenError()

    return instance


async def get_authorized_resource_with_soft_delete(
    db: AsyncSession,
    model: type[T],
    resource_id: uuid.UUID,
    tenant_id: uuid.UUID,
    *,
    raise_if_missing: bool = True,
) -> T | None:
    """Fetch a tenant-isolated resource, excluding soft-deleted records.

    Queries:
        SELECT * FROM <table>
        WHERE id = :id AND tenant_id = :tenant_id AND deleted_at IS NULL

    Args:
        db:               Active async database session.
        model:            SQLAlchemy ORM model class with `id`, `tenant_id`, `deleted_at`.
        resource_id:      The resource UUID to fetch.
        tenant_id:        The tenant UUID from the authenticated session.
        raise_if_missing: If True, raises ResourceNotFoundOrForbiddenError when not found.

    Returns:
        The ORM instance if found, in-tenant, and not soft-deleted; None otherwise.

    Raises:
        ResourceNotFoundOrForbiddenError: If resource not found and raise_if_missing is True.
    """
    stmt = select(model).where(
        model.id == resource_id,  # type: ignore[attr-defined]
        model.tenant_id == tenant_id,  # type: ignore[attr-defined]
        model.deleted_at.is_(None),  # type: ignore[attr-defined]
    )
    result = await db.execute(stmt)
    instance = result.scalar_one_or_none()

    if instance is None and raise_if_missing:
        raise ResourceNotFoundOrForbiddenError()

    return instance


def assert_resource_tenant(
    resource: Any,
    tenant_id: uuid.UUID,
) -> None:
    """Assert that a loaded resource's tenant_id matches the expected tenant.

    Use as an additional defense-in-depth check after resource retrieval.

    Raises:
        ResourceNotFoundOrForbiddenError: If tenant_id does not match.
    """
    resource_tenant = getattr(resource, "tenant_id", None)
    if resource_tenant != tenant_id:
        raise ResourceNotFoundOrForbiddenError()
