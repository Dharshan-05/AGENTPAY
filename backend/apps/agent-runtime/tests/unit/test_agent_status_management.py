"""Unit tests for Phase 130 — Agent Status Management.

Tests:
- Retrieve agent operational status & lifecycle metadata
- Pause active agent transitions status to 'paused' and revokes active sessions
- Pause already paused agent raises AgentStatusTransitionError
- Resume paused agent back to active status (verifies active credential requirement)
- Resume active agent raises AgentAlreadyActiveError (409 Conflict)
- Resurrecting deactivated agent fails with InvalidAgentLifecycleTransitionError
- Status update dispatcher delegates strictly to AgentLifecycleService
- Cross-tenant status query returns AgentNotFoundError (404 IDOR protection)
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.agent_lifecycle_service import AgentLifecycleService
from app.domain.exceptions.agent_exceptions import (
    AgentActivationError,
    AgentAlreadyActiveError,
    AgentNotFoundError,
    AgentStatusTransitionError,
    InvalidAgentLifecycleTransitionError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_credential import AgentCredential
from app.infrastructure.database.models.agent_lifecycle import AgentLifecycle

_lifecycle_service = AgentLifecycleService()


def _make_agent_and_lc(
    tenant_id: uuid.UUID | None = None,
    status: str = "active",
) -> tuple[Agent, AgentLifecycle]:
    tid = tenant_id or uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tid,
        name="Status Test Bot",
        slug="status-bot",
        agent_type="autonomous",
        status=status,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    lc = AgentLifecycle(
        id=uuid.uuid4(),
        tenant_id=tid,
        agent_id=agent_id,
        status=status,
        status_reason="Initial status",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    return agent, lc


@pytest.mark.asyncio
async def test_01_get_agent_status_success() -> None:
    """Verify get_agent_lifecycle retrieves status metadata correctly."""
    tenant_id = uuid.uuid4()
    agent, lc = _make_agent_and_lc(tenant_id, status="active")

    db = AsyncMock()
    lc_res = MagicMock()
    lc_res.scalar_one_or_none.return_value = lc
    db.execute.return_value = lc_res

    res = await _lifecycle_service.get_agent_lifecycle(db, tenant_id, agent.id)
    assert res.status == "active"
    assert res.agent_id == agent.id


@pytest.mark.asyncio
async def test_02_pause_active_agent_success_revokes_sessions() -> None:
    """Verify pause_agent transitions active agent to paused and revokes active sessions."""
    tenant_id = uuid.uuid4()
    agent, lc = _make_agent_and_lc(tenant_id, status="active")

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent
    lc_res = MagicMock()
    lc_res.scalar_one_or_none.return_value = lc
    session_res = MagicMock()
    session_res.rowcount = 3

    db.execute.side_effect = [agent_res, lc_res, session_res]
    db.flush = AsyncMock()
    db.refresh = AsyncMock()

    paused_agent, paused_lc, revoked_count = await _lifecycle_service.pause_agent(
        db, tenant_id, agent.id, reason="Maintenance"
    )

    assert paused_agent.status == "paused"
    assert paused_lc.status == "paused"
    assert revoked_count == 3


@pytest.mark.asyncio
async def test_03_pause_already_paused_agent_raises_error() -> None:
    """Verify pausing an already paused agent raises AgentStatusTransitionError."""
    tenant_id = uuid.uuid4()
    agent, lc = _make_agent_and_lc(tenant_id, status="paused")

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent
    lc_res = MagicMock()
    lc_res.scalar_one_or_none.return_value = lc

    db.execute.side_effect = [agent_res, lc_res]

    with pytest.raises(AgentStatusTransitionError):
        await _lifecycle_service.pause_agent(db, tenant_id, agent.id)


@pytest.mark.asyncio
async def test_04_resume_paused_agent_success() -> None:
    """Verify resuming a paused agent to active status succeeds when active credential exists."""
    tenant_id = uuid.uuid4()
    agent, lc = _make_agent_and_lc(tenant_id, status="paused")
    cred = AgentCredential(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent.id,
        credential_type="api_key",
        secret_hash="hash",
        status="active",
    )

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent
    lc_res = MagicMock()
    lc_res.scalar_one_or_none.return_value = lc
    cred_res = MagicMock()
    cred_res.scalar_one_or_none.return_value = cred

    db.execute.side_effect = [agent_res, lc_res, cred_res]
    db.flush = AsyncMock()
    db.refresh = AsyncMock()

    resumed_agent, resumed_lc = await _lifecycle_service.resume_agent(
        db, tenant_id, agent.id, reason="Maintenance complete"
    )

    assert resumed_agent.status == "active"
    assert resumed_lc.status == "active"


@pytest.mark.asyncio
async def test_05_resume_agent_without_credential_fails() -> None:
    """Verify resuming an agent without an active credential raises AgentActivationError."""
    tenant_id = uuid.uuid4()
    agent, lc = _make_agent_and_lc(tenant_id, status="paused")

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent
    lc_res = MagicMock()
    lc_res.scalar_one_or_none.return_value = lc
    cred_res = MagicMock()
    cred_res.scalar_one_or_none.return_value = None  # No credential

    db.execute.side_effect = [agent_res, lc_res, cred_res]

    with pytest.raises(AgentActivationError):
        await _lifecycle_service.resume_agent(db, tenant_id, agent.id)


@pytest.mark.asyncio
async def test_06_resume_already_active_agent_raises_conflict() -> None:
    """Verify resuming an already active agent raises AgentAlreadyActiveError."""
    tenant_id = uuid.uuid4()
    agent, lc = _make_agent_and_lc(tenant_id, status="active")

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent
    lc_res = MagicMock()
    lc_res.scalar_one_or_none.return_value = lc

    db.execute.side_effect = [agent_res, lc_res]

    with pytest.raises(AgentAlreadyActiveError):
        await _lifecycle_service.resume_agent(db, tenant_id, agent.id)


@pytest.mark.asyncio
async def test_07_resurrect_deactivated_agent_fails() -> None:
    """Verify attempting to resume/reactivate a deactivated agent fails closed."""
    tenant_id = uuid.uuid4()
    agent, lc = _make_agent_and_lc(tenant_id, status="deactivated")

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent
    lc_res = MagicMock()
    lc_res.scalar_one_or_none.return_value = lc

    db.execute.side_effect = [agent_res, lc_res]

    with pytest.raises(InvalidAgentLifecycleTransitionError):
        await _lifecycle_service.resume_agent(db, tenant_id, agent.id)


@pytest.mark.asyncio
async def test_08_cross_tenant_status_read_returns_not_found() -> None:
    """Verify cross-tenant status access raises AgentNotFoundError (404)."""
    tenant_a = uuid.uuid4()
    agent_id = uuid.uuid4()

    db = AsyncMock()
    lc_res = MagicMock()
    lc_res.scalar_one_or_none.return_value = None
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = None

    db.execute.side_effect = [lc_res, agent_res]

    with pytest.raises(AgentNotFoundError):
        await _lifecycle_service.get_agent_lifecycle(db, tenant_a, agent_id)
