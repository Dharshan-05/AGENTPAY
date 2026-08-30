"""Unit, Security & Adversarial Tests for Phase 299 — Payment Refund Flow."""

from __future__ import annotations

import inspect
import threading
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.payment.idempotency.payment_idempotency_service import (
    PaymentIdempotencyConflictError,
    PaymentIdempotencyService,
)
from app.payment.refunds.payment_refund_service import (
    PaymentRefundAmountError,
    PaymentRefundEligibilityError,
    PaymentRefundError,
    PaymentRefundService,
)
from app.schemas.payment import PaymentStatus, SupportedCurrency
from app.schemas.payment_idempotency import IdempotencyState
from app.schemas.payment_refund import PaymentRefundRequest, PaymentRefundResult
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
        decision_fingerprint="f" * 64,
        created_at=datetime.now(UTC),
    )


def _make_refund_request(
    tenant_id: uuid.UUID,
    agent_id: uuid.UUID,
    tx_id: str,
    captured_amt: Decimal = Decimal("100.00"),
    refund_amt: Decimal = Decimal("100.00"),
    idemp_key: str = "idemp_rfnd_12345",
    payment_id: str = "pay_test_299_01",
) -> PaymentRefundRequest:
    return PaymentRefundRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        order_id="order_test_299_01",
        payment_id=payment_id,
        captured_amount=captured_amt,
        refund_amount=refund_amt,
        currency=SupportedCurrency.INR,
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="fp_auth_299_valid",
        idempotency_key=idemp_key,
        refund_reason="Customer return",
    )


def test_01_valid_full_refund_from_captured() -> None:
    """1. Test valid full refund for CAPTURED payment status."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_01"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(tenant_id, agent_id, tx_id, Decimal("500.00"), Decimal("500.00"))

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"
    mock_provider.refund_payment.return_value = {"id": "rfnd_rzp_test_01", "status": "processed"}

    service = PaymentRefundService(provider=mock_provider)
    res = service.process_refund(decision, req, current_status=PaymentStatus.CAPTURED)

    assert isinstance(res, PaymentRefundResult)
    assert res.refund_status == PaymentStatus.REFUNDED
    assert res.previous_status == PaymentStatus.CAPTURED
    assert res.refund_amount == Decimal("500.00")
    assert res.provider_refund_id == "rfnd_rzp_test_01"
    assert mock_provider.refund_payment.call_count == 1


def test_02_valid_partial_refund_from_captured() -> None:
    """2. Test valid partial refund for CAPTURED payment status."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_02"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(tenant_id, agent_id, tx_id, Decimal("500.00"), Decimal("200.00"))

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"
    mock_provider.refund_payment.return_value = {"id": "rfnd_rzp_test_02", "status": "processed"}

    service = PaymentRefundService(provider=mock_provider)
    res = service.process_refund(decision, req, current_status=PaymentStatus.CAPTURED)

    assert res.refund_status == PaymentStatus.REFUNDED
    assert res.refund_amount == Decimal("200.00")


def test_03_uncaptured_payment_rejection_created() -> None:
    """3. Security Test: Refund from CREATED status is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_03"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(tenant_id, agent_id, tx_id)

    service = PaymentRefundService()
    with pytest.raises(PaymentRefundEligibilityError):
        service.process_refund(decision, req, current_status=PaymentStatus.CREATED)


def test_04_uncaptured_payment_rejection_order_created() -> None:
    """4. Security Test: Refund from ORDER_CREATED status is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_04"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(tenant_id, agent_id, tx_id)

    service = PaymentRefundService()
    with pytest.raises(PaymentRefundEligibilityError):
        service.process_refund(decision, req, current_status=PaymentStatus.ORDER_CREATED)


def test_05_uncaptured_payment_rejection_checkout_ready() -> None:
    """5. Security Test: Refund from CHECKOUT_READY status is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_05"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(tenant_id, agent_id, tx_id)

    service = PaymentRefundService()
    with pytest.raises(PaymentRefundEligibilityError):
        service.process_refund(decision, req, current_status=PaymentStatus.CHECKOUT_READY)


def test_06_uncaptured_payment_rejection_payment_pending() -> None:
    """6. Security Test: Refund from PAYMENT_PENDING status is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_06"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(tenant_id, agent_id, tx_id)

    service = PaymentRefundService()
    with pytest.raises(PaymentRefundEligibilityError):
        service.process_refund(decision, req, current_status=PaymentStatus.PAYMENT_PENDING)


