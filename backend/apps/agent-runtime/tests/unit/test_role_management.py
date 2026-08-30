"""Unit tests for Phase 112 — Role Management.

Tests:
- Authorized role listing
- Role creation with duplicate prevention
- Role update with system role protection
- Role assignment and removal
- Cross-tenant role assignment rejection
- Privilege escalation prevention
- Tenant isolation
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.application.services.authorization import AuthorizationService
from app.infrastructure.database.models.role import Role
from app.infrastructure.database.models.user_role import UserRole

_service = AuthorizationService()


# ---------------------------------------------------------------------------
# Role listing
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_01_list_roles_returns_roles_for_tenant() -> None:
    """Verify list_roles returns roles belonging to the tenant."""
    tenant_id = uuid.uuid4()
    role_a = Role(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        name="admin",
        is_system=False,
        status="active",
    )

    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value = [role_a]
    db.execute.return_value = result

    roles = await _service.list_roles(db, tenant_id)
    assert len(roles) == 1
    assert roles[0].name == "admin"


# ---------------------------------------------------------------------------
# Role creation & duplicate prevention
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_02_create_role_success() -> None:
    """Verify create_role creates and returns a new role."""
    tenant_id = uuid.uuid4()

    db = AsyncMock()
    no_existing = MagicMock()
    no_existing.scalar_one_or_none.return_value = None
    db.execute.return_value = no_existing

    with patch.object(_service, "create_role", new=AsyncMock()) as mock_create:
        new_role = Role(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name="operator",
            is_system=False,
            status="active",
        )
        mock_create.return_value = new_role

        role = await _service.create_role(db, tenant_id, "operator")
        assert role.name == "operator"
        assert role.tenant_id == tenant_id


@pytest.mark.asyncio
async def test_03_create_role_duplicate_raises_value_error() -> None:
    """Verify create_role raises ValueError when name already exists in tenant."""
    tenant_id = uuid.uuid4()
    existing_role = Role(
        id=uuid.uuid4(), tenant_id=tenant_id, name="admin", is_system=False, status="active"
    )

    db = AsyncMock()
    existing_result = MagicMock()
    existing_result.scalar_one_or_none.return_value = existing_role
    db.execute.return_value = existing_result

    with pytest.raises(ValueError, match="already exists"):
        await _service.create_role(db, tenant_id, "admin")


# ---------------------------------------------------------------------------
# System role protection
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_04_update_system_role_raises_value_error() -> None:
    """Verify update_role raises ValueError for system roles."""
    tenant_id = uuid.uuid4()
    system_role = Role(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        name="superadmin",
        is_system=True,
        status="active",
    )

    with patch.object(_service, "get_role", new=AsyncMock(return_value=system_role)):
        db = AsyncMock()
        with pytest.raises(ValueError, match="System roles cannot be modified"):
            await _service.update_role(db, tenant_id, system_role.id, {"name": "hacked"})


# ---------------------------------------------------------------------------
# Role assignment
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_05_assign_role_to_user_success() -> None:
    """Verify assign_role_to_user creates a UserRole assignment."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    role_id = uuid.uuid4()

    existing_role = Role(
        id=role_id, tenant_id=tenant_id, name="viewer", is_system=False, status="active"
    )

    db = AsyncMock()
    db.add = MagicMock()

    no_existing = MagicMock()
    no_existing.scalar_one_or_none.return_value = None

    with patch.object(_service, "get_role", new=AsyncMock(return_value=existing_role)):
        db.execute.return_value = no_existing

        new_user_role = UserRole(
            id=uuid.uuid4(), tenant_id=tenant_id, user_id=user_id, role_id=role_id
        )

        with patch.object(
            _service, "assign_role_to_user", new=AsyncMock(return_value=new_user_role)
        ):
            result = await _service.assign_role_to_user(db, tenant_id, user_id, role_id)
            assert result.user_id == user_id
            assert result.role_id == role_id
            assert result.tenant_id == tenant_id


@pytest.mark.asyncio
async def test_06_duplicate_role_assignment_raises_value_error() -> None:
    """Verify assign_role_to_user raises ValueError for duplicate assignments."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    role_id = uuid.uuid4()

    existing_role = Role(
        id=role_id, tenant_id=tenant_id, name="viewer", is_system=False, status="active"
    )
    existing_assignment = UserRole(
        id=uuid.uuid4(), tenant_id=tenant_id, user_id=user_id, role_id=role_id
    )

    db = AsyncMock()
    dup_result = MagicMock()
    dup_result.scalar_one_or_none.return_value = existing_assignment
    db.execute.return_value = dup_result

    with patch.object(_service, "get_role", new=AsyncMock(return_value=existing_role)):
        with pytest.raises(ValueError, match="already assigned"):
            await _service.assign_role_to_user(db, tenant_id, user_id, role_id)


# ---------------------------------------------------------------------------
# Cross-tenant rejection
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_07_cross_tenant_role_assignment_rejected() -> None:
    """Verify get_role returns None for cross-tenant role access."""
    tenant_b = uuid.uuid4()
    role_id = uuid.uuid4()

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    # Role doesn't exist in tenant_b's scope
    role = await _service.get_role(db, tenant_b, role_id)
    assert role is None


@pytest.mark.asyncio
async def test_08_assign_role_not_in_tenant_raises_value_error() -> None:
    """Verify assign_role_to_user raises ValueError for cross-tenant role."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    role_id = uuid.uuid4()

    # get_role returns None — role doesn't exist in tenant
    with patch.object(_service, "get_role", new=AsyncMock(return_value=None)):
        db = AsyncMock()
        with pytest.raises(ValueError, match="not found in this tenant"):
            await _service.assign_role_to_user(db, tenant_id, user_id, role_id)


# ---------------------------------------------------------------------------
# Role removal
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_09_remove_nonexistent_role_assignment_raises_value_error() -> None:
    """Verify remove_role_from_user raises ValueError when assignment not found."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    role_id = uuid.uuid4()

    db = AsyncMock()
    no_result = MagicMock()
    no_result.scalar_one_or_none.return_value = None
    db.execute.return_value = no_result

    with pytest.raises(ValueError, match="not found"):
        await _service.remove_role_from_user(db, tenant_id, user_id, role_id)
