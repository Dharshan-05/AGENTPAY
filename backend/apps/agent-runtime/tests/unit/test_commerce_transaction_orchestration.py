"""Unit and Security Tests for Commerce Transaction Orchestration Subsystem (Phase 184)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.commerce_transaction_orchestrator_service import (
    CommerceTransactionOrchestratorService,
)
from app.domain.exceptions.agent_exceptions import ExecutionValidationError
from app.infrastructure.database.models.purchase_intent import PurchaseIntent
from app.schemas.agentpay_integration import AgentPayTransactionResult
from app.schemas.commerce_transaction_orchestration import CommerceExecutionRequest
from app.schemas.commerce_validation import CommerceValidationResult


@pytest.fixture
def service() -> CommerceTransactionOrchestratorService:
    service = CommerceTransactionOrchestratorService()
    service.validation_service.validate_commerce_request = AsyncMock()  # type: ignore[method-assign]  # noqa: E501
    service.agentpay_adapter.initiate_payment = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_execute_transaction_success(
    service: CommerceTransactionOrchestratorService,
) -> None:
    """1. Test successful transaction execution orchestration."""
    tenant_id = uuid.uuid4()
    req_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    now = datetime.now(UTC)

    service.validation_service.validate_commerce_request.return_value = (  # type: ignore[attr-defined]  # noqa: E501
        CommerceValidationResult(
            valid=True,
            purchase_request_id=req_id,
            purchase_plan_id=uuid.uuid4(),
            currency="USD",
            subtotal=Decimal("100.00"),
            discount_total=Decimal("0.00"),
            total=Decimal("100.00"),
            requires_approval=False,
            validation_errors=[],
            warnings=[],
            validated_at=now,
        )
    )

    intent = PurchaseIntent(
        id=req_id,
        tenant_id=tenant_id,
        merchant_id=uuid.uuid4(),
        agent_id=agent_id,
        product_id=uuid.uuid4(),
        intent_reference="req_exec_01",
        status="pending",
        quantity=Decimal("1.000"),
        unit_price=Decimal("100.00"),
        total_amount=Decimal("100.00"),
        currency_code="USD",
    )

    service.agentpay_adapter.initiate_payment.return_value = AgentPayTransactionResult(  # type: ignore[attr-defined]  # noqa: E501
        transaction_id=uuid.uuid4(),
        reference_code="TXN-TEST01",
        status="SETTLED",
        amount=100.00,
        currency="USD",
        recipient=f"Merchant-{intent.merchant_id}",
        requires_approval=False,
        idempotency_key="exec_12345678",
        executed_at=now,
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = intent

    req = CommerceExecutionRequest(purchase_request_id=req_id)
    res = await service.execute_commerce_transaction(mock_db, tenant_id, req)
    assert res.status == "COMPLETED"
    assert res.total_amount == Decimal("100.00")


@pytest.mark.asyncio
async def test_02_cancel_completed_transaction_rejected(
    service: CommerceTransactionOrchestratorService,
) -> None:
    """2. Test attempt to cancel a completed transaction raises ExecutionValidationError."""  # noqa: E501
    tenant_id = uuid.uuid4()
    req_id = uuid.uuid4()

    intent = PurchaseIntent(
        id=req_id,
        tenant_id=tenant_id,
        merchant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        product_id=uuid.uuid4(),
        intent_reference="req_exec_02",
        status="approved",
        quantity=Decimal("1.000"),
        unit_price=Decimal("100.00"),
        total_amount=Decimal("100.00"),
        currency_code="USD",
        intent_metadata={"execution_status": "COMPLETED"},
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = intent

    with pytest.raises(ExecutionValidationError):
        await service.cancel_commerce_transaction(mock_db, tenant_id, req_id)
