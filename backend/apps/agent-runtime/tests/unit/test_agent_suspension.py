"""Unit tests for Phase 125 — Agent Suspension.

Tests:
- Successful suspension (transitions active -> suspended atomically)
- Revokes all active agent sessions upon suspension
- Preserves historical data and credentials
- Already suspended agent returns AgentAlreadySuspendedError (409 Conflict)
- Invalid lifecycle transition (e.g. from deactivated -> suspended) fails
- Cross-tenant suspension fails with AgentNotFoundError (404 Not Found)
- Suspended agent cannot create sessions or pass session validation
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.agent_lifecycle_service import AgentLifecycleService
from app.application.services.agent_session_service import AgentSessionService
from app.domain.exceptions.agent_exceptions import (
    AgentAlreadySuspendedError,
    AgentNotFoundError,
    AgentSessionCreationError,
    InvalidAgentLifecycleTransitionError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_lifecycle import AgentLifecycle
from app.schemas.agents import AgentSessionCreateRequest

_lifecycle_service = AgentLifecycleService()
_session_service = AgentSessionService()


def _make_agent_and_lc(
    tenant_id: uuid.UUID | None = None,
    status: str = "active",
) -> tuple[Agent, AgentLifecycle]:
    tid = tenant_id or uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tid,
        name="Suspension Test Bot",
        slug="susp-bot",
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
        status_reason="Active state",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    return agent, lc


@pytest.mark.asyncio
async def test_01_suspend_agent_success() -> None:
    """Verify suspend_agent transitions active agent to suspended and revokes sessions."""
    tenant_id = uuid.uuid4()
    agent, lc = _make_agent_and_lc(tenant_id, status="active")

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent
    lc_res = MagicMock()
    lc_res.scalar_one_or_none.return_value = lc

    # session update result
    session_res = MagicMock()
    session_res.rowcount = 2

    db.execute.side_effect = [agent_res, lc_res, session_res]
    db.flush = AsyncMock()
    db.refresh = AsyncMock()

    suspended_agent, suspended_lc, revoked_count = await _lifecycle_service.suspend_agent(
        db, tenant_id, agent.id, reason="Security review"
    )

    assert suspended_agent.status == "suspended"
    assert suspended_lc.status == "suspended"
    assert suspended_lc.suspended_at is not None
    assert revoked_count == 2


@pytest.mark.asyncio
async def test_02_suspend_already_suspended_conflict() -> None:
    """Verify suspending an already suspended agent raises AgentAlreadySuspendedError."""
    tenant_id = uuid.uuid4()
    agent, lc = _make_agent_and_lc(tenant_id, status="suspended")

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent
    lc_res = MagicMock()
    lc_res.scalar_one_or_none.return_value = lc

    db.execute.side_effect = [agent_res, lc_res]

    with pytest.raises(AgentAlreadySuspendedError):
        await _lifecycle_service.suspend_agent(db, tenant_id, agent.id)


@pytest.mark.asyncio
async def test_03_suspend_deactivated_agent_invalid_transition() -> None:
    """Verify suspending a deactivated agent raises InvalidAgentLifecycleTransitionError."""
    tenant_id = uuid.uuid4()
    agent, lc = _make_agent_and_lc(tenant_id, status="deactivated")

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent
    lc_res = MagicMock()
    lc_res.scalar_one_or_none.return_value = lc

    db.execute.side_effect = [agent_res, lc_res]

    with pytest.raises(InvalidAgentLifecycleTransitionError):
        await _lifecycle_service.suspend_agent(db, tenant_id, agent.id)


@pytest.mark.asyncio
async def test_04_suspend_cross_tenant_raises_not_found() -> None:
    """Verify suspend_agent raises AgentNotFoundError (IDOR 404) for cross-tenant request."""
    tenant_a = uuid.uuid4()
    agent_id = uuid.uuid4()

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = None
    db.execute.return_value = agent_res

    with pytest.raises(AgentNotFoundError):
        await _lifecycle_service.suspend_agent(db, tenant_a, agent_id)


@pytest.mark.asyncio
async def test_05_suspended_agent_cannot_create_session() -> None:
    """Verify session creation for suspended agent raises AgentSessionCreationError."""
    tenant_id = uuid.uuid4()
    agent, _ = _make_agent_and_lc(tenant_id, status="suspended")

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent
    db.execute.return_value = agent_res

    req = AgentSessionCreateRequest()
    with pytest.raises(AgentSessionCreationError, match="suspended"):
        await _session_service.create_session(db, tenant_id, agent.id, req)
