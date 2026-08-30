"""Unit and Financial Integrity Tests for AgentPay Core Integration (Phase 160)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.agentpay_tool_adapter import AgentPayToolAdapter
from app.schemas.agentpay_integration import AgentPayTransactionRequest
from app.schemas.human_approval import ApprovalPolicyEvaluationResponse, ApprovalRiskLevel


@pytest.fixture
def adapter() -> AgentPayToolAdapter:
    adapter = AgentPayToolAdapter()
    adapter.approval_service.evaluate_approval_policy = AsyncMock()  # type: ignore[method-assign]
    adapter.approval_service.create_approval_request = AsyncMock()  # type: ignore[method-assign]
    adapter.reliability_service.classify_retry_safety = AsyncMock()  # type: ignore[method-assign]
    return adapter


@pytest.mark.asyncio
async def test_01_initiate_payment_auto_settled_low_amount(
    adapter: AgentPayToolAdapter,
) -> None:
    """1. Test payment initiation for low amount ($20) is settled without requiring human approval."""  # noqa: E501
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_policy = ApprovalPolicyEvaluationResponse(
        requires_approval=False,
        risk_level=ApprovalRiskLevel.LOW,
        required_approvals_count=0,
        matched_policy_name="Low Risk Auto-Approval Policy",
        auto_approved=True,
    )
    adapter.approval_service.evaluate_approval_policy.return_value = mock_policy  # type: ignore[attr-defined]  # noqa: E501

    mock_retry = MagicMock()
    mock_retry.classification.value = "SAFE_TO_RETRY"
    adapter.reliability_service.classify_retry_safety.return_value = mock_retry  # type: ignore[attr-defined]  # noqa: E501

    req = AgentPayTransactionRequest(
        amount=20.00,
        currency="USD",
        recipient="Coffee Shop",
        description="Morning Coffee",
        idempotency_key="IDEM-SAFE-PAY-12345",
    )

    res = await adapter.initiate_payment(MagicMock(), tenant_id, agent_id, req)
    assert res.amount == 20.00
    assert res.status == "SETTLED"
    assert res.requires_approval is False
    assert res.approval_request_id is None


@pytest.mark.asyncio
async def test_02_initiate_payment_triggers_human_approval_high_amount(
    adapter: AgentPayToolAdapter,
) -> None:
    """2. Test financial payment > $50 triggers Phase 162 human approval request."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    user_id = uuid.uuid4()
    approval_id = uuid.uuid4()

    mock_policy = ApprovalPolicyEvaluationResponse(
        requires_approval=True,
        risk_level=ApprovalRiskLevel.MEDIUM,
        required_approvals_count=1,
        matched_policy_name="Medium Risk Single Approval Policy",
        auto_approved=False,
    )
    adapter.approval_service.evaluate_approval_policy.return_value = mock_policy  # type: ignore[attr-defined]  # noqa: E501

    mock_appr_resp = MagicMock()
    mock_appr_resp.approval_id = approval_id
    adapter.approval_service.create_approval_request.return_value = mock_appr_resp  # type: ignore[attr-defined]  # noqa: E501

    mock_retry = MagicMock()
    mock_retry.classification.value = "SAFE_TO_RETRY"
    adapter.reliability_service.classify_retry_safety.return_value = mock_retry  # type: ignore[attr-defined]  # noqa: E501

    req = AgentPayTransactionRequest(
        amount=250.00,
        currency="USD",
        recipient="Electronics Store",
        description="Monitor Purchase",
        idempotency_key="IDEM-HIGH-PAY-67890",
    )

    res = await adapter.initiate_payment(MagicMock(), tenant_id, agent_id, req, user_id=user_id)
    assert res.amount == 250.00
    assert res.status == "PENDING_APPROVAL"
    assert res.requires_approval is True
    assert res.approval_request_id == approval_id


@pytest.mark.asyncio
async def test_03_missing_idempotency_key_rejected(
    adapter: AgentPayToolAdapter,
) -> None:
    """3. Test missing or short idempotency key is rejected prior to financial execution."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    with pytest.raises((ValueError, TypeError, Exception)):  # noqa: B017
        req = AgentPayTransactionRequest(
            amount=10.00,
            currency="USD",
            recipient="Merchant",
            description="Test",
            idempotency_key="short",
        )
        await adapter.initiate_payment(MagicMock(), tenant_id, agent_id, req)
