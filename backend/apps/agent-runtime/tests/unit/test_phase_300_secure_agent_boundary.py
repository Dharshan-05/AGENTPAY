"""Unit, Security & Adversarial Tests for Phase 300 — Secure Agent-to-Razorpay Boundary."""

from __future__ import annotations

import inspect
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.payment.boundary.agent_payment_boundary import (
    AgentPaymentBoundary,
    AgentPaymentBoundaryError,
)
from app.schemas.agent_payment_boundary import (
    AgentPaymentCommand,
    AgentPaymentOperation,
    AgentPaymentResponse,
)
from app.schemas.payment import (
    PaymentOrderResult,
    PaymentStatus,
    RazorpayCheckoutConfig,
    SupportedCurrency,
)
from app.schemas.payment_cancellation import PaymentCancellationResult
from app.schemas.payment_refund import PaymentRefundResult
from app.schemas.risk_engine import (
    FinalRiskDecision,
    FinalRiskDecisionResult,
    RiskThresholdBand,
)


def _make_decision_result(
    tenant_id: uuid.UUID, agent_id: uuid.UUID, tx_id: str
) -> FinalRiskDecisionResult:
    return FinalRiskDecisionResult(
        evaluation_id=uuid.uuid4(),
        decision_id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        prediction_timestamp=datetime.now(UTC),
        decision=FinalRiskDecision.ALLOW,
        decision_reason="LOW_RISK_PERMITTED",
        composite_risk_score=10.0,
        risk_band=RiskThresholdBand.LOW_RISK_BAND,
        policy_precedence="ALLOW",
        hard_security_status="PASSED",
        triggered_rule_ids=[],
        review_reasons=[],
        block_reasons=[],
        available_signal_types=["FRAUDGUARD"],
        unavailable_signal_types=[],
        cold_start=False,
        policy_authoritative=True,
        threshold_configuration_version="1.0.0",
        threshold_configuration_hash="t" * 64,
        weight_configuration_version="1.0.0",
        weight_configuration_hash="w" * 64,
        source_fingerprints=["s" * 64],
        calculation_fingerprint="c" * 64,
        decision_fingerprint="fp_auth_300_valid",
        created_at=datetime.now(UTC),
    )


def test_01_valid_create_order_command() -> None:
    """1. Test valid CREATE_ORDER command via AgentPaymentBoundary."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_bnd_01"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    cmd = AgentPaymentCommand(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        operation=AgentPaymentOperation.CREATE_ORDER,
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="fp_auth_300_valid",
        idempotency_key="idemp_bnd_01_key",
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
    )

    mock_payment_svc = MagicMock()
    mock_order_res = PaymentOrderResult(
        order_id="order_rzp_300_01",
        provider_name="razorpay",
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        amount_minor_units=10000,
        currency=SupportedCurrency.INR,
        status="created",
        idempotency_key="idemp_bnd_01_key",
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="fp_auth_300_valid",
    )
    mock_payment_svc.create_payment_order.return_value = mock_order_res

    boundary = AgentPaymentBoundary(payment_service=mock_payment_svc)
    res = boundary.execute_agent_command(decision, cmd)

    assert isinstance(res, AgentPaymentResponse)
    assert res.operation == AgentPaymentOperation.CREATE_ORDER
    assert res.status == "ORDER_CREATED"
    assert len(res.command_fingerprint) == 64


def test_02_valid_checkout_command() -> None:
    """2. Test valid CHECKOUT command via AgentPaymentBoundary."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_bnd_02"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    cmd = AgentPaymentCommand(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        operation=AgentPaymentOperation.CHECKOUT,
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="fp_auth_300_valid",
        idempotency_key="idemp_bnd_02_key",
        order_id="order_rzp_300_02",
        amount=Decimal("250.00"),
        currency=SupportedCurrency.INR,
    )

    mock_payment_svc = MagicMock()
    mock_checkout_res = RazorpayCheckoutConfig(
        key_id="rzp_test_public_key",
        order_id="order_rzp_300_02",
        amount=Decimal("250.00"),
        amount_minor_units=25000,
        currency=SupportedCurrency.INR,
        description="Checkout modal",
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
    )
    mock_payment_svc.generate_checkout_configuration.return_value = mock_checkout_res

    boundary = AgentPaymentBoundary(payment_service=mock_payment_svc)
    res = boundary.execute_agent_command(decision, cmd)

    assert res.operation == AgentPaymentOperation.CHECKOUT
    assert res.status == "CHECKOUT_CONFIGURED"


