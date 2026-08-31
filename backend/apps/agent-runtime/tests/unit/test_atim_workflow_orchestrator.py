"""Unit tests for ATIM Durable Workflow Orchestrator (Phase 23 / Group 12)."""

import uuid

import pytest

from app.application.services.atim_workflow_orchestrator import ATIMWorkflowOrchestrator
from app.domain.governance.workflow_models import WorkflowState, WorkflowStepType


@pytest.fixture
def workflow_orchestrator():
    return ATIMWorkflowOrchestrator()


def test_01_start_workflow_initiation(workflow_orchestrator):
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    corr_id = "corr_wf_01"

    wf = workflow_orchestrator.start_workflow(
        tenant_id=tenant_id,
        workflow_type="PAYMENT_APPROVAL_FLOW",
        correlation_id=corr_id,
        total_steps=2,
        agent_id=agent_id,
    )

    assert wf.tenant_id == tenant_id
    assert wf.workflow_type == "PAYMENT_APPROVAL_FLOW"
    assert wf.state == WorkflowState.INITIATED
    assert wf.signature is not None


def test_02_execute_workflow_steps_to_completion(workflow_orchestrator):
    tenant_id = uuid.uuid4()
    wf = workflow_orchestrator.start_workflow(tenant_id, "PAYMENT_APPROVAL_FLOW", "corr_02", total_steps=2)

    # Step 0
    is_replayed0, step0 = workflow_orchestrator.execute_workflow_step(
        workflow_id=wf.id,
        step_index=0,
        step_type=WorkflowStepType.VALIDATE_INTENT,
        input_params={"amount": "500.00"},
        handler_result={"valid": True},
    )
    assert is_replayed0 is False
    assert step0.step_index == 0

    # Step 1 -> Completes Workflow
    is_replayed1, step1 = workflow_orchestrator.execute_workflow_step(
        workflow_id=wf.id,
        step_index=1,
        step_type=WorkflowStepType.EXECUTE_TRANSACTION,
        input_params={"payment_method": "UPI"},
        handler_result={"status": "SUCCESS"},
    )
    assert is_replayed1 is False
    assert workflow_orchestrator.get_workflow_instance(wf.id).state == WorkflowState.COMPLETED


def test_03_step_level_idempotency_replay(workflow_orchestrator):
    tenant_id = uuid.uuid4()
    wf = workflow_orchestrator.start_workflow(tenant_id, "TRANSFER_FLOW", "corr_03", total_steps=2)
    params = {"amount": "100.00"}

    # Execute step 0 first time
    _, step_first = workflow_orchestrator.execute_workflow_step(wf.id, 0, WorkflowStepType.CHECK_LIMITS, params, {"allowed": True})

    # Re-execute step 0 second time with identical input -> returns replayed step record
    is_replayed, step_second = workflow_orchestrator.execute_workflow_step(wf.id, 0, WorkflowStepType.CHECK_LIMITS, params, {"allowed": True})

    assert is_replayed is True
    assert step_second.id == step_first.id


def test_04_workflow_cancellation(workflow_orchestrator):
    tenant_id = uuid.uuid4()
    wf = workflow_orchestrator.start_workflow(tenant_id, "TRANSFER_FLOW", "corr_04", total_steps=2)

    cancelled = workflow_orchestrator.cancel_workflow(wf.id, reason="User requested cancellation")
    assert cancelled.state == WorkflowState.CANCELLED
