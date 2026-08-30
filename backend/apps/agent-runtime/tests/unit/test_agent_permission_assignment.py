"""Unit tests for Phase 128 — Agent Permission Assignment.

Tests:
- List direct permissions assigned to agent
- Assign permission to agent successfully
- Prevent duplicate permission assignment (AgentPermissionAlreadyAssignedError)
- Prevent assignment of unknown or unregistered permission (AgentPermissionAssignmentError)
- Revoke direct permission from agent
- Revoke non-existent permission assignment raises AgentPermissionNotFoundError
- IDOR defense: cross-tenant agent permission access raises AgentNotFoundError (404)
- Effective permission resolution combines direct and role-inherited permissions
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.authorization import AuthorizationService
from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    AgentPermissionAlreadyAssignedError,
    AgentPermissionAssignmentError,
    AgentPermissionNotFoundError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_permission import AgentPermission
from app.infrastructure.database.models.permission import Permission

_auth_service = AuthorizationService()


def _make_agent(tenant_id: uuid.UUID | None = None) -> Agent:
    tid = tenant_id or uuid.uuid4()
    return Agent(
        id=uuid.uuid4(),
        tenant_id=tid,
        name="Permission Test Bot",
        slug="perm-bot",
        agent_type="autonomous",
        status="active",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def _make_permission(name: str = "payments:read") -> Permission:
    return Permission(
        id=uuid.uuid4(),
        name=name,
        resource=name.split(":")[0],
        action=name.split(":")[1],
        is_system=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_01_list_agent_permissions_success() -> None:
    """Verify listing assigned permissions for an agent within tenant."""
    tenant_id = uuid.uuid4()
    agent = _make_agent(tenant_id)
    perm = _make_permission("payments:read")
    ap = AgentPermission(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent.id,
        permission_id=perm.id,
        permission=perm,
        created_at=datetime.now(UTC),
    )

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent

    ap_res = MagicMock()
    ap_res.scalars.return_value.all.return_value = [ap]

    db.execute.side_effect = [agent_res, ap_res]

    result = await _auth_service.list_agent_permissions(db, tenant_id, agent.id)
    assert len(result) == 1
    assert result[0].permission_id == perm.id


@pytest.mark.asyncio
async def test_02_assign_permission_to_agent_success() -> None:
    """Verify assigning a canonical permission to an agent."""
    tenant_id = uuid.uuid4()
    agent = _make_agent(tenant_id)
    perm = _make_permission("payments:read")

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent

    perm_res = MagicMock()
    perm_res.scalar_one_or_none.return_value = perm

    dup_res = MagicMock()
    dup_res.scalar_one_or_none.return_value = None

    db.execute.side_effect = [agent_res, perm_res, dup_res]
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()

    ap = await _auth_service.assign_permission_to_agent(db, tenant_id, agent.id, perm.id)

    assert ap.agent_id == agent.id
    assert ap.permission_id == perm.id
    assert ap.tenant_id == tenant_id


@pytest.mark.asyncio
async def test_03_assign_permission_duplicate_conflict() -> None:
    """Verify duplicate permission assignment raises AgentPermissionAlreadyAssignedError."""
    tenant_id = uuid.uuid4()
    agent = _make_agent(tenant_id)
    perm = _make_permission("payments:read")
    existing_ap = AgentPermission(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent.id,
        permission_id=perm.id,
    )

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent

    perm_res = MagicMock()
    perm_res.scalar_one_or_none.return_value = perm

    dup_res = MagicMock()
    dup_res.scalar_one_or_none.return_value = existing_ap

    db.execute.side_effect = [agent_res, perm_res, dup_res]

    with pytest.raises(AgentPermissionAlreadyAssignedError):
        await _auth_service.assign_permission_to_agent(db, tenant_id, agent.id, perm.id)


@pytest.mark.asyncio
async def test_04_assign_permission_unknown_or_unregistered_fails() -> None:
    """Verify assigning unknown/unregistered permission raises AgentPermissionAssignmentError."""
    tenant_id = uuid.uuid4()
    agent = _make_agent(tenant_id)

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent

    perm_res = MagicMock()
    perm_res.scalar_one_or_none.return_value = None  # Not found

    db.execute.side_effect = [agent_res, perm_res]

    with pytest.raises(AgentPermissionAssignmentError):
        await _auth_service.assign_permission_to_agent(db, tenant_id, agent.id, uuid.uuid4())


@pytest.mark.asyncio
async def test_05_revoke_permission_from_agent_success() -> None:
    """Verify revoking a permission assignment from an agent."""
    tenant_id = uuid.uuid4()
    agent = _make_agent(tenant_id)
    perm_id = uuid.uuid4()
    ap = AgentPermission(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent.id,
        permission_id=perm_id,
    )

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent

    ap_res = MagicMock()
    ap_res.scalar_one_or_none.return_value = ap

    db.execute.side_effect = [agent_res, ap_res]
    db.delete = AsyncMock()
    db.flush = AsyncMock()

    await _auth_service.revoke_permission_from_agent(db, tenant_id, agent.id, perm_id)

    db.delete.assert_called_once_with(ap)


@pytest.mark.asyncio
async def test_06_revoke_permission_not_found() -> None:
    """Verify revoking a non-existent permission raises AgentPermissionNotFoundError."""
    tenant_id = uuid.uuid4()
    agent = _make_agent(tenant_id)
    perm_id = uuid.uuid4()

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent

    ap_res = MagicMock()
    ap_res.scalar_one_or_none.return_value = None

    db.execute.side_effect = [agent_res, ap_res]

    with pytest.raises(AgentPermissionNotFoundError):
        await _auth_service.revoke_permission_from_agent(db, tenant_id, agent.id, perm_id)


@pytest.mark.asyncio
async def test_07_agent_permission_cross_tenant_idor_not_found() -> None:
    """Verify cross-tenant agent permission operations raise AgentNotFoundError (404)."""
    tenant_a = uuid.uuid4()
    agent_id = uuid.uuid4()

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = None
    db.execute.return_value = agent_res

    with pytest.raises(AgentNotFoundError):
        await _auth_service.list_agent_permissions(db, tenant_a, agent_id)


@pytest.mark.asyncio
async def test_08_effective_permissions_includes_direct_and_role_inherited() -> None:
    """Verify resolve_agent_permissions returns union of direct and inherited permissions."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    db = AsyncMock()
    direct_res = MagicMock()
    direct_res.scalars.return_value.all.return_value = ["payments:read"]

    inherited_res = MagicMock()
    inherited_res.scalars.return_value.all.return_value = ["transactions:read"]

    db.execute.side_effect = [direct_res, inherited_res]

    perms = await _auth_service.resolve_agent_permissions(db, tenant_id, agent_id)
    assert perms == frozenset({"payments:read", "transactions:read"})
