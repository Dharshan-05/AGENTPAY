"""Unit & Security tests for Phase 141 — Intent Classification."""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.intent_classification_service import IntentClassificationService
from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent
from app.schemas.agents import ExtractedEntities, StructuredIntent


@pytest.mark.asyncio
async def test_intent_classification_known_categories(db_session: AsyncSession) -> None:
    """Test deterministic mapping of extracted actions to canonical categories."""
    service = IntentClassificationService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Classifier Agent",
        slug="classifier-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    intent = StructuredIntent(
        intent_id=uuid.uuid4(),
        action="payment",
        target="merchant",
        entities=ExtractedEntities(amount=Decimal("100.00"), currency="USD"),
        confidence=Decimal("0.95"),
        source="rule_based_provider",
    )

    res = await service.classify_intent(db_session, tenant_id, agent_id, intent)

    assert res.agent_id == agent_id
    assert res.tenant_id == tenant_id
    assert res.classification.intent_category == "PAYMENT"
    assert res.classification.confidence == Decimal("0.95")


@pytest.mark.asyncio
async def test_intent_classification_low_confidence_forces_unknown(
    db_session: AsyncSession,
) -> None:
    """Test ambiguous/low-confidence intent forces UNKNOWN category."""
    service = IntentClassificationService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Ambiguous Agent",
        slug="ambiguous-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    intent = StructuredIntent(
        intent_id=uuid.uuid4(),
        action="payment",
        confidence=Decimal("0.30"),  # Low confidence < 0.50
        source="rule_based_provider",
    )

    res = await service.classify_intent(db_session, tenant_id, agent_id, intent)

    assert res.classification.intent_category == "UNKNOWN"
    assert "forces UNKNOWN" in res.classification.reason


@pytest.mark.asyncio
async def test_intent_classification_cross_tenant_idor_rejected(
    db_session: AsyncSession,
) -> None:
    """Test cross-tenant access to intent classification fails with AgentNotFoundError (404)."""
    service = IntentClassificationService()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_a,
        name="Tenant A Class Agent",
        slug="tenant-a-class-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    intent = StructuredIntent(
        intent_id=uuid.uuid4(),
        action="payment",
        confidence=Decimal("0.90"),
        source="rule_based_provider",
    )

    with pytest.raises(AgentNotFoundError):
        await service.classify_intent(db_session, tenant_b, agent_id, intent)
