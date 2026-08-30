"""Unit tests for Phase 124 — Agent Activation.

Tests:
- Successful agent activation (transitions provisioning -> active atomically)
- Agent activation requires an active credential (fails with AgentActivationError if none)
- Activation of already active agent fails (AgentAlreadyActiveError -> 409 Conflict)
- Activation from invalid state fails (InvalidAgentLifecycleTransitionError)
- Cross-tenant activation fails with AgentNotFoundError (IDOR 404)
- Safe response serialization (AgentActivationResponse)
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
    InvalidAgentLifecycleTransitionError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_credential import AgentCredential
from app.infrastructure.database.models.agent_lifecycle import AgentLifecycle
from app.schemas.agents import AgentActivationResponse

_lifecycle_service = AgentLifecycleService()


def _make_agent_and_lc(
    tenant_id: uuid.UUID | None = None,
    status: str = "provisioning",
) -> tuple[Agent, AgentLifecycle]:
    tid = tenant_id or uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tid,
        name="Activation Test Bot",
        slug="act-bot",
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
        status_reason="Initial provisioning",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    return agent, lc


@pytest.mark.asyncio
async def test_01_activate_agent_success() -> None:
    """Verify activate_agent transitions agent to active when active credential exists."""
    tenant_id = uuid.uuid4()
    agent, lc = _make_agent_and_lc(tenant_id, status="provisioning")

    mock_cred = MagicMock(spec=AgentCredential)
    mock_cred.status = "active"

    db = AsyncMock()
    # 1. Agent query result
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent
    # 2. Lifecycle query result
    lc_res = MagicMock()
    lc_res.scalar_one_or_none.return_value = lc
    # 3. Credential query result
    cred_res = MagicMock()
    cred_res.scalar_one_or_none.return_value = mock_cred

    db.execute.side_effect = [agent_res, lc_res, cred_res]
    db.flush = AsyncMock()
    db.refresh = AsyncMock()

    activated_agent, activated_lc = await _lifecycle_service.activate_agent(
        db, tenant_id, agent.id, reason="Approved for production"
    )

    assert activated_agent.status == "active"
    assert activated_lc.status == "active"
    assert activated_lc.activated_at is not None


@pytest.mark.asyncio
async def test_02_activate_agent_without_credential_fails() -> None:
    """Verify activate_agent raises AgentActivationError if no active credential exists."""
    tenant_id = uuid.uuid4()
    agent, lc = _make_agent_and_lc(tenant_id, status="provisioning")

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent
    lc_res = MagicMock()
    lc_res.scalar_one_or_none.return_value = lc
    cred_res = MagicMock()
    cred_res.scalar_one_or_none.return_value = None  # No credential

    db.execute.side_effect = [agent_res, lc_res, cred_res]

    with pytest.raises(AgentActivationError, match="without an active credential"):
        await _lifecycle_service.activate_agent(db, tenant_id, agent.id)


@pytest.mark.asyncio
async def test_03_activate_already_active_agent_conflict() -> None:
    """Verify activate_agent raises AgentAlreadyActiveError if agent is already active."""
    tenant_id = uuid.uuid4()
    agent, lc = _make_agent_and_lc(tenant_id, status="active")

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent
    lc_res = MagicMock()
    lc_res.scalar_one_or_none.return_value = lc

    db.execute.side_effect = [agent_res, lc_res]

    with pytest.raises(AgentAlreadyActiveError):
        await _lifecycle_service.activate_agent(db, tenant_id, agent.id)


@pytest.mark.asyncio
async def test_04_activate_deactivated_agent_invalid_transition() -> None:
    """Verify activating a deactivated agent raises InvalidAgentLifecycleTransitionError."""
    tenant_id = uuid.uuid4()
    agent, lc = _make_agent_and_lc(tenant_id, status="deactivated")

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = agent
    lc_res = MagicMock()
    lc_res.scalar_one_or_none.return_value = lc

    db.execute.side_effect = [agent_res, lc_res]

    with pytest.raises(InvalidAgentLifecycleTransitionError):
        await _lifecycle_service.activate_agent(db, tenant_id, agent.id)


@pytest.mark.asyncio
async def test_05_activate_cross_tenant_raises_not_found() -> None:
    """Verify activate_agent raises AgentNotFoundError (IDOR 404) for cross-tenant request."""
    tenant_a = uuid.uuid4()
    agent_id = uuid.uuid4()

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = None
    db.execute.return_value = agent_res

    with pytest.raises(AgentNotFoundError):
        await _lifecycle_service.activate_agent(db, tenant_a, agent_id)


def test_06_activation_response_safe_serialization() -> None:
    """Verify AgentActivationResponse contains zero secret or credential fields."""
    fields = set(AgentActivationResponse.model_fields.keys())
    forbidden = {"secret", "raw_secret", "secret_hash", "private_key", "password"}
    assert forbidden.isdisjoint(fields)
