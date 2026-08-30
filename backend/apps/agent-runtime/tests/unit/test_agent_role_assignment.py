"""Unit tests for Phase 129 — Agent Role Assignment.

Tests:
- List assigned roles for an agent
- Assign tenant/system role to agent successfully
- Prevent duplicate role assignment (AgentRoleAlreadyAssignedError)
- Prevent assignment of unknown/cross-tenant role (AgentRoleAssignmentError)
- Revoke role from agent
- Revoking non-existent role assignment raises AgentRoleNotFoundError
- IDOR defense: cross-tenant agent role access raises AgentNotFoundError (404)
- Revoking role preserves original Role definition
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.authorization import AuthorizationService
from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    AgentRoleAlreadyAssignedError,
    AgentRoleAssignmentError,
    AgentRoleNotFoundError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_role import AgentRole
from app.infrastructure.database.models.role import Role

_auth_service = AuthorizationService()


def _make_agent(tenant_id: uuid.UUID | None = None) -> Agent:
    tid = tenant_id or uuid.uuid4()
    return Agent(
        id=uuid.uuid4(),
        tenant_id=tid,
        name="Role Test Bot",
        slug="role-bot",
        agent_type="autonomous",
        status="active",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def _make_role(tenant_id: uuid.UUID, name: str = "operator") -> Role:
    return Role(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        name=name,
        description="Operator role",
        is_system=False,
        status="active",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_01_list_agent_roles_success() -> None:
    """Verify listing assigned roles for an agent within tenant."""
    tenant_id = uuid.uuid4()
    agent = _make_agent(tenant_id)
    role = _make_role(tenant_id, "operator")
    ar = AgentRole(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent.id,
        role_id=role.id,
        role=role,
        created_at=datetime.now(UTC),
    )

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent

    ar_res = MagicMock()
    ar_res.scalars.return_value.all.return_value = [ar]

    db.execute.side_effect = [agent_res, ar_res]

    result = await _auth_service.list_agent_roles(db, tenant_id, agent.id)
    assert len(result) == 1
    assert result[0].role_id == role.id


@pytest.mark.asyncio
async def test_02_assign_role_to_agent_success() -> None:
    """Verify assigning a valid role to an agent."""
    tenant_id = uuid.uuid4()
    agent = _make_agent(tenant_id)
    role = _make_role(tenant_id, "operator")

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent

    role_res = MagicMock()
    role_res.scalar_one_or_none.return_value = role

    dup_res = MagicMock()
    dup_res.scalar_one_or_none.return_value = None

    db.execute.side_effect = [agent_res, role_res, dup_res]
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()

    ar = await _auth_service.assign_role_to_agent(db, tenant_id, agent.id, role.id)

    assert ar.agent_id == agent.id
    assert ar.role_id == role.id
    assert ar.tenant_id == tenant_id


@pytest.mark.asyncio
async def test_03_assign_role_duplicate_conflict() -> None:
    """Verify duplicate role assignment raises AgentRoleAlreadyAssignedError."""
    tenant_id = uuid.uuid4()
    agent = _make_agent(tenant_id)
    role = _make_role(tenant_id, "operator")
    existing_ar = AgentRole(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent.id,
        role_id=role.id,
    )

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent

    role_res = MagicMock()
    role_res.scalar_one_or_none.return_value = role

    dup_res = MagicMock()
    dup_res.scalar_one_or_none.return_value = existing_ar

    db.execute.side_effect = [agent_res, role_res, dup_res]

    with pytest.raises(AgentRoleAlreadyAssignedError):
        await _auth_service.assign_role_to_agent(db, tenant_id, agent.id, role.id)


@pytest.mark.asyncio
async def test_04_assign_role_unknown_fails() -> None:
    """Verify assigning non-existent/cross-tenant role raises AgentRoleAssignmentError."""
    tenant_id = uuid.uuid4()
    agent = _make_agent(tenant_id)

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent

    role_res = MagicMock()
    role_res.scalar_one_or_none.return_value = None

    db.execute.side_effect = [agent_res, role_res]

    with pytest.raises(AgentRoleAssignmentError):
        await _auth_service.assign_role_to_agent(db, tenant_id, agent.id, uuid.uuid4())


@pytest.mark.asyncio
async def test_05_revoke_role_from_agent_success() -> None:
    """Verify revoking a role assignment from an agent."""
    tenant_id = uuid.uuid4()
    agent = _make_agent(tenant_id)
    role_id = uuid.uuid4()
    ar = AgentRole(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent.id,
        role_id=role_id,
    )

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent

    ar_res = MagicMock()
    ar_res.scalar_one_or_none.return_value = ar

    db.execute.side_effect = [agent_res, ar_res]
    db.delete = AsyncMock()
    db.flush = AsyncMock()

    await _auth_service.remove_role_from_agent(db, tenant_id, agent.id, role_id)

    db.delete.assert_called_once_with(ar)


@pytest.mark.asyncio
async def test_06_revoke_role_not_found() -> None:
    """Verify revoking a non-existent role assignment raises AgentRoleNotFoundError."""
    tenant_id = uuid.uuid4()
    agent = _make_agent(tenant_id)
    role_id = uuid.uuid4()

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent

    ar_res = MagicMock()
    ar_res.scalar_one_or_none.return_value = None

    db.execute.side_effect = [agent_res, ar_res]

    with pytest.raises(AgentRoleNotFoundError):
        await _auth_service.remove_role_from_agent(db, tenant_id, agent.id, role_id)


@pytest.mark.asyncio
async def test_07_agent_role_cross_tenant_idor_not_found() -> None:
    """Verify cross-tenant agent role operations raise AgentNotFoundError (404)."""
    tenant_a = uuid.uuid4()
    agent_id = uuid.uuid4()

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = None
    db.execute.return_value = agent_res

    with pytest.raises(AgentNotFoundError):
        await _auth_service.list_agent_roles(db, tenant_a, agent_id)


@pytest.mark.asyncio
async def test_08_revoking_role_preserves_role_definition() -> None:
    """Verify removing agent role deletes AgentRole link without modifying Role entity."""
    tenant_id = uuid.uuid4()
    agent = _make_agent(tenant_id)
    role = _make_role(tenant_id, "operator")
    ar = AgentRole(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent.id,
        role_id=role.id,
    )

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent

    ar_res = MagicMock()
    ar_res.scalar_one_or_none.return_value = ar

    db.execute.side_effect = [agent_res, ar_res]
    db.delete = AsyncMock()
    db.flush = AsyncMock()

    await _auth_service.remove_role_from_agent(db, tenant_id, agent.id, role.id)

    assert role.name == "operator"
    assert role.deleted_at is None
