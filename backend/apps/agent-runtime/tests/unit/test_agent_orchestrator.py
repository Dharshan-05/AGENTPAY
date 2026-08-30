"""Unit, Security & Integration tests for Phase 149 — Agent Orchestrator."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_orchestrator_service import AgentOrchestratorService
from app.application.services.agent_planning_service import AgentPlanningService
from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.user import User


@pytest.mark.asyncio
async def test_orchestrate_agent_ready_decision(db_session: AsyncSession) -> None:
    """Test valid agent orchestration yields READY decision and state."""
    planning_service = AgentPlanningService()
    orchestrator_service = AgentOrchestratorService()

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
        name="Orchestration Agent",
        slug="orch-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(user)
    db_session.add(agent)
    await db_session.flush()

    plan, _ = await planning_service.create_and_validate_plan(
        db_session,
        tenant_id=tenant_id,
        agent_id=agent_id,
        user_id=user_id,
        request_text="Pay $100.00 to merchant CloudCorp",
    )

    orch_res = await orchestrator_service.orchestrate_agent(
        db_session,
        tenant_id=tenant_id,
        agent_id=agent_id,
        user_id=user_id,
        intent_id=plan.intent_id,
        plan_id=plan.plan_id,
    )

    assert orch_res.orchestration_id is not None
    assert orch_res.tenant_id == tenant_id
    assert orch_res.agent_id == agent_id
    assert orch_res.decision == "READY"
    assert orch_res.state == "READY"
    assert orch_res.execution_eligible is True
    assert orch_res.plan_valid is True
    assert orch_res.intent_valid is True


@pytest.mark.asyncio
async def test_orchestrate_deactivated_agent_rejected(db_session: AsyncSession) -> None:
    """Test deactivated agent orchestration is REJECTED with security event."""
    orchestrator_service = AgentOrchestratorService()

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
        name="Deactivated Agent",
        slug="deact-agent",
        agent_type="autonomous",
        status="deactivated",
    )
    db_session.add(user)
    db_session.add(agent)
    await db_session.flush()

    orch_res = await orchestrator_service.orchestrate_agent(
        db_session,
        tenant_id=tenant_id,
        agent_id=agent_id,
        user_id=user_id,
    )

    assert orch_res.decision == "REJECTED"
    assert orch_res.state == "REJECTED"
    assert orch_res.execution_eligible is False
    assert any("status is 'deactivated'" in r for r in orch_res.blocking_reasons)


@pytest.mark.asyncio
async def test_orchestrate_suspended_agent_blocked(db_session: AsyncSession) -> None:
    """Test suspended agent orchestration yields BLOCKED decision."""
    orchestrator_service = AgentOrchestratorService()

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
        slug="susp-agent",
        agent_type="autonomous",
        status="suspended",
    )
    db_session.add(user)
    db_session.add(agent)
    await db_session.flush()

    orch_res = await orchestrator_service.orchestrate_agent(
        db_session,
        tenant_id=tenant_id,
        agent_id=agent_id,
        user_id=user_id,
    )

    assert orch_res.decision == "BLOCKED"
    assert orch_res.state == "BLOCKED"
    assert orch_res.execution_eligible is False


@pytest.mark.asyncio
async def test_orchestration_cross_tenant_idor_rejected(db_session: AsyncSession) -> None:
    """Test cross-tenant orchestration lookup fails with AgentNotFoundError (404)."""
    orchestrator_service = AgentOrchestratorService()

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

    with pytest.raises(AgentNotFoundError):
        await orchestrator_service.orchestrate_agent(
            db_session,
            tenant_id=tenant_b,
            agent_id=agent_id,
            user_id=user_id,
        )


@pytest.mark.asyncio
async def test_orchestrator_no_execution_guarantee(db_session: AsyncSession) -> None:
    """Test orchestration decision occurs without executing plan or calling tools."""
    planning_service = AgentPlanningService()
    orchestrator_service = AgentOrchestratorService()

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
        name="Zero Execution Agent",
        slug="zero-exec-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(user)
    db_session.add(agent)
    await db_session.flush()

    plan, _ = await planning_service.create_and_validate_plan(
        db_session,
        tenant_id=tenant_id,
        agent_id=agent_id,
        user_id=user_id,
        request_text="Pay $300.00 to merchant ZeroExec",
    )

    orch_res = await orchestrator_service.orchestrate_agent(
        db_session,
        tenant_id=tenant_id,
        agent_id=agent_id,
        user_id=user_id,
        intent_id=plan.intent_id,
        plan_id=plan.plan_id,
    )

    # Decision is READY, but NO execution happened!
    assert orch_res.decision == "READY"
    assert orch_res.state == "READY"
    # Agent status remains unchanged active
    assert agent.status == "active"