def test_03_valid_cancel_command() -> None:
    """3. Test valid CANCEL command via AgentPaymentBoundary."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_bnd_03"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    cmd = AgentPaymentCommand(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        operation=AgentPaymentOperation.CANCEL,
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="fp_auth_300_valid",
        idempotency_key="idemp_bnd_03_key",
        order_id="order_rzp_300_03",
        reason="Agent requested cancellation",
    )

    mock_cancel_svc = MagicMock()
    mock_cancel_res = PaymentCancellationResult(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        order_id="order_rzp_300_03",
        previous_status=PaymentStatus.ORDER_CREATED,
        cancellation_fingerprint="fp_cncl_03",
    )
    mock_cancel_svc.cancel_payment.return_value = mock_cancel_res

    boundary = AgentPaymentBoundary(cancellation_service=mock_cancel_svc)
    res = boundary.execute_agent_command(decision, cmd)

    assert res.operation == AgentPaymentOperation.CANCEL
    assert res.status == "CANCELLED"


def test_04_valid_refund_command() -> None:
    """4. Test valid REFUND command via AgentPaymentBoundary."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_bnd_04"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    cmd = AgentPaymentCommand(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        operation=AgentPaymentOperation.REFUND,
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="fp_auth_300_valid",
        idempotency_key="idemp_bnd_04_key",
        order_id="order_rzp_300_04",
        payment_id="pay_rzp_300_04",
        captured_amount=Decimal("500.00"),
        refund_amount=Decimal("500.00"),
        currency=SupportedCurrency.INR,
        reason="Full refund",
    )

    mock_refund_svc = MagicMock()
    mock_refund_res = PaymentRefundResult(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        order_id="order_rzp_300_04",
        payment_id="pay_rzp_300_04",
        provider_refund_id="rfnd_04",
        refund_amount=Decimal("500.00"),
        captured_amount=Decimal("500.00"),
        currency=SupportedCurrency.INR,
        refund_fingerprint="fp_rfnd_04",
    )
    mock_refund_svc.process_refund.return_value = mock_refund_res

    boundary = AgentPaymentBoundary(refund_service=mock_refund_svc)
    res = boundary.execute_agent_command(decision, cmd)

    assert res.operation == AgentPaymentOperation.REFUND
    assert res.status == "REFUNDED"


def test_05_tenant_spoofing_rejection() -> None:
    """5. Security Test: Agent attempting tenant spoofing is rejected."""
    tenant_id = uuid.uuid4()
    other_tenant = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_bnd_05"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    cmd = AgentPaymentCommand(
        tenant_id=other_tenant,  # Spoofed tenant!
        agent_id=agent_id,
        transaction_id=tx_id,
        operation=AgentPaymentOperation.CREATE_ORDER,
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="fp_auth_300_valid",
        idempotency_key="idemp_bnd_05",
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
    )

    boundary = AgentPaymentBoundary()
    with pytest.raises(AgentPaymentBoundaryError) as exc_info:
        boundary.execute_agent_command(decision, cmd)

    assert exc_info.value.error_code == "TENANT_MISMATCH"


