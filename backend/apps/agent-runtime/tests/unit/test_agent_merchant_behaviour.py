"""Unit & Security tests for Phase 138 — Merchant Behaviour Analysis."""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_merchant_behaviour_service import AgentMerchantBehaviourService
from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.commerce_transaction import CommerceTransaction


@pytest.mark.asyncio
async def test_merchant_behaviour_no_transactions(db_session: AsyncSession) -> None:
    """Test merchant behaviour analysis when agent has zero transactions."""
    service = AgentMerchantBehaviourService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Empty Merchant Agent",
        slug="empty-merchant-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    res = await service.analyze_merchant_behaviour(db_session, tenant_id, agent_id)

    assert res.unique_merchants_count == 0
    assert res.top_merchant_concentration == Decimal("0.00")
    assert res.risk_indicator == "normal"
    assert res.severity == "low"


@pytest.mark.asyncio
async def test_merchant_behaviour_high_concentration(db_session: AsyncSession) -> None:
    """Test merchant behaviour analysis when top merchant concentration is >= 90%."""
    service = AgentMerchantBehaviourService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Conc Agent",
        slug="conc-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)

    # 10 transactions with exact same merchant
    for _i in range(10):
        tx = CommerceTransaction(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            merchant_id=merchant_id,
            product_id=uuid.uuid4(),
            transaction_reference=f"mref-{uuid.uuid4().hex[:8]}",
            transaction_type="purchase",
            status="completed",
            quantity=1,
            amount=Decimal("50.00"),
            subtotal=Decimal("50.00"),
            total_amount=Decimal("50.00"),
        )
        db_session.add(tx)
    await db_session.flush()

    res = await service.analyze_merchant_behaviour(db_session, tenant_id, agent_id)

    assert res.unique_merchants_count == 1
    assert res.top_merchant_concentration == Decimal("1.00")
    assert res.risk_indicator == "unusual_concentration"
    assert res.severity == "medium"


@pytest.mark.asyncio
async def test_merchant_behaviour_new_merchant_burst(db_session: AsyncSession) -> None:
    """Test merchant behaviour analysis when burst of 5+ new merchants are added."""
    service = AgentMerchantBehaviourService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Burst Agent",
        slug="burst-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)

    # Insert transactions with 5 distinct merchants
    for _i in range(5):
        m_id = uuid.uuid4()
        tx = CommerceTransaction(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            merchant_id=m_id,
            product_id=uuid.uuid4(),
            transaction_reference=f"bmref-{uuid.uuid4().hex[:8]}",
            transaction_type="purchase",
            status="completed",
            quantity=1,
            amount=Decimal("100.00"),
            subtotal=Decimal("100.00"),
            total_amount=Decimal("100.00"),
        )
        db_session.add(tx)
    await db_session.flush()

    res = await service.analyze_merchant_behaviour(db_session, tenant_id, agent_id)

    assert res.new_merchants_last_7d == 5
    assert res.risk_indicator == "new_merchant_burst"
    assert res.severity == "high"


@pytest.mark.asyncio
async def test_merchant_behaviour_cross_tenant_idor_rejected(
    db_session: AsyncSession,
) -> None:
    """Test cross-tenant access to merchant behaviour fails with AgentNotFoundError (404)."""
    service = AgentMerchantBehaviourService()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_a,
        name="Tenant A M Agent",
        slug="tenant-a-m-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    with pytest.raises(AgentNotFoundError):
        await service.analyze_merchant_behaviour(db_session, tenant_b, agent_id)
