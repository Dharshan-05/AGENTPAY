"""Unit, Security & Integration tests for Phase 146 — Agent Planning Engine."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_planning_service import AgentPlanningService
from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    PlanGenerationError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.user import User


@pytest.mark.asyncio
async def test_create_and_validate_plan_success(db_session: AsyncSession) -> None:
    """Test creating and validating a plan from request text."""
    service = AgentPlanningService()
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
        name="Planning Agent",
        slug="planning-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(user)
    db_session.add(agent)
    await db_session.flush()

    request_text = "Please pay $250.00 to merchant CloudServ"
    plan, val_res = await service.create_and_validate_plan(
        db_session,
        tenant_id=tenant_id,
        agent_id=agent_id,
        user_id=user_id,
        request_text=request_text,
    )

    assert plan.plan_id is not None
    assert plan.tenant_id == tenant_id
    assert plan.agent_id == agent_id
    assert plan.intent_type == "PAYMENT"
    assert len(plan.steps) == 5
    assert val_res.is_valid is True
    assert val_res.execution_eligible is True


@pytest.mark.asyncio
async def test_get_stored_plan_by_id(db_session: AsyncSession) -> None:
    """Test retrieving stored plan by ID within tenant scope."""
    service = AgentPlanningService()
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
        name="Retrieval Planning Agent",
        slug="retrieval-planning-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(user)
    db_session.add(agent)
    await db_session.flush()

    created_plan, _ = await service.create_and_validate_plan(
        db_session,
        tenant_id=tenant_id,
        agent_id=agent_id,
        user_id=user_id,
        request_text="Check balance for account",
    )

    fetched = await service.get_plan(
        db_session, tenant_id=tenant_id, agent_id=agent_id, plan_id=created_plan.plan_id
    )
    assert fetched.plan_id == created_plan.plan_id
    assert fetched.intent_type == "BALANCE_QUERY"
    assert len(fetched.steps) == 2


@pytest.mark.asyncio
async def test_plan_cross_tenant_idor_rejected(db_session: AsyncSession) -> None:
    """Test cross-tenant plan access attempt fails with AgentNotFoundError (404)."""
    service = AgentPlanningService()
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
        name="Tenant A Agent",
        slug="tenant-a-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(user)
    db_session.add(agent)
    await db_session.flush()

    plan, _ = await service.create_and_validate_plan(
        db_session,
        tenant_id=tenant_a,
        agent_id=agent_id,
        user_id=user_id,
        request_text="Query transaction logs",
    )

    with pytest.raises(AgentNotFoundError):
        await service.get_plan(
            db_session, tenant_id=tenant_b, agent_id=agent_id, plan_id=plan.plan_id
        )


@pytest.mark.asyncio
async def test_suspended_agent_planning_rejected(db_session: AsyncSession) -> None:
    """Test attempting to generate plan for suspended agent fails."""
    service = AgentPlanningService()
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
        name="Suspended Agent",
        slug="suspended-agent",
        agent_type="autonomous",
        status="suspended",
    )
    db_session.add(user)
    db_session.add(agent)
    await db_session.flush()

    with pytest.raises(PlanGenerationError):
        await service.create_and_validate_plan(
            db_session,
            tenant_id=tenant_id,
            agent_id=agent_id,
            user_id=user_id,
            request_text="Pay $50.00 to merchant test",
        )