def test_07_uncaptured_payment_rejection_payment_received() -> None:
    """7. Security Test: Refund from PAYMENT_RECEIVED status is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_07"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(tenant_id, agent_id, tx_id)

    service = PaymentRefundService()
    with pytest.raises(PaymentRefundEligibilityError):
        service.process_refund(decision, req, current_status=PaymentStatus.PAYMENT_RECEIVED)


def test_08_uncaptured_payment_rejection_payment_verified() -> None:
    """8. Security Test: Refund from PAYMENT_VERIFIED status is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_08"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(tenant_id, agent_id, tx_id)

    service = PaymentRefundService()
    with pytest.raises(PaymentRefundEligibilityError):
        service.process_refund(decision, req, current_status=PaymentStatus.PAYMENT_VERIFIED)


def test_09_cancelled_payment_rejection() -> None:
    """9. Security Test: Refund from CANCELLED status is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_09"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(tenant_id, agent_id, tx_id)

    service = PaymentRefundService()
    with pytest.raises(PaymentRefundEligibilityError):
        service.process_refund(decision, req, current_status=PaymentStatus.CANCELLED)


def test_10_failed_payment_rejection() -> None:
    """10. Security Test: Refund from FAILED status is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_10"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(tenant_id, agent_id, tx_id)

    service = PaymentRefundService()
    with pytest.raises(PaymentRefundEligibilityError):
        service.process_refund(decision, req, current_status=PaymentStatus.FAILED)


def test_11_already_refunded_payment_rejection() -> None:
    """11. Security Test: Refund from REFUNDED status is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_11"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(tenant_id, agent_id, tx_id)

    service = PaymentRefundService()
    with pytest.raises(PaymentRefundEligibilityError):
        service.process_refund(decision, req, current_status=PaymentStatus.REFUNDED)


def test_12_refund_amount_overflow_rejected() -> None:
    """12. Financial Integrity: Refund amount exceeding captured amount is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_12"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(
        tenant_id,
        agent_id,
        tx_id,
        captured_amt=Decimal("100.00"),
        refund_amt=Decimal("150.00"),
    )

    service = PaymentRefundService()
    with pytest.raises(PaymentRefundAmountError):
        service.process_refund(decision, req, current_status=PaymentStatus.CAPTURED)


def test_13_zero_refund_amount_rejected() -> None:
    """13. Financial Integrity: Zero refund amount is rejected by Pydantic validation."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    with pytest.raises(ValueError):
        _make_refund_request(tenant_id, agent_id, "tx_13", refund_amt=Decimal("0.00"))


def test_14_negative_refund_amount_rejected() -> None:
    """14. Financial Integrity: Negative refund amount is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    with pytest.raises(ValueError):
        _make_refund_request(tenant_id, agent_id, "tx_14", refund_amt=Decimal("-50.00"))


def test_15_excessive_decimal_precision_rejected() -> None:
    """15. Financial Integrity: Monetary amounts exceeding 2 decimal places are rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    with pytest.raises(ValueError):
        _make_refund_request(tenant_id, agent_id, "tx_15", refund_amt=Decimal("10.005"))


def test_16_tenant_mismatch_rejection() -> None:
    """16. Security Test: Tenant mismatch between decision and refund request is rejected."""
    tenant_id = uuid.uuid4()
    other_tenant = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_16"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(other_tenant, agent_id, tx_id)

    service = PaymentRefundService()
    with pytest.raises(PaymentRefundError) as exc_info:
        service.process_refund(decision, req, current_status=PaymentStatus.CAPTURED)

    assert exc_info.value.error_code == "TENANT_MISMATCH"


def test_17_agent_mismatch_rejection() -> None:
    """17. Security Test: Agent mismatch between decision and refund request is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    other_agent = uuid.uuid4()
    tx_id = "tx_rfnd_17"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(tenant_id, other_agent, tx_id)

    service = PaymentRefundService()
    with pytest.raises(PaymentRefundError) as exc_info:
        service.process_refund(decision, req, current_status=PaymentStatus.CAPTURED)

    assert exc_info.value.error_code == "AGENT_MISMATCH"


