"""Integration tests for ATIM Durable Workflow REST APIs (Phase 23 / Group 12)."""

import pytest


def test_01_workflow_model_imports():
    from app.domain.governance.workflow_models import WorkflowState, WorkflowStepType
    assert WorkflowState.COMPLETED.value == "COMPLETED"
    assert WorkflowStepType.EXECUTE_TRANSACTION.value == "EXECUTE_TRANSACTION"
