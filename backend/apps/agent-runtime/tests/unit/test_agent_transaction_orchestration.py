"""Unit and security tests for Phase 161 Agent Transaction Orchestration."""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.application.services.agent_transaction_orchestrator_service import (
    AgentTransactionOrchestratorService,
)
from app.domain.exceptions.agent_exceptions import WorkflowExecutionError
from app.schemas.human_approval import ApprovalPolicyEvaluationResponse, ApprovalRiskLevel
from app.schemas.transaction_orchestration import (
    StepExecutionMode,
    WorkflowCancelRequest,
    WorkflowCreateRequest,
    WorkflowStatus,
    WorkflowStepCreate,
)


@pytest.fixture
def mock_db() -> MagicMock:
    """Fixture for SQLAlchemy session mock."""
    session = MagicMock()
    session.execute.return_value.scalar_one_or_none.return_value = None
    return session


@pytest.fixture
def service() -> AgentTransactionOrchestratorService:
    """Fixture for AgentTransactionOrchestratorService."""
    return AgentTransactionOrchestratorService()


@pytest.mark.asyncio
async def test_01_create_and_start_workflow_success(
    mock_db: MagicMock, service: AgentTransactionOrchestratorService
) -> None:
    """1. Test successful creation and step execution of an orchestrated transaction workflow."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = WorkflowCreateRequest(
        workflow_name="Test Payment Workflow",
        idempotency_key=f"IDEM-{uuid.uuid4().hex[:8]}",
        amount=25.00,
        currency="USD",
        steps=[
            WorkflowStepCreate(
                step_number=1,
                step_name="verify_balance",
                tool_name="balance_check",
                execution_mode=StepExecutionMode.SEQUENTIAL,
            ),
            WorkflowStepCreate(
                step_number=2,
                step_name="execute_transfer",
                tool_name="payment_transfer",
                execution_mode=StepExecutionMode.SEQUENTIAL,
                depends_on_steps=["verify_balance"],
            ),
        ],
    )

    with (
        patch.object(
            service._trust_service, "get_agent_trust", return_value={"agent_id": agent_id}
        ),
        patch.object(
            service._approval_service,
            "evaluate_approval_policy",
            return_value=ApprovalPolicyEvaluationResponse(
                requires_approval=False,
                risk_level=ApprovalRiskLevel.LOW,
                required_approvals_count=0,
                matched_policy_name="Low Risk Policy",
                auto_approved=True,
            ),
        ),
    ):
        res = await service.create_and_start_workflow(mock_db, tenant_id, agent_id, req)

        assert res.workflow_name == "Test Payment Workflow"
        assert res.status == WorkflowStatus.COMPLETED
        assert res.total_steps == 2
        assert len(res.steps) == 2
        assert res.steps[0].status == "COMPLETED"
        assert res.steps[1].status == "COMPLETED"


@pytest.mark.asyncio
async def test_02_workflow_cancellation(
    mock_db: MagicMock, service: AgentTransactionOrchestratorService
) -> None:
    """2. Test cancellation of an active workflow."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    workflow_id = uuid.uuid4()

    mock_plan = MagicMock()
    mock_plan.id = workflow_id
    mock_plan.tenant_id = tenant_id
    mock_plan.agent_id = agent_id
    mock_plan.status = WorkflowStatus.VALIDATING.value
    mock_plan.plan_reference = "IDEM-12345"
    mock_plan.total_estimated_cost = 100.0
    mock_plan.steps = []
    mock_plan.plan_metadata = {"workflow_name": "Test Cancel"}

    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_plan

    cancel_req = WorkflowCancelRequest(reason="User changed mind")
    res = await service.cancel_workflow(mock_db, tenant_id, agent_id, workflow_id, cancel_req)

    assert res.status == WorkflowStatus.CANCELLED


@pytest.mark.asyncio
async def test_03_cross_tenant_workflow_isolation(
    mock_db: MagicMock, service: AgentTransactionOrchestratorService
) -> None:
    """3. Verify cross-tenant workflow lookup failure (tenant isolation)."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    workflow_id = uuid.uuid4()

    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    with pytest.raises(WorkflowExecutionError, match="not found"):
        await service.get_workflow_status(mock_db, tenant_id, agent_id, workflow_id)
