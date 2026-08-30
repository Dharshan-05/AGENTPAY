"""Unit tests for Phase 123 — Agent Lifecycle Service.

Tests:
- State machine transition validation rules
- Legal state transitions (provisioning -> active)
- Illegal state transitions rejected
- Get agent lifecycle (tenant-scoped)
- Cross-tenant lifecycle lookup raises AgentNotFoundError (IDOR 404)
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.agent_lifecycle_service import (
    AgentLifecycleService,
    validate_transition,
)
from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent_lifecycle import AgentLifecycle

_lifecycle_service = AgentLifecycleService()


def test_01_state_machine_transition_rules() -> None:
    """Verify state machine transition logic for allowed and disallowed transitions."""
    # Legal transitions
    assert validate_transition("provisioning", "active") is True
    assert validate_transition("active", "paused") is True
    assert validate_transition("active", "suspended") is True
    assert validate_transition("active", "deactivated") is True
    assert validate_transition("paused", "active") is True

    # Illegal transitions
    assert validate_transition("active", "provisioning") is False
    assert validate_transition("deactivated", "active") is False
    assert validate_transition("deactivated", "provisioning") is False
    assert validate_transition("invalid_state", "active") is False


@pytest.mark.asyncio
async def test_02_get_agent_lifecycle_existing() -> None:
    """Verify get_agent_lifecycle returns existing lifecycle record for agent in tenant."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_lc = AgentLifecycle(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent_id,
        status="provisioning",
        status_reason="Initial state",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = mock_lc
    db.execute.return_value = result

    lc = await _lifecycle_service.get_agent_lifecycle(db, tenant_id, agent_id)
    assert lc.agent_id == agent_id
    assert lc.status == "provisioning"


@pytest.mark.asyncio
async def test_03_get_agent_lifecycle_cross_tenant_raises_not_found() -> None:
    """Verify get_agent_lifecycle raises AgentNotFoundError for cross-tenant access."""
    tenant_a = uuid.uuid4()
    agent_id = uuid.uuid4()

    db = AsyncMock()
    # Mock no lifecycle and no agent in tenant_a
    result_lc = MagicMock()
    result_lc.scalar_one_or_none.return_value = None
    result_agent = MagicMock()
    result_agent.scalar_one_or_none.return_value = None

    db.execute.side_effect = [result_lc, result_agent]

    with pytest.raises(AgentNotFoundError):
        await _lifecycle_service.get_agent_lifecycle(db, tenant_a, agent_id)
