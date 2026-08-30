"""Unit & Security tests for Phase 139 — Category Behaviour Analysis."""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_category_behaviour_service import (
    AgentCategoryBehaviourService,
)
from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.commerce_transaction import CommerceTransaction


@pytest.mark.asyncio
async def test_category_behaviour_no_transactions(db_session: AsyncSession) -> None:
    """Test category behaviour analysis when agent has zero transactions."""
    service = AgentCategoryBehaviourService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Empty Category Agent",
        slug="empty-cat-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    res = await service.analyze_category_behaviour(db_session, tenant_id, agent_id)

    assert res.agent_id == agent_id
    assert res.tenant_id == tenant_id
    assert res.total_transactions_count == 0
    assert res.unique_categories_count == 0
    assert res.dominant_category == "general"
    assert res.dominant_category_ratio == Decimal("0.00")
    assert res.risk_indicator == "normal"
    assert res.severity == "low"


@pytest.mark.asyncio
async def test_category_behaviour_high_concentration(db_session: AsyncSession) -> None:
    """Test category behaviour analysis with high concentration ratio."""
    service = AgentCategoryBehaviourService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    merchant_id = uuid.uuid4()
    product_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="High Category Agent",
        slug="high-cat-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)

    # 9 purchase transactions
    for _ in range(9):
        tx = CommerceTransaction(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            merchant_id=merchant_id,
            product_id=product_id,
            transaction_reference=f"catref-a-{uuid.uuid4().hex[:8]}",
            transaction_type="purchase",
            status="completed",
            quantity=1,
            amount=Decimal("100.00"),
            subtotal=Decimal("100.00"),
            total_amount=Decimal("100.00"),
        )
        db_session.add(tx)

    # 1 refund transaction
    tx_b = CommerceTransaction(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent_id,
        merchant_id=merchant_id,
        product_id=product_id,
        transaction_reference=f"catref-b-{uuid.uuid4().hex[:8]}",
        transaction_type="refund",
        status="completed",
        quantity=1,
        amount=Decimal("100.00"),
        subtotal=Decimal("100.00"),
        total_amount=Decimal("100.00"),
    )
    db_session.add(tx_b)
    await db_session.flush()

    res = await service.analyze_category_behaviour(db_session, tenant_id, agent_id)

    assert res.total_transactions_count == 10
    assert res.unique_categories_count == 2
    assert res.dominant_category == "purchase"
    assert res.dominant_category_ratio == Decimal("0.90")
    assert res.risk_indicator == "unusual_concentration"
    assert res.severity == "medium"


@pytest.mark.asyncio
async def test_category_behaviour_cross_tenant_idor_rejected(
    db_session: AsyncSession,
) -> None:
    """Test cross-tenant access to category behaviour fails with AgentNotFoundError (404)."""
    service = AgentCategoryBehaviourService()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_a,
        name="Tenant A Cat Agent",
        slug="tenant-a-cat-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    with pytest.raises(AgentNotFoundError):
        await service.analyze_category_behaviour(db_session, tenant_b, agent_id)
