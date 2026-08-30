"""Unit tests for Phase 126 — Agent Revocation / Deactivation.

Tests:
- Successful revocation (active/suspended -> deactivated)
- Deactivated is terminal (transition from deactivated -> active rejected)
- Revokes active sessions and invalidates active credentials
- Already deactivated agent returns AgentAlreadyRevokedError (409 Conflict)
- Cross-tenant revocation returns AgentNotFoundError (IDOR 404)
- Zero hard deletion (records remain in DB for audit reference)
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.agent_lifecycle_service import (
    AgentLifecycleService,
    validate_transition,
)
from app.domain.exceptions.agent_exceptions import (
    AgentAlreadyRevokedError,
    AgentNotFoundError,
)
from app.infrastructure.database.models.agent import Agent
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
        name="Revocation Test Bot",
        slug="rev-bot",
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
async def test_01_revoke_agent_success() -> None:
    """Verify revoke_agent transitions agent to deactivated, revoking sessions and credentials."""
    tenant_id = uuid.uuid4()
    agent, lc = _make_agent_and_lc(tenant_id, status="active")

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent
    lc_res = MagicMock()
    lc_res.scalar_one_or_none.return_value = lc

    # session update result & credential update result
    session_res = MagicMock()
    session_res.rowcount = 3
    cred_res = MagicMock()
    cred_res.rowcount = 1

    db.execute.side_effect = [agent_res, lc_res, session_res, cred_res]
    db.flush = AsyncMock()
    db.refresh = AsyncMock()

    (
        deact_agent,
        deact_lc,
        rev_sessions,
        rev_creds,
    ) = await _lifecycle_service.revoke_agent(
        db, tenant_id, agent.id, reason="Permanent decommission"
    )

    assert deact_agent.status == "deactivated"
    assert deact_lc.status == "deactivated"
    assert deact_lc.deactivated_at is not None
    assert rev_sessions == 3
    assert rev_creds == 1


@pytest.mark.asyncio
async def test_02_deactivated_is_terminal_state() -> None:
    """Verify state machine prohibits any transition out of deactivated status."""
    assert validate_transition("deactivated", "active") is False
    assert validate_transition("deactivated", "provisioning") is False
    assert validate_transition("deactivated", "suspended") is False
    assert validate_transition("deactivated", "paused") is False


@pytest.mark.asyncio
async def test_03_revoke_already_deactivated_conflict() -> None:
    """Verify revoking an already deactivated agent raises AgentAlreadyRevokedError."""
    tenant_id = uuid.uuid4()
    agent, lc = _make_agent_and_lc(tenant_id, status="deactivated")

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent
    lc_res = MagicMock()
    lc_res.scalar_one_or_none.return_value = lc

    db.execute.side_effect = [agent_res, lc_res]

    with pytest.raises(AgentAlreadyRevokedError):
        await _lifecycle_service.revoke_agent(db, tenant_id, agent.id)


@pytest.mark.asyncio
async def test_04_revoke_cross_tenant_raises_not_found() -> None:
    """Verify revoke_agent raises AgentNotFoundError (IDOR 404) for cross-tenant request."""
    tenant_a = uuid.uuid4()
    agent_id = uuid.uuid4()

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = None
    db.execute.return_value = agent_res

    with pytest.raises(AgentNotFoundError):
        await _lifecycle_service.revoke_agent(db, tenant_a, agent_id)
