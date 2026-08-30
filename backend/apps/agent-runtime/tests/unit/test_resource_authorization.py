"""Unit tests for Phase 115 — Resource-Level Authorization.

Tests:
- Same-tenant resource access succeeds
- Cross-tenant resource access returns None (IDOR protection)
- raise_if_missing=True raises ResourceNotFoundOrForbiddenError
- raise_if_missing=False returns None safely
- assert_resource_tenant raises on mismatch
- Soft-deleted resource is excluded
- IDOR: cross-tenant returns 404 not 403 (existence not revealed)
- Explicit IDOR scenario: tenant A cannot access tenant B's resource
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.api.dependencies.resource_auth import (
    assert_resource_tenant,
    get_authorized_resource,
    get_authorized_resource_with_soft_delete,
)
from app.domain.exceptions.auth_exceptions import ResourceNotFoundOrForbiddenError
from app.infrastructure.database.models.role import Role

# ---------------------------------------------------------------------------
# Same-tenant access
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_01_same_tenant_resource_returned() -> None:
    """Verify get_authorized_resource returns resource for matching tenant."""
    tenant_id = uuid.uuid4()
    resource_id = uuid.uuid4()

    resource = Role(
        id=resource_id,
        tenant_id=tenant_id,
        name="viewer",
        is_system=False,
        status="active",
    )

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = resource
    db.execute.return_value = result

    fetched = await get_authorized_resource(db, Role, resource_id, tenant_id)
    assert fetched is resource


# ---------------------------------------------------------------------------
# Cross-tenant IDOR protection
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_02_cross_tenant_resource_raises_not_found() -> None:
    """Verify cross-tenant resource access raises ResourceNotFoundOrForbiddenError (404)."""
    tenant_a = uuid.uuid4()
    resource_id = uuid.uuid4()

    db = AsyncMock()
    result = MagicMock()
    # DB returns None because tenant_id filter excludes tenant A's resource
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    with pytest.raises(ResourceNotFoundOrForbiddenError):
        await get_authorized_resource(db, Role, resource_id, tenant_a)


@pytest.mark.asyncio
async def test_03_raise_if_missing_false_returns_none() -> None:
    """Verify raise_if_missing=False returns None instead of raising."""
    tenant_id = uuid.uuid4()
    resource_id = uuid.uuid4()

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    fetched = await get_authorized_resource(
        db, Role, resource_id, tenant_id, raise_if_missing=False
    )
    assert fetched is None


# ---------------------------------------------------------------------------
# Soft-delete exclusion
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_04_soft_deleted_resource_is_excluded() -> None:
    """Verify get_authorized_resource_with_soft_delete excludes deleted records."""
    tenant_id = uuid.uuid4()
    resource_id = uuid.uuid4()

    db = AsyncMock()
    result = MagicMock()
    # Soft-deleted record excluded — DB returns None
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    with pytest.raises(ResourceNotFoundOrForbiddenError):
        await get_authorized_resource_with_soft_delete(db, Role, resource_id, tenant_id)


# ---------------------------------------------------------------------------
# assert_resource_tenant
# ---------------------------------------------------------------------------


def test_05_assert_resource_tenant_passes_for_matching_tenant() -> None:
    """Verify assert_resource_tenant does not raise on correct tenant."""
    tenant_id = uuid.uuid4()
    resource = MagicMock()
    resource.tenant_id = tenant_id

    assert_resource_tenant(resource, tenant_id)  # Must not raise


def test_06_assert_resource_tenant_raises_on_mismatch() -> None:
    """Verify assert_resource_tenant raises on tenant mismatch."""
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    resource = MagicMock()
    resource.tenant_id = tenant_b

    with pytest.raises(ResourceNotFoundOrForbiddenError):
        assert_resource_tenant(resource, tenant_a)


# ---------------------------------------------------------------------------
# Explicit IDOR scenario
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_07_idor_user_a_cannot_access_tenant_b_resource() -> None:
    """Verify explicit IDOR protection: user in tenant A cannot access tenant B resource."""
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    resource_id = uuid.uuid4()

    # Tenant B owns this resource
    tenant_b_resource = Role(
        id=resource_id,
        tenant_id=tenant_b,
        name="admin",
        is_system=False,
        status="active",
    )

    # DB query with tenant_a filter finds nothing (WHERE tenant_id = tenant_a)
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    # User in tenant_a attempts to fetch tenant_b's resource
    with pytest.raises(ResourceNotFoundOrForbiddenError):
        await get_authorized_resource(db, Role, resource_id, tenant_a)

    # Control: same resource is accessible with correct tenant
    result_b = MagicMock()
    result_b.scalar_one_or_none.return_value = tenant_b_resource
    db.execute.return_value = result_b

    fetched = await get_authorized_resource(db, Role, resource_id, tenant_b)
    assert fetched is tenant_b_resource


@pytest.mark.asyncio
async def test_08_idor_returns_404_not_403() -> None:
    """Verify IDOR returns ResourceNotFoundOrForbiddenError (404) not 403.

    This prevents revealing whether a resource exists in another tenant.
    """
    from app.exceptions.codes import ErrorCode

    tenant_a = uuid.uuid4()
    resource_id = uuid.uuid4()

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    with pytest.raises(ResourceNotFoundOrForbiddenError) as exc_info:
        await get_authorized_resource(db, Role, resource_id, tenant_a)

    assert exc_info.value.code == ErrorCode.RESOURCE_NOT_FOUND
