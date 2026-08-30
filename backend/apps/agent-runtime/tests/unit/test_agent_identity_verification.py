"""Unit and Security Tests for Agent Identity Verification Subsystem (Phase 182)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.agent_identity_verification_service import (
    AgentIdentityVerificationService,
)
from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent


@pytest.fixture
def service() -> AgentIdentityVerificationService:
    return AgentIdentityVerificationService()


@pytest.mark.asyncio
async def test_01_verify_active_agent_success(
    service: AgentIdentityVerificationService,
) -> None:
    """1. Test successful identity verification for an active agent."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Test Agent",
        slug="test-agent",
        agent_type="autonomous",
        status="active",
    )

    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none.return_value = agent

    res = await service.verify_agent_identity(mock_db, tenant_id, agent_id)
    assert res.verified is True
    assert res.agent_id == agent_id
    assert res.tenant_id == tenant_id
    assert res.agent_status == "active"


@pytest.mark.asyncio
async def test_02_unknown_agent_fails_closed_404(
    service: AgentIdentityVerificationService,
) -> None:
    """2. Test unknown or cross-tenant agent raises AgentNotFoundError (anti-enumeration 404)."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    with pytest.raises(AgentNotFoundError):
        await service.verify_agent_identity(mock_db, tenant_id, agent_id)


@pytest.mark.asyncio
async def test_03_inactive_or_suspended_agent_rejected(
    service: AgentIdentityVerificationService,
) -> None:
    """3. Test paused or suspended agent fails verification."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Suspended Agent",
        slug="suspended-agent",
        agent_type="autonomous",
        status="suspended",
    )

    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none.return_value = agent

    res = await service.verify_agent_identity(mock_db, tenant_id, agent_id)
    assert res.verified is False
    assert res.agent_status == "suspended"
    assert "not active" in res.verification_reason