def test_06_agent_spoofing_rejection() -> None:
    """6. Security Test: Agent attempting agent ID spoofing is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    other_agent = uuid.uuid4()
    tx_id = "tx_bnd_06"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    cmd = AgentPaymentCommand(
        tenant_id=tenant_id,
        agent_id=other_agent,  # Spoofed agent!
        transaction_id=tx_id,
        operation=AgentPaymentOperation.CREATE_ORDER,
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="fp_auth_300_valid",
        idempotency_key="idemp_bnd_06",
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
    )

    boundary = AgentPaymentBoundary()
    with pytest.raises(AgentPaymentBoundaryError) as exc_info:
        boundary.execute_agent_command(decision, cmd)

    assert exc_info.value.error_code == "AGENT_MISMATCH"


def test_07_transaction_spoofing_rejection() -> None:
    """7. Security Test: Agent attempting transaction ID spoofing is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_bnd_07"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    cmd = AgentPaymentCommand(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="other_tx_999",  # Spoofed tx!
        operation=AgentPaymentOperation.CREATE_ORDER,
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="fp_auth_300_valid",
        idempotency_key="idemp_bnd_07",
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
    )

    boundary = AgentPaymentBoundary()
    with pytest.raises(AgentPaymentBoundaryError) as exc_info:
        boundary.execute_agent_command(decision, cmd)

    assert exc_info.value.error_code == "TRANSACTION_MISMATCH"


def test_08_missing_authorization_fingerprint_rejected() -> None:
    """8. Security Test: Command with missing authorization fingerprint is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_bnd_08"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    cmd = AgentPaymentCommand(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        operation=AgentPaymentOperation.CREATE_ORDER,
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="",  # Blank FP!
        idempotency_key="idemp_bnd_08",
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
    )

    boundary = AgentPaymentBoundary()
    with pytest.raises(AgentPaymentBoundaryError) as exc_info:
        boundary.execute_agent_command(decision, cmd)

    assert exc_info.value.error_code == "AUTHORIZATION_FINGERPRINT_MISSING"


def test_09_secret_redaction_in_agent_response() -> None:
    """9. Security Test: AgentPaymentResponse model_fields contain 0 secret fields."""
    assert "key_secret" not in AgentPaymentResponse.model_fields
    assert "webhook_secret" not in AgentPaymentResponse.model_fields


def test_10_static_check_no_direct_razorpay_sdk_imports() -> None:
    """10. Static Check: AgentPaymentBoundary DOES NOT import razorpay SDK directly."""
    import app.payment.boundary.agent_payment_boundary as apb_mod

    source_code = inspect.getsource(apb_mod)
    assert "import razorpay" not in source_code
    assert "from razorpay" not in source_code


def test_11_static_check_no_authorization_bypass() -> None:
    """11. Static Check: AgentPaymentBoundary DOES NOT contain authorization bypass routines."""
    import app.payment.boundary.agent_payment_boundary as apb_mod

    source_code = inspect.getsource(apb_mod)
    assert "bypass_authorization" not in source_code


def test_12_static_check_no_risk_recalculation() -> None:
    """12. Static Check: AgentPaymentBoundary DOES NOT recalculate risk score."""
    import app.payment.boundary.agent_payment_boundary as apb_mod

    source_code = inspect.getsource(apb_mod)
    assert "calculate_composite_risk_score" not in source_code


def test_13_agent_command_forbids_extra_fields() -> None:
    """13. Security Test: AgentPaymentCommand rejects extra injected fields (extra='forbid')."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    with pytest.raises(ValueError):
        AgentPaymentCommand.model_validate(
            {
                "tenant_id": str(tenant_id),
                "agent_id": str(agent_id),
                "transaction_id": "tx_13",
                "operation": "create_order",
                "authorization_id": str(uuid.uuid4()),
                "authorization_fingerprint": "fp_13",
                "idempotency_key": "idemp_key_13",
                "amount": "100.00",
                "currency": "INR",
                "key_secret": "injected_secret_val",  # Extra secret injection attempt!
            }
        )


def test_14_agent_response_model_frozen() -> None:
    """14. Security Test: AgentPaymentResponse model is frozen and immutable."""
    res = AgentPaymentResponse(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_14",
        operation=AgentPaymentOperation.CREATE_ORDER,
        status="ORDER_CREATED",
        command_fingerprint="fp_14",
        result_payload={},
    )

    with pytest.raises((TypeError, Exception)):
        res.status = "CAPTURED"  # Mutate attempt!
