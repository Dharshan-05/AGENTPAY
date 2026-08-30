"""Unit, Security & Integration tests for Phase 145 — Intent Storage."""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.intent_storage_service import IntentStorageService
from app.domain.exceptions.agent_exceptions import AgentNotFoundError, IntentNotFoundError
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.user import User


@pytest.mark.asyncio
async def test_process_and_store_intent_pipeline_success(db_session: AsyncSession) -> None:
    """Test full pipeline: extract -> classify -> validate -> normalize -> store."""
    service = IntentStorageService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    user_id = uuid.uuid4()

    user = User(
        id=user_id,
        tenant_id=tenant_id,
        email=f"user-{uuid.uuid4().hex[:6]}@example.com",
        password_hash="hash",
    )
    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Storage Agent",
        slug="storage-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(user)
    db_session.add(agent)
    await db_session.flush()

    request_text = "Please pay $150.75 to merchant cloud_corp"
    stored_intent = await service.process_and_store_intent(
        db_session,
        tenant_id=tenant_id,
        agent_id=agent_id,
        user_id=user_id,
        request_text=request_text,
    )

    meta = stored_intent.intent_metadata
    assert stored_intent.id is not None
    assert stored_intent.tenant_id == tenant_id
    assert stored_intent.agent_id == agent_id
    assert meta["intent_type"] == "PAYMENT"
    assert meta["status"] == "stored"
    assert Decimal(meta["confidence"]) >= Decimal("0.90")
    assert meta["normalized_payload"]["action"] == "payment"
    assert meta["normalized_payload"]["entities"]["amount"] == "150.75"
    assert meta["normalized_payload"]["entities"]["currency"] == "USD"


@pytest.mark.asyncio
async def test_store_intent_sanitizes_secret_material(db_session: AsyncSession) -> None:
    """Test raw request text is sanitized before database storage."""
    service = IntentStorageService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    user_id = uuid.uuid4()

    user = User(
        id=user_id,
        tenant_id=tenant_id,
        email=f"user-{uuid.uuid4().hex[:6]}@example.com",
        password_hash="hash",
    )
    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Secret Sanitizer Agent",
        slug="secret-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(user)
    db_session.add(agent)
    await db_session.flush()

    request_text = "Pay $100 to merchant acme with password: SuperSecretPassWord123"
    stored_intent = await service.process_and_store_intent(
        db_session,
        tenant_id=tenant_id,
        agent_id=agent_id,
        user_id=user_id,
        request_text=request_text,
    )

    raw_text = str(stored_intent.intent_metadata.get("raw_text", ""))
    assert "SuperSecretPassWord123" not in raw_text
    assert "[REDACTED]" in raw_text


@pytest.mark.asyncio
async def test_get_and_list_stored_intents(db_session: AsyncSession) -> None:
    """Test retrieving and listing stored intents with tenant isolation."""
    service = IntentStorageService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    user_id = uuid.uuid4()

    user = User(
        id=user_id,
        tenant_id=tenant_id,
        email=f"user-{uuid.uuid4().hex[:6]}@example.com",
        password_hash="hash",
    )
    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Retrieval Agent",
        slug="retrieval-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(user)
    db_session.add(agent)
    await db_session.flush()

    stored_intent = await service.process_and_store_intent(
        db_session,
        tenant_id=tenant_id,
        agent_id=agent_id,
        user_id=user_id,
        request_text="Pay $50 to merchant store",
    )

    # Retrieval check
    fetched = await service.get_intent(
        db_session, tenant_id=tenant_id, agent_id=agent_id, intent_id=stored_intent.id
    )
    assert fetched.id == stored_intent.id
    assert fetched.intent_metadata["intent_type"] == "PAYMENT"

    # List check
    items, has_more = await service.list_intents(
        db_session, tenant_id=tenant_id, agent_id=agent_id, limit=10
    )
    assert len(items) == 1
    assert has_more is False
    assert items[0].id == stored_intent.id


@pytest.mark.asyncio
async def test_stored_intent_cross_tenant_idor_rejected(db_session: AsyncSession) -> None:
    """Test cross-tenant access to stored intent fails with AgentNotFoundError (404)."""
    service = IntentStorageService()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()
    user_id = uuid.uuid4()

    user = User(
        id=user_id,
        tenant_id=tenant_a,
        email=f"user-{uuid.uuid4().hex[:6]}@example.com",
        password_hash="hash",
    )
    agent = Agent(
        id=agent_id,
        tenant_id=tenant_a,
        name="Tenant A Storage Agent",
        slug="tenant-a-storage-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(user)
    db_session.add(agent)
    await db_session.flush()

    stored = await service.process_and_store_intent(
        db_session,
        tenant_id=tenant_a,
        agent_id=agent_id,
        user_id=user_id,
        request_text="Pay $75 to merchant vendor",
    )

    with pytest.raises(AgentNotFoundError):
        await service.get_intent(
            db_session, tenant_id=tenant_b, agent_id=agent_id, intent_id=stored.id
        )


@pytest.mark.asyncio
async def test_get_missing_intent_raises_404(db_session: AsyncSession) -> None:
    """Test attempting to get a non-existent intent ID raises IntentNotFoundError (404)."""
    service = IntentStorageService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Missing Intent Agent",
        slug="missing-intent-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    fake_intent_id = uuid.uuid4()
    with pytest.raises(IntentNotFoundError):
        await service.get_intent(
            db_session, tenant_id=tenant_id, agent_id=agent_id, intent_id=fake_intent_id
        )
