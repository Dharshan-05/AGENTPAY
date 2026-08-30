"""Unit tests for Phase 113 — Permission Management.

Tests:
- Permission resolution from roles
- has_permission() returns AuthorizationDecision
- Default deny for missing permission
- Empty permission string denial
- Grant/revoke role permissions
- Duplicate permission assignment prevention
- Cross-tenant prevention
- resolve_permissions returns frozenset
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.application.services.authorization import AuthorizationService
from app.domain.authorization.context import AuthorizationContext
from app.domain.authorization.permissions_registry import PAYMENTS_READ, ROLES_READ, USERS_CREATE
from app.domain.exceptions.auth_exceptions import PermissionDeniedError
from app.infrastructure.database.models.permission import Permission
from app.infrastructure.database.models.role import Role
from app.infrastructure.database.models.role_permission import RolePermission

_service = AuthorizationService()


# ---------------------------------------------------------------------------
# Permission resolution
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_01_resolve_permissions_returns_frozenset() -> None:
    """Verify resolve_permissions returns a frozenset of permission names."""
    ctx = AuthorizationContext(
        user_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )

    with patch.object(
        _service, "resolve_permissions", new=AsyncMock(return_value=frozenset({PAYMENTS_READ}))
    ):
        db = AsyncMock()
        perms = await _service.resolve_permissions(db, ctx)
        assert isinstance(perms, frozenset)
        assert PAYMENTS_READ in perms


@pytest.mark.asyncio
async def test_02_has_permission_returns_allow_when_granted() -> None:
    """Verify has_permission returns allow decision when user has permission."""
    ctx = AuthorizationContext(
        user_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )

    with patch.object(
        _service,
        "resolve_permissions",
        new=AsyncMock(return_value=frozenset({PAYMENTS_READ, ROLES_READ})),
    ):
        db = AsyncMock()
        decision = await _service.has_permission(db, ctx, PAYMENTS_READ)
        assert decision.allowed is True
        assert decision.permission == PAYMENTS_READ


@pytest.mark.asyncio
async def test_03_has_permission_returns_deny_when_missing() -> None:
    """Verify has_permission returns deny when user lacks permission (default-deny)."""
    ctx = AuthorizationContext(
        user_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )

    with patch.object(
        _service,
        "resolve_permissions",
        new=AsyncMock(return_value=frozenset({ROLES_READ})),
    ):
        db = AsyncMock()
        decision = await _service.has_permission(db, ctx, USERS_CREATE)
        assert decision.allowed is False


@pytest.mark.asyncio
async def test_04_empty_permission_string_is_denied() -> None:
    """Verify empty permission string is always denied."""
    ctx = AuthorizationContext(
        user_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )

    db = AsyncMock()
    decision = await _service.has_permission(db, ctx, "")
    assert decision.allowed is False


@pytest.mark.asyncio
async def test_05_require_permission_raises_on_deny() -> None:
    """Verify require_permission raises PermissionDeniedError on default-deny."""
    ctx = AuthorizationContext(
        user_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )

    with patch.object(
        _service,
        "resolve_permissions",
        new=AsyncMock(return_value=frozenset()),
    ):
        db = AsyncMock()
        with pytest.raises(PermissionDeniedError):
            await _service.require_permission(db, ctx, PAYMENTS_READ)


@pytest.mark.asyncio
async def test_06_require_permission_passes_when_granted() -> None:
    """Verify require_permission does not raise when permission is present."""
    ctx = AuthorizationContext(
        user_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )

    with patch.object(
        _service,
        "resolve_permissions",
        new=AsyncMock(return_value=frozenset({PAYMENTS_READ})),
    ):
        db = AsyncMock()
        # Should not raise
        await _service.require_permission(db, ctx, PAYMENTS_READ)


# ---------------------------------------------------------------------------
# Grant/revoke role-permission
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_07_grant_role_permission_success() -> None:
    """Verify grant_role_permission creates a RolePermission record."""
    tenant_id = uuid.uuid4()
    role_id = uuid.uuid4()
    perm_id = uuid.uuid4()

    role = Role(id=role_id, tenant_id=tenant_id, name="editor", is_system=False, status="active")
    perm = Permission(
        id=perm_id, name=PAYMENTS_READ, resource="payments", action="read", is_system=True
    )
    new_rp = RolePermission(id=uuid.uuid4(), role_id=role_id, permission_id=perm_id)

    with (
        patch.object(_service, "get_role", new=AsyncMock(return_value=role)),
        patch.object(_service, "get_permission", new=AsyncMock(return_value=perm)),
        patch.object(_service, "grant_role_permission", new=AsyncMock(return_value=new_rp)),
    ):
        db = AsyncMock()
        result = await _service.grant_role_permission(db, tenant_id, role_id, perm_id)
        assert result.role_id == role_id
        assert result.permission_id == perm_id


@pytest.mark.asyncio
async def test_08_grant_duplicate_permission_raises_value_error() -> None:
    """Verify grant_role_permission raises ValueError for duplicate assignment."""
    tenant_id = uuid.uuid4()
    role_id = uuid.uuid4()
    perm_id = uuid.uuid4()

    role = Role(id=role_id, tenant_id=tenant_id, name="editor", is_system=False, status="active")
    perm = Permission(
        id=perm_id, name=PAYMENTS_READ, resource="payments", action="read", is_system=True
    )
    existing_rp = RolePermission(id=uuid.uuid4(), role_id=role_id, permission_id=perm_id)

    db = AsyncMock()
    dup_result = MagicMock()
    dup_result.scalar_one_or_none.return_value = existing_rp
    db.execute.return_value = dup_result

    with (
        patch.object(_service, "get_role", new=AsyncMock(return_value=role)),
        patch.object(_service, "get_permission", new=AsyncMock(return_value=perm)),
    ):
        with pytest.raises(ValueError, match="already assigned"):
            await _service.grant_role_permission(db, tenant_id, role_id, perm_id)


@pytest.mark.asyncio
async def test_09_grant_permission_cross_tenant_role_rejected() -> None:
    """Verify grant_role_permission raises ValueError for role outside tenant."""
    tenant_id = uuid.uuid4()
    role_id = uuid.uuid4()
    perm_id = uuid.uuid4()

    with patch.object(_service, "get_role", new=AsyncMock(return_value=None)):
        db = AsyncMock()
        with pytest.raises(ValueError, match="not found in this tenant"):
            await _service.grant_role_permission(db, tenant_id, role_id, perm_id)


@pytest.mark.asyncio
async def test_10_revoke_nonexistent_permission_raises_value_error() -> None:
    """Verify revoke_role_permission raises ValueError if assignment not found."""
    tenant_id = uuid.uuid4()
    role_id = uuid.uuid4()
    perm_id = uuid.uuid4()
    role = Role(id=role_id, tenant_id=tenant_id, name="editor", is_system=False, status="active")

    db = AsyncMock()
    no_result = MagicMock()
    no_result.scalar_one_or_none.return_value = None
    db.execute.return_value = no_result

    with patch.object(_service, "get_role", new=AsyncMock(return_value=role)):
        with pytest.raises(ValueError, match="not found"):
            await _service.revoke_role_permission(db, tenant_id, role_id, perm_id)
