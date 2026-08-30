"""Unit, Security & Integration tests for Phase 150 — Agent Runtime State Management."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_state_service import AgentStateService
from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    InvalidAgentStateTransitionError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.user import User


@pytest.mark.asyncio
async def test_valid_state_transition_sequence(db_session: AsyncSession) -> None:
    """Test valid runtime state transition sequence: IDLE -> PREPARING -> READY -> WAITING."""
    service = AgentStateService()
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
        name="State Agent",
        slug="state-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(user)
    db_session.add(agent)
    await db_session.flush()

    # Initial state lookup
    s0 = await service.get_agent_state(db_session, tenant_id, agent_id)
    assert s0.current_state == "IDLE"
    assert s0.previous_state is None

    # Transition 1: IDLE -> PREPARING
    s1 = await service.update_agent_state(
        db_session,
        tenant_id,
        agent_id,
        user_id,
        requested_transition="PREPARING",
        reason="Preparing plan",
    )
    assert s1.current_state == "PREPARING"
    assert s1.previous_state == "IDLE"

    # Transition 2: PREPARING -> READY
    s2 = await service.update_agent_state(
        db_session,
        tenant_id,
        agent_id,
        user_id,
        requested_transition="READY",
        reason="Plan validated",
    )
    assert s2.current_state == "READY"
    assert s2.previous_state == "PREPARING"

    # Transition 3: READY -> WAITING
    s3 = await service.update_agent_state(
        db_session,
        tenant_id,
        agent_id,
        user_id,
        requested_transition="WAITING",
        reason="Awaiting event",
    )
    assert s3.current_state == "WAITING"
    assert s3.previous_state == "READY"


@pytest.mark.asyncio
async def test_invalid_state_transition_fails(db_session: AsyncSession) -> None:
    """Test attempting an illegal transition (IDLE -> READY directly) fails fail-closed."""
    service = AgentStateService()
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
        name="Invalid State Agent",
        slug="invalid-state-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(user)
    db_session.add(agent)
    await db_session.flush()

    with pytest.raises(InvalidAgentStateTransitionError):
        await service.update_agent_state(
            db_session, tenant_id, agent_id, user_id, requested_transition="READY"
        )


@pytest.mark.asyncio
async def test_deactivated_agent_state_update_rejected(db_session: AsyncSession) -> None:
    """Test state update for deactivated agent is rejected fail-closed."""
    service = AgentStateService()
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
        name="Deactivated State Agent",
        slug="deact-state-agent",
        agent_type="autonomous",
        status="deactivated",
    )
    db_session.add(user)
    db_session.add(agent)
    await db_session.flush()

    with pytest.raises(InvalidAgentStateTransitionError):
        await service.update_agent_state(
            db_session, tenant_id, agent_id, user_id, requested_transition="PREPARING"
        )


@pytest.mark.asyncio
async def test_state_cross_tenant_idor_rejected(db_session: AsyncSession) -> None:
    """Test cross-tenant state lookup/update fails with AgentNotFoundError (404)."""
    service = AgentStateService()
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
        name="Tenant A State Agent",
        slug="tenant-a-state-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(user)
    db_session.add(agent)
    await db_session.flush()

    with pytest.raises(AgentNotFoundError):
        await service.get_agent_state(db_session, tenant_b, agent_id)

    with pytest.raises(AgentNotFoundError):
        await service.update_agent_state(
            db_session, tenant_b, agent_id, user_id, requested_transition="PREPARING"
        )
