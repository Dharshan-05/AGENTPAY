"""Unit & Security tests for Phase 134 — Agent Trust Data."""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_trust_service import AgentTrustService
from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    InvalidAgentTrustScoreError,
)
from app.infrastructure.database.models.agent import Agent


@pytest.mark.asyncio
async def test_get_agent_trust_success(db_session: AsyncSession) -> None:
    """Test retrieving agent trust posture data."""
    service = AgentTrustService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Trust Agent",
        slug="trust-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    trust = await service.get_agent_trust(db_session, tenant_id, agent_id)
    assert trust is not None
    assert trust.agent_id == agent_id
    assert trust.tenant_id == tenant_id
    assert trust.trust_status == "unknown"


@pytest.mark.asyncio
async def test_update_agent_trust_success(db_session: AsyncSession) -> None:
    """Test controlled administrative update of agent trust score and status."""
    service = AgentTrustService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Trust Agent 2",
        slug="trust-agent-2",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    updated = await service.update_agent_trust(
        db_session,
        tenant_id,
        agent_id,
        trust_status="high",
        trust_score=Decimal("95.50"),
        trust_reason="Verified security compliance audit passed",
    )

    assert updated.trust_status == "high"
    assert updated.trust_score == Decimal("95.50")
    assert updated.trust_reason == "Verified security compliance audit passed"
    assert updated.evaluated_at is not None


@pytest.mark.asyncio
async def test_update_agent_trust_invalid_score_rejected(db_session: AsyncSession) -> None:
    """Test that out-of-range trust score (< 0 or > 100) raises InvalidAgentTrustScoreError."""
    service = AgentTrustService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Trust Agent 3",
        slug="trust-agent-3",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    with pytest.raises(InvalidAgentTrustScoreError):
        await service.update_agent_trust(
            db_session, tenant_id, agent_id, trust_score=Decimal("105.00")
        )

    with pytest.raises(InvalidAgentTrustScoreError):
        await service.update_agent_trust(
            db_session, tenant_id, agent_id, trust_score=Decimal("-5.00")
        )


@pytest.mark.asyncio
async def test_agent_trust_cross_tenant_idor_rejected(db_session: AsyncSession) -> None:
    """Test cross-tenant access to trust data fails with AgentNotFoundError (404)."""
    service = AgentTrustService()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_a,
        name="Tenant A Trust Agent",
        slug="tenant-a-trust-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    with pytest.raises(AgentNotFoundError):
        await service.get_agent_trust(db_session, tenant_b, agent_id)
