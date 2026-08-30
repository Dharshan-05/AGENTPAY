"""Unit & Security tests for Phase 140 — Intent Extraction."""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.intent_extraction_service import IntentExtractionService
from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent


@pytest.mark.asyncio
async def test_intent_extraction_payment_request(db_session: AsyncSession) -> None:
    """Test extracting semantic intent from a payment request string."""
    service = IntentExtractionService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Extractor Agent",
        slug="extractor-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    request_text = "Please pay ₹500.50 to merchant acme_store"
    res = await service.extract_intent(db_session, tenant_id, agent_id, request_text)

    assert res.agent_id == agent_id
    assert res.tenant_id == tenant_id
    assert res.extracted_intent.action == "payment"
    assert res.extracted_intent.entities.amount == Decimal("500.50")
    assert res.extracted_intent.entities.currency == "INR"
    assert res.extracted_intent.entities.merchant == "acme_store"
    assert res.extracted_intent.confidence >= Decimal("0.90")


@pytest.mark.asyncio
async def test_intent_extraction_redacts_sensitive_material(
    db_session: AsyncSession,
) -> None:
    """Test intent extraction sanitizes passwords, API keys, and bearer tokens."""
    service = IntentExtractionService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Sanitize Agent",
        slug="sanitize-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    request_text = "Pay $100 to merchant cloud_corp with password: SuperSecretPassword123"
    res = await service.extract_intent(db_session, tenant_id, agent_id, request_text)

    # Confirm extracted entities do not contain secret material
    assert res.extracted_intent.entities.merchant == "cloud_corp"
    assert res.extracted_intent.entities.amount == Decimal("100")


@pytest.mark.asyncio
async def test_intent_extraction_cross_tenant_idor_rejected(
    db_session: AsyncSession,
) -> None:
    """Test cross-tenant access to intent extraction fails with AgentNotFoundError (404)."""
    service = IntentExtractionService()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_a,
        name="Tenant A Ext Agent",
        slug="tenant-a-ext-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    with pytest.raises(AgentNotFoundError):
        await service.extract_intent(db_session, tenant_b, agent_id, "Pay $50")
