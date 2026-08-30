"""Unit & Security tests for Phase 136 — Agent Behaviour Deviation."""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_behaviour_deviation_service import (
    AgentBehaviourDeviationService,
)
from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.behaviour_event import BehaviourEvent


@pytest.mark.asyncio
async def test_calculate_deviation_normal_activity(db_session: AsyncSession) -> None:
    """Test behaviour deviation calculation under normal baseline conditions."""
    service = AgentBehaviourDeviationService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Deviation Test Agent",
        slug="dev-test-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    res = await service.calculate_deviation(db_session, tenant_id, agent_id)

    assert res.agent_id == agent_id
    assert res.tenant_id == tenant_id
    assert res.deviation_type == "frequency"
    assert res.severity == "low"
    assert res.deviation_score == Decimal("0.00")


@pytest.mark.asyncio
async def test_calculate_deviation_high_frequency_burst(db_session: AsyncSession) -> None:
    """Test behaviour deviation detection when recent event frequency spikes."""
    service = AgentBehaviourDeviationService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Spike Agent",
        slug="spike-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)

    # Insert 100 recent events
    for i in range(100):
        evt = BehaviourEvent(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            event_reference=f"ref-{uuid.uuid4().hex[:8]}",
            event_type="agent",
            event_action="executed",
            event_result="success",
            sequence_number=i,
        )
        db_session.add(evt)
    await db_session.flush()

    res = await service.calculate_deviation(db_session, tenant_id, agent_id)

    assert res.deviation_score > Decimal("0.00")
    assert res.severity in ("medium", "high")
    assert "exceeded" in res.reason.lower()


@pytest.mark.asyncio
async def test_behaviour_deviation_cross_tenant_idor_rejected(
    db_session: AsyncSession,
) -> None:
    """Test cross-tenant access to behaviour deviation fails with AgentNotFoundError (404)."""
    service = AgentBehaviourDeviationService()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_a,
        name="Tenant A Agent",
        slug="tenant-a-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    with pytest.raises(AgentNotFoundError):
        await service.calculate_deviation(db_session, tenant_b, agent_id)