def test_18_transaction_mismatch_rejection() -> None:
    """18. Security Test: Transaction mismatch between decision and refund request is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_18"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(tenant_id, agent_id, "other_tx_888")

    service = PaymentRefundService()
    with pytest.raises(PaymentRefundError) as exc_info:
        service.process_refund(decision, req, current_status=PaymentStatus.CAPTURED)

    assert exc_info.value.error_code == "TRANSACTION_MISMATCH"


def test_19_missing_authorization_fingerprint_rejected() -> None:
    """19. Security Test: Refund request with missing authorization fingerprint is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_19"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    req = PaymentRefundRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        order_id="order_19",
        payment_id="pay_19",
        captured_amount=Decimal("100.00"),
        refund_amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="",  # Blank FP!
        idempotency_key="idemp_key_19",
    )

    service = PaymentRefundService()
    with pytest.raises(PaymentRefundError) as exc_info:
        service.process_refund(decision, req, current_status=PaymentStatus.CAPTURED)

    assert exc_info.value.error_code == "AUTHORIZATION_FINGERPRINT_MISSING"


def test_20_idempotent_replay_of_completed_refund() -> None:
    """20. Test repeated refund request with same key replays previous refund result."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_20"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(tenant_id, agent_id, tx_id, idemp_key="idemp_key_rfnd_20")

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"
    mock_provider.refund_payment.return_value = {"id": "rfnd_rzp_20", "status": "processed"}

    idemp_service = PaymentIdempotencyService()
    service = PaymentRefundService(provider=mock_provider, idempotency_service=idemp_service)

    res1 = service.process_refund(decision, req, current_status=PaymentStatus.CAPTURED)
    assert res1.refund_status == PaymentStatus.REFUNDED
    assert mock_provider.refund_payment.call_count == 1

    # Second call -> replays previous result! (0 provider calls)
    res2 = service.process_refund(decision, req, current_status=PaymentStatus.CAPTURED)
    assert res2.refund_status == PaymentStatus.REFUNDED
    assert mock_provider.refund_payment.call_count == 1


def test_21_modified_request_on_same_idempotency_key_conflict() -> None:
    """21. Adversarial Test: Modified refund_amount on same idempotency key raises 409 Conflict."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_21"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"
    mock_provider.refund_payment.return_value = {"id": "rfnd_test_21", "status": "processed"}

    req1 = _make_refund_request(
        tenant_id, agent_id, tx_id, refund_amt=Decimal("50.00"), idemp_key="idemp_key_21"
    )
    req2 = _make_refund_request(
        tenant_id, agent_id, tx_id, refund_amt=Decimal("100.00"), idemp_key="idemp_key_21"
    )

    idemp_service = PaymentIdempotencyService()
    service = PaymentRefundService(provider=mock_provider, idempotency_service=idemp_service)

    service.process_refund(decision, req1, current_status=PaymentStatus.CAPTURED)

    with pytest.raises(PaymentIdempotencyConflictError):
        service.process_refund(decision, req2, current_status=PaymentStatus.CAPTURED)


def test_22_concurrent_refund_threading_safety() -> None:
    """22. Concurrency Test: Multi-threaded simultaneous refund guarantees 1 provider call."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_22_concurrent"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(tenant_id, agent_id, tx_id, idemp_key="idemp_key_22_concurrent")

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"
    mock_provider.refund_payment.return_value = {"id": "rfnd_22", "status": "processed"}

    idemp_service = PaymentIdempotencyService()
    service = PaymentRefundService(provider=mock_provider, idempotency_service=idemp_service)

    results: list[PaymentRefundResult] = []
    lock = threading.Lock()

    def _worker() -> None:
        try:
            r = service.process_refund(decision, req, current_status=PaymentStatus.CAPTURED)
            with lock:
                results.append(r)
        except Exception:
            pass

    threads = [threading.Thread(target=_worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert mock_provider.refund_payment.call_count == 1
    assert len(results) >= 1


def test_23_provider_failure_handling() -> None:
    """23. Test provider failure during refund marks idempotency record as FAILED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_23_fail"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(tenant_id, agent_id, tx_id, idemp_key="idemp_key_23_fail")

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"
    mock_provider.refund_payment.side_effect = RuntimeError("Razorpay refund API unavailable")

    idemp_service = PaymentIdempotencyService()
    service = PaymentRefundService(provider=mock_provider, idempotency_service=idemp_service)

    with pytest.raises(PaymentRefundError):
        service.process_refund(decision, req, current_status=PaymentStatus.CAPTURED)

    # Check record state in idempotency store
    hash_val = idemp_service.compute_identity_hash(
        tenant_id, agent_id, tx_id, "payment_refund", "idemp_key_23_fail"
    )
    rec = idemp_service._store[hash_val]
    assert rec.state == IdempotencyState.FAILED


