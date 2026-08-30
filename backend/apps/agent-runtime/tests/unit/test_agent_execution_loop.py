"""Unit, Security & Integration tests for Phase 151 — Agent Execution Loop."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_execution_service import AgentExecutionService
from app.application.services.agent_orchestrator_service import AgentOrchestratorService
from app.application.services.agent_planning_service import AgentPlanningService
from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    ExecutionBlockedError,
    ExecutionPolicyViolationError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.user import User


@pytest.mark.asyncio
async def test_create_and_run_execution_success(db_session: AsyncSession) -> None:
    """Test valid plan execution completes successfully with COMPLETED status."""
    planning_service = AgentPlanningService()
    orchestrator_service = AgentOrchestratorService()
    execution_service = AgentExecutionService()

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
        name="Execution Agent",
        slug="exec-agent",
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
        request_text="Check account balance",
    )

    orch = await orchestrator_service.orchestrate_agent(
        db_session,
        tenant_id=tenant_id,
        agent_id=agent_id,
        user_id=user_id,
        intent_id=plan.intent_id,
        plan_id=plan.plan_id,
    )

    exec_res = await execution_service.create_and_run_execution(
        db_session,
        tenant_id=tenant_id,
        agent_id=agent_id,
        user_id=user_id,
        plan_id=plan.plan_id,
        orchestration_id=orch.orchestration_id,
    )

    assert exec_res.execution_id is not None
    assert exec_res.tenant_id == tenant_id
    assert exec_res.agent_id == agent_id
    assert exec_res.plan_id == plan.plan_id
    assert exec_res.status == "COMPLETED"
    assert len(exec_res.steps) == len(plan.steps)
    assert all(s.status == "COMPLETED" for s in exec_res.steps)


@pytest.mark.asyncio
async def test_deactivated_agent_execution_rejected(db_session: AsyncSession) -> None:
    """Test execution creation for deactivated agent is rejected fail-closed."""
    planning_service = AgentPlanningService()
    execution_service = AgentExecutionService()

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
        name="Active Agent",
        slug="act-agent",
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
        request_text="Check account balance",
    )

    # Deactivate agent
    agent.status = "deactivated"
    db_session.add(agent)
    await db_session.flush()

    with pytest.raises(ExecutionPolicyViolationError):
        await execution_service.create_and_run_execution(
            db_session,
            tenant_id=tenant_id,
            agent_id=agent_id,
            user_id=user_id,
            plan_id=plan.plan_id,
        )


@pytest.mark.asyncio
async def test_suspended_agent_execution_blocked(db_session: AsyncSession) -> None:
    """Test execution creation for suspended agent is blocked fail-closed."""
    planning_service = AgentPlanningService()
    execution_service = AgentExecutionService()

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
        request_text="Check account balance",
    )

    # Suspend agent
    agent.status = "suspended"
    db_session.add(agent)
    await db_session.flush()

    with pytest.raises(ExecutionBlockedError):
        await execution_service.create_and_run_execution(
            db_session,
            tenant_id=tenant_id,
            agent_id=agent_id,
            user_id=user_id,
            plan_id=plan.plan_id,
        )


@pytest.mark.asyncio
async def test_execution_cross_tenant_idor_rejected(db_session: AsyncSession) -> None:
    """Test cross-tenant execution creation fails with AgentNotFoundError (404)."""
    execution_service = AgentExecutionService()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()
    user_id = uuid.uuid4()
    plan_id = uuid.uuid4()

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
        slug="tenant-a-exec-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(user)
    db_session.add(agent)
    await db_session.flush()

    with pytest.raises(AgentNotFoundError):
        await execution_service.create_and_run_execution(
            db_session,
            tenant_id=tenant_b,
            agent_id=agent_id,
            user_id=user_id,
            plan_id=plan_id,
        )


@pytest.mark.asyncio
async def test_cancel_execution_success(db_session: AsyncSession) -> None:
    """Test cancelling an ongoing execution loop sets status to CANCELLED."""
    planning_service = AgentPlanningService()
    execution_service = AgentExecutionService()

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
        name="Cancel Agent",
        slug="cancel-agent",
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
        request_text="Check account balance",
    )

    exec_res = await execution_service.create_and_run_execution(
        db_session,
        tenant_id=tenant_id,
        agent_id=agent_id,
        user_id=user_id,
        plan_id=plan.plan_id,
    )

    cancelled_res = await execution_service.cancel_execution(
        db_session,
        tenant_id=tenant_id,
        agent_id=agent_id,
        user_id=user_id,
        execution_id=exec_res.execution_id,
    )

    assert cancelled_res.execution_id == exec_res.execution_id
    assert cancelled_res.status == "CANCELLED"


@pytest.mark.asyncio
async def test_unsupported_execution_boundary_handling(db_session: AsyncSession) -> None:
    """Test plan steps requiring external tools hit unsupported execution boundary safely."""
    planning_service = AgentPlanningService()
    execution_service = AgentExecutionService()

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
        name="Payment Agent",
        slug="pay-agent",
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
        request_text="Pay $500.00 to merchant CloudCorp",
    )

    exec_res = await execution_service.create_and_run_execution(
        db_session,
        tenant_id=tenant_id,
        agent_id=agent_id,
        user_id=user_id,
        plan_id=plan.plan_id,
    )

    # Payment plan contains tool-requiring steps (prepare_payment)
    assert exec_res.status == "BLOCKED"
    blocked_step = [s for s in exec_res.steps if s.status == "BLOCKED"][0]
    assert blocked_step.error_code == "UNSUPPORTED_EXECUTION_BOUNDARY"
    assert blocked_step.output_metadata.get("is_supported") is False
