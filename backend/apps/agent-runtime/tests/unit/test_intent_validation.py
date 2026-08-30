"""Unit & Security tests for Phase 143 — Intent Validation."""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.intent_validation_service import IntentValidationService
from app.domain.exceptions.agent_exceptions import AgentNotFoundError, IntentValidationError
from app.infrastructure.database.models.agent import Agent
from app.schemas.agents import ExtractedEntities, StructuredIntent


@pytest.mark.asyncio
async def test_valid_payment_intent_validation(db_session: AsyncSession) -> None:
    """Test valid PAYMENT intent passes validation and is execution eligible."""
    service = IntentValidationService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Validation Agent",
        slug="val-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    intent = StructuredIntent(
        intent_id=uuid.uuid4(),
        action="payment",
        target="merchant",
        entities=ExtractedEntities(amount=Decimal("250.00"), currency="USD", merchant="cloud_corp"),
        confidence=Decimal("0.95"),
        source="rule_based_provider",
    )

    res = await service.validate_intent(
        db_session, tenant_id, agent_id, intent, intent_category="PAYMENT"
    )

    assert res.is_valid is True
    assert res.intent_category == "PAYMENT"
    assert res.is_execution_eligible is True
    assert len(res.validation_errors) == 0


@pytest.mark.asyncio
async def test_invalid_payment_missing_amount(db_session: AsyncSession) -> None:
    """Test PAYMENT intent missing amount fails validation."""
    service = IntentValidationService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Validation Agent 2",
        slug="val-agent-2",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    intent = StructuredIntent(
        intent_id=uuid.uuid4(),
        action="payment",
        target="merchant",
        entities=ExtractedEntities(currency="USD"),  # missing amount
        confidence=Decimal("0.90"),
        source="rule_based_provider",
    )

    res = await service.validate_intent(
        db_session, tenant_id, agent_id, intent, intent_category="PAYMENT"
    )

    assert res.is_valid is False
    assert res.is_execution_eligible is False
    assert any("amount" in err for err in res.validation_errors)


@pytest.mark.asyncio
async def test_unknown_intent_is_not_execution_eligible(db_session: AsyncSession) -> None:
    """Test UNKNOWN category is valid as representation but ineligible for execution."""
    service = IntentValidationService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Validation Agent 3",
        slug="val-agent-3",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    intent = StructuredIntent(
        intent_id=uuid.uuid4(),
        action="unknown_action",
        confidence=Decimal("0.40"),
        source="rule_based_provider",
    )

    res = await service.validate_intent(
        db_session, tenant_id, agent_id, intent, intent_category="UNKNOWN"
    )

    assert res.is_valid is True
    assert res.intent_category == "UNKNOWN"
    assert res.is_execution_eligible is False


@pytest.mark.asyncio
async def test_validation_suspended_agent_fails(db_session: AsyncSession) -> None:
    """Test suspended agent fails intent validation with IntentValidationError."""
    service = IntentValidationService()
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
    db_session.add(agent)
    await db_session.flush()

    intent = StructuredIntent(
        intent_id=uuid.uuid4(),
        action="payment",
        confidence=Decimal("0.95"),
        source="rule_based_provider",
    )

    with pytest.raises(IntentValidationError):
        await service.validate_intent(
            db_session, tenant_id, agent_id, intent, intent_category="PAYMENT"
        )


@pytest.mark.asyncio
async def test_validation_cross_tenant_idor_rejected(db_session: AsyncSession) -> None:
    """Test cross-tenant access during validation fails with AgentNotFoundError (404)."""
    service = IntentValidationService()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_a,
        name="Tenant A Agent",
        slug="tenant-a-val-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    intent = StructuredIntent(
        intent_id=uuid.uuid4(),
        action="payment",
        confidence=Decimal("0.95"),
        source="rule_based_provider",
    )

    with pytest.raises(AgentNotFoundError):
        await service.validate_intent(
            db_session, tenant_b, agent_id, intent, intent_category="PAYMENT"
        )
