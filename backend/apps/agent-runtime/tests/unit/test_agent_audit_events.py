"""Unit & Security tests for Phase 132 — Agent Audit Events."""

import uuid
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_audit_service import AgentAuditService
from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent


@pytest.mark.asyncio
async def test_record_agent_audit_event_success(db_session: AsyncSession) -> None:
    """Test recording an immutable audit event for an agent."""
    service = AgentAuditService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    actor_id = uuid.uuid4()

    event = await service.record_audit_event(
        db_session,
        tenant_id,
        agent_id,
        actor_id,
        event_type="agent_activated",
        event_action="activate_agent",
        event_result="success",
        event_metadata={"reason": "Manual activation"},
    )

    assert event.id is not None
    assert event.tenant_id == tenant_id
    assert event.agent_id == agent_id
    assert event.actor_id == actor_id
    assert event.event_type == "agent_activated"
    assert event.event_action == "activate_agent"
    assert event.event_result == "success"


@pytest.mark.asyncio
async def test_record_agent_audit_event_sanitizes_sensitive_metadata(
    db_session: AsyncSession,
) -> None:
    """Test that audit event metadata automatically redacts secret fields."""
    service = AgentAuditService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    actor_id = uuid.uuid4()

    metadata: dict[str, Any] = {
        "raw_secret": "my_secret_key",
        "access_token": "bearer_12345",
        "safe_field": "public_info",
    }

    event = await service.record_audit_event(
        db_session,
        tenant_id,
        agent_id,
        actor_id,
        event_type="credential_issued",
        event_action="issue_credential",
        event_metadata=metadata,
    )

    assert event.event_metadata["raw_secret"] == "[REDACTED]"
    assert event.event_metadata["access_token"] == "[REDACTED]"
    assert event.event_metadata["safe_field"] == "public_info"


@pytest.mark.asyncio
async def test_list_agent_audit_events_keyset_pagination(db_session: AsyncSession) -> None:
    """Test keyset pagination for listing audit events."""
    service = AgentAuditService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    actor_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Audit Agent",
        slug="audit-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    for i in range(5):
        await service.record_audit_event(
            db_session,
            tenant_id,
            agent_id,
            actor_id,
            event_type=f"event_{i}",
            event_action=f"action_{i}",
        )

    events, has_more = await service.list_agent_audit_events(
        db_session, tenant_id, agent_id, limit=3
    )

    assert len(events) == 3
    assert has_more is True


@pytest.mark.asyncio
async def test_agent_audit_events_cross_tenant_idor_rejected(db_session: AsyncSession) -> None:
    """Test cross-tenant access to audit events fails with AgentNotFoundError (404)."""
    service = AgentAuditService()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_a,
        name="Tenant A Audit Agent",
        slug="tenant-a-audit-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    with pytest.raises(AgentNotFoundError):
        await service.list_agent_audit_events(db_session, tenant_b, agent_id)
