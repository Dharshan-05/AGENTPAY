"""Unit & Security tests for Phase 137 — Agent Velocity Detection."""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_velocity_detection_service import AgentVelocityDetectionService
from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.commerce_transaction import CommerceTransaction


@pytest.mark.asyncio
async def test_velocity_detection_zero_activity(db_session: AsyncSession) -> None:
    """Test velocity detection with empty activity window."""
    service = AgentVelocityDetectionService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Zero Vel Agent",
        slug="zero-vel-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    res = await service.detect_velocity(db_session, tenant_id, agent_id, window="24h")

    assert res.observed_count == 0
    assert res.observed_amount == Decimal("0.00")
    assert res.velocity_score == Decimal("0.00")
    assert res.severity == "low"


@pytest.mark.asyncio
async def test_velocity_detection_threshold_exceeded(db_session: AsyncSession) -> None:
    """Test velocity detection when transactions exceed defined count and amount thresholds."""
    service = AgentVelocityDetectionService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="High Vel Agent",
        slug="high-vel-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)

    # Create 10 transactions exceeding custom threshold of 5
    for _i in range(10):
        tx = CommerceTransaction(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            merchant_id=merchant_id,
            product_id=uuid.uuid4(),
            transaction_reference=f"tx-{uuid.uuid4().hex[:8]}",
            transaction_type="purchase",
            status="completed",
            quantity=1,
            amount=Decimal("100.00"),
            subtotal=Decimal("100.00"),
            total_amount=Decimal("100.00"),
        )
        db_session.add(tx)
    await db_session.flush()

    res = await service.detect_velocity(
        db_session,
        tenant_id,
        agent_id,
        window="24h",
        custom_threshold_count=5,
    )

    assert res.observed_count == 10
    assert res.velocity_score > Decimal("0.00")
    assert res.severity in ("high", "critical")


@pytest.mark.asyncio
async def test_velocity_detection_cross_tenant_idor_rejected(
    db_session: AsyncSession,
) -> None:
    """Test cross-tenant access to velocity detection fails with AgentNotFoundError (404)."""
    service = AgentVelocityDetectionService()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_a,
        name="Tenant A Vel Agent",
        slug="tenant-a-vel-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    with pytest.raises(AgentNotFoundError):
        await service.detect_velocity(db_session, tenant_b, agent_id)