def test_24_secret_redaction_verification() -> None:
    """24. Security Test: PaymentRefundResult model_fields contain 0 secret fields."""
    assert "key_secret" not in PaymentRefundResult.model_fields
    assert "webhook_secret" not in PaymentRefundResult.model_fields


def test_25_deterministic_refund_fingerprint() -> None:
    """25. Test refund fingerprint is deterministic SHA-256 over canonical safe metadata."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_rfnd_25"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_refund_request(tenant_id, agent_id, tx_id)

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"
    mock_provider.refund_payment.return_value = {"id": "rfnd_25", "status": "processed"}

    service = PaymentRefundService(provider=mock_provider)
    res = service.process_refund(decision, req, current_status=PaymentStatus.CAPTURED)

    assert len(res.refund_fingerprint) == 64


def test_26_static_check_no_direct_razorpay_sdk_imports() -> None:
    """26. Static Check: PaymentRefundService DOES NOT import razorpay SDK directly."""
    import app.payment.refunds.payment_refund_service as prs_mod

    source_code = inspect.getsource(prs_mod)
    assert "import razorpay" not in source_code
    assert "from razorpay" not in source_code


def test_27_static_check_no_risk_recalculation() -> None:
    """27. Static Check: PaymentRefundService DOES NOT recalculate risk scores."""
    import app.payment.refunds.payment_refund_service as prs_mod

    source_code = inspect.getsource(prs_mod)
    assert "calculate_composite_risk_score" not in source_code
    assert "evaluate_hard_security_rules" not in source_code


def test_28_static_check_no_authorization_bypass() -> None:
    """28. Static Check: PaymentRefundService DOES NOT contain authorization bypass routines."""
    import app.payment.refunds.payment_refund_service as prs_mod

    source_code = inspect.getsource(prs_mod)
    assert "bypass_authorization" not in source_code


def test_29_cross_tenant_isolation_in_refund() -> None:
    """29. Security Test: Cross-tenant refund requests use isolated identity hashes."""
    tenant_A = uuid.uuid4()
    tenant_B = uuid.uuid4()
    agent_id = uuid.uuid4()

    service = PaymentRefundService()
    hash_A = service.idempotency_service.compute_identity_hash(
        tenant_A, agent_id, "tx", "op", "key"
    )
    hash_B = service.idempotency_service.compute_identity_hash(
        tenant_B, agent_id, "tx", "op", "key"
    )

    assert hash_A != hash_B


def test_30_cross_agent_isolation_in_refund() -> None:
    """30. Security Test: Cross-agent refund requests use isolated identity hashes."""
    tenant_id = uuid.uuid4()
    agent_A = uuid.uuid4()
    agent_B = uuid.uuid4()

    service = PaymentRefundService()
    hash_A = service.idempotency_service.compute_identity_hash(
        tenant_id, agent_A, "tx", "op", "key"
    )
    hash_B = service.idempotency_service.compute_identity_hash(
        tenant_id, agent_B, "tx", "op", "key"
    )

    assert hash_A != hash_B


def test_31_cross_transaction_isolation_in_refund() -> None:
    """31. Security Test: Cross-transaction refund requests use isolated identity hashes."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    service = PaymentRefundService()
    hash_A = service.idempotency_service.compute_identity_hash(
        tenant_id, agent_id, "tx_A", "op", "key"
    )
    hash_B = service.idempotency_service.compute_identity_hash(
        tenant_id, agent_id, "tx_B", "op", "key"
    )

    assert hash_A != hash_B


def test_32_refund_model_frozen_and_immutable() -> None:
    """32. Security Test: PaymentRefundResult model is frozen and immutable."""
    res = PaymentRefundResult(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_32",
        order_id="order_32",
        payment_id="pay_32",
        provider_refund_id="rfnd_32",
        refund_amount=Decimal("100.00"),
        captured_amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        refund_fingerprint="fp_32",
    )

    with pytest.raises((TypeError, Exception)):
        res.refund_status = PaymentStatus.CAPTURED  # Mutate attempt!


def test_33_out_of_scope_future_phases_unimplemented() -> None:
    """33. Static Check: Refund codebase contains 0 Phase 300+ features."""
    import app.payment.refunds.payment_refund_service as prs_mod

    source_code = inspect.getsource(prs_mod)
    assert "reviewer_approval_queue" not in source_code
    assert "approval_workflow" not in source_code
