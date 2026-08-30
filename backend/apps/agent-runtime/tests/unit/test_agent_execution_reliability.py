"""Unit and security tests for Phase 163 Agent Execution Reliability."""

import uuid
from unittest.mock import MagicMock

import pytest

from app.application.services.agent_execution_reliability_service import (
    AgentExecutionReliabilityService,
)
from app.domain.exceptions.agent_exceptions import CircuitBreakerOpenError
from app.schemas.execution_reliability import (
    CircuitBreakerState,
    ExecutionReconcileRequest,
    ExecutionRetryRequest,
    RetryClassification,
)


@pytest.fixture
def mock_db() -> MagicMock:
    """Fixture for SQLAlchemy session mock."""
    session = MagicMock()
    session.execute.return_value.scalar_one_or_none.return_value = None
    return session


@pytest.fixture
def service() -> AgentExecutionReliabilityService:
    """Fixture for AgentExecutionReliabilityService."""
    return AgentExecutionReliabilityService()


@pytest.mark.asyncio
async def test_01_retry_safety_classification_rules(
    service: AgentExecutionReliabilityService,
) -> None:
    """1. Verify retry classification rules (SAFE_TO_RETRY vs NOT_SAFE_TO_RETRY vs REQUIRES_RECONCILIATION)."""  # noqa: E501
    # Financial operation timeout -> REQUIRES_RECONCILIATION
    recon_eval = await service.classify_retry_safety(
        error_message="gateway_timeout during charge", is_financial=True, is_idempotent=True
    )
    assert recon_eval.classification == RetryClassification.REQUIRES_RECONCILIATION
    assert recon_eval.is_retryable is False

    # Financial operation without idempotency -> NOT_SAFE_TO_RETRY
    non_idem_eval = await service.classify_retry_safety(
        error_message="financial charge failed", is_financial=True, is_idempotent=False
    )
    assert non_idem_eval.classification == RetryClassification.NOT_SAFE_TO_RETRY
    assert non_idem_eval.is_retryable is False

    # Transient error on idempotent query -> SAFE_TO_RETRY
    transient_eval = await service.classify_retry_safety(
        error_message="HTTP 503 Service Unavailable", is_financial=False, is_idempotent=True
    )
    assert transient_eval.classification == RetryClassification.SAFE_TO_RETRY
    assert transient_eval.is_retryable is True


@pytest.mark.asyncio
async def test_02_circuit_breaker_tripped_blocks_execution(
    mock_db: MagicMock, service: AgentExecutionReliabilityService
) -> None:
    """2. Verify that an OPEN circuit breaker blocks retry attempts."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    workflow_id = uuid.uuid4()

    # Trip circuit breaker for payment gateway (threshold = 5)
    for _ in range(5):
        await service.record_service_failure("payment_gateway")

    cb_status = await service.get_circuit_breaker_status("payment_gateway")
    assert cb_status.state == CircuitBreakerState.OPEN

    retry_req = ExecutionRetryRequest(
        workflow_id=workflow_id,
        step_name="process_payment",
        idempotency_key="IDEM-TEST-123",
        force_retry=False,
    )

    with pytest.raises(CircuitBreakerOpenError, match="circuit breaker is OPEN"):
        await service.attempt_safe_execution_retry(mock_db, tenant_id, agent_id, retry_req)


@pytest.mark.asyncio
async def test_03_reconcile_execution_state_success(
    mock_db: MagicMock, service: AgentExecutionReliabilityService
) -> None:
    """3. Verify successful financial execution state reconciliation."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    workflow_id = uuid.uuid4()

    reconcile_req = ExecutionReconcileRequest(
        workflow_id=workflow_id,
        payment_order_id=uuid.uuid4(),
        resolution_action="CONFIRM_SUCCESS",
        reason="Bank gateway confirmed transaction status in settlement report.",
    )

    res = await service.reconcile_execution_state(mock_db, tenant_id, agent_id, reconcile_req)

    assert res.reconciled is True
    assert res.classification == RetryClassification.REQUIRES_RECONCILIATION
    assert "reconciled successfully" in res.message
