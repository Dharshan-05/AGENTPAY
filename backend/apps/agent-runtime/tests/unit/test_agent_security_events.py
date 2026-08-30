"""Unit & Security tests for Phase 133 — Agent Security Events."""

import uuid
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_security_event_service import AgentSecurityEventService
from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent


@pytest.mark.asyncio
async def test_record_agent_security_event_success(db_session: AsyncSession) -> None:
    """Test recording an append-only security event for an agent."""
    service = AgentSecurityEventService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    event = await service.record_security_event(
        db_session,
        tenant_id,
        agent_id=agent_id,
        event_type="credential",
        event_action="credential_used",
        event_result="success",
        severity="low",
        event_payload={"client_ip": "127.0.0.1"},
    )

    assert event.id is not None
    assert event.tenant_id == tenant_id
    assert event.agent_id == agent_id
    assert event.event_type == "credential"
    assert event.event_action == "credential_used"
    assert event.severity == "low"


@pytest.mark.asyncio
async def test_record_security_event_sanitizes_secret_payload(
    db_session: AsyncSession,
) -> None:
    """Test that security event payload sanitizes raw credentials and tokens."""
    service = AgentSecurityEventService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    payload: dict[str, Any] = {
        "password": "supersecretpassword",
        "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "context": "authentication_attempt",
    }

    event = await service.record_security_event(
        db_session,
        tenant_id,
        agent_id=agent_id,
        event_type="authentication",
        event_action="login",
        event_payload=payload,
    )

    assert event.event_payload is not None
    assert event.event_payload["password"] == "[REDACTED]"
    assert event.event_payload["jwt"] == "[REDACTED]"
    assert event.event_payload["context"] == "authentication_attempt"


@pytest.mark.asyncio
async def test_list_agent_security_events_success(db_session: AsyncSession) -> None:
    """Test listing security events for an agent with filters."""
    service = AgentSecurityEventService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Security Agent",
        slug="security-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    await service.record_security_event(
        db_session,
        tenant_id,
        agent_id=agent_id,
        event_type="credential",
        event_action="credential_used",
        severity="low",
    )
    await service.record_security_event(
        db_session,
        tenant_id,
        agent_id=agent_id,
        event_type="suspicious_activity",
        event_action="tenant_boundary_violation",
        severity="high",
    )

    events, _ = await service.list_agent_security_events(
        db_session, tenant_id, agent_id, severity="high"
    )

    assert len(events) == 1
    assert events[0].severity == "high"
    assert events[0].event_action == "tenant_boundary_violation"


@pytest.mark.asyncio
async def test_agent_security_events_cross_tenant_idor_rejected(
    db_session: AsyncSession,
) -> None:
    """Test cross-tenant access to security events fails with AgentNotFoundError (404)."""
    service = AgentSecurityEventService()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_a,
        name="Tenant A Sec Agent",
        slug="tenant-a-sec-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    with pytest.raises(AgentNotFoundError):
        await service.list_agent_security_events(db_session, tenant_b, agent_id)
