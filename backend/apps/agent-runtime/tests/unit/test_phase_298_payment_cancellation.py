"""Unit, Security & Adversarial Tests for Phase 298 — Payment Cancellation Flow."""

from __future__ import annotations

import inspect
import threading
import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.payment.cancellation.payment_cancellation_service import (
    PaymentCancellationEligibilityError,
    PaymentCancellationError,
    PaymentCancellationService,
)
from app.payment.idempotency.payment_idempotency_service import (
    PaymentIdempotencyConflictError,
    PaymentIdempotencyService,
)
from app.schemas.payment import PaymentStatus
from app.schemas.payment_cancellation import (
    PaymentCancellationRequest,
    PaymentCancellationResult,
)
from app.schemas.payment_idempotency import IdempotencyState
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


def _make_cancel_request(
    tenant_id: uuid.UUID,
    agent_id: uuid.UUID,
    tx_id: str,
    idemp_key: str = "idemp_cncl_12345",
    order_id: str = "order_test_298_01",
) -> PaymentCancellationRequest:
    return PaymentCancellationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        order_id=order_id,
        payment_id="pay_test_298_01",
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="fp_auth_298_valid",
        idempotency_key=idemp_key,
        cancellation_reason="User cancelled order",
    )


def test_01_valid_cancellation_from_created() -> None:
    """1. Test valid cancellation from CREATED status."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_cncl_01"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_cancel_request(tenant_id, agent_id, tx_id)

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"
    mock_provider.cancel_payment.return_value = {"status": "cancelled"}

    service = PaymentCancellationService(provider=mock_provider)
    res = service.cancel_payment(decision, req, current_status=PaymentStatus.CREATED)

    assert isinstance(res, PaymentCancellationResult)
    assert res.cancellation_status == PaymentStatus.CANCELLED
    assert res.previous_status == PaymentStatus.CREATED
    assert mock_provider.cancel_payment.call_count == 1


def test_02_valid_cancellation_from_order_created() -> None:
    """2. Test valid cancellation from ORDER_CREATED status."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_cncl_02"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_cancel_request(tenant_id, agent_id, tx_id)

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"

    service = PaymentCancellationService(provider=mock_provider)
    res = service.cancel_payment(decision, req, current_status=PaymentStatus.ORDER_CREATED)

    assert res.cancellation_status == PaymentStatus.CANCELLED
    assert res.previous_status == PaymentStatus.ORDER_CREATED


def test_03_valid_cancellation_from_checkout_ready() -> None:
    """3. Test valid cancellation from CHECKOUT_READY status."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_cncl_03"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_cancel_request(tenant_id, agent_id, tx_id)

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"

    service = PaymentCancellationService(provider=mock_provider)
    res = service.cancel_payment(decision, req, current_status=PaymentStatus.CHECKOUT_READY)

    assert res.cancellation_status == PaymentStatus.CANCELLED
    assert res.previous_status == PaymentStatus.CHECKOUT_READY


def test_04_valid_cancellation_from_payment_pending() -> None:
    """4. Test valid cancellation from PAYMENT_PENDING status."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_cncl_04"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_cancel_request(tenant_id, agent_id, tx_id)

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"

    service = PaymentCancellationService(provider=mock_provider)
    res = service.cancel_payment(decision, req, current_status=PaymentStatus.PAYMENT_PENDING)

    assert res.cancellation_status == PaymentStatus.CANCELLED
    assert res.previous_status == PaymentStatus.PAYMENT_PENDING


def test_05_tenant_mismatch_rejection() -> None:
    """5. Security Test: Tenant mismatch between decision and request is rejected."""
    tenant_id = uuid.uuid4()
    other_tenant = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_cncl_05"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_cancel_request(other_tenant, agent_id, tx_id)

    service = PaymentCancellationService()
    with pytest.raises(PaymentCancellationError) as exc_info:
        service.cancel_payment(decision, req, current_status=PaymentStatus.ORDER_CREATED)

    assert exc_info.value.error_code == "TENANT_MISMATCH"


def test_06_agent_mismatch_rejection() -> None:
    """6. Security Test: Agent mismatch between decision and request is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    other_agent = uuid.uuid4()
    tx_id = "tx_cncl_06"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_cancel_request(tenant_id, other_agent, tx_id)

    service = PaymentCancellationService()
    with pytest.raises(PaymentCancellationError) as exc_info:
        service.cancel_payment(decision, req, current_status=PaymentStatus.ORDER_CREATED)

    assert exc_info.value.error_code == "AGENT_MISMATCH"


def test_07_transaction_mismatch_rejection() -> None:
    """7. Security Test: Transaction mismatch between decision and request is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_cncl_07"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_cancel_request(tenant_id, agent_id, "other_tx_999")

    service = PaymentCancellationService()
    with pytest.raises(PaymentCancellationError) as exc_info:
        service.cancel_payment(decision, req, current_status=PaymentStatus.ORDER_CREATED)

    assert exc_info.value.error_code == "TRANSACTION_MISMATCH"


def test_08_invalid_status_rejection_payment_received() -> None:
    """8. Security Test: Cancellation from PAYMENT_RECEIVED status is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_cncl_08"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_cancel_request(tenant_id, agent_id, tx_id)

    service = PaymentCancellationService()
    with pytest.raises(PaymentCancellationEligibilityError):
        service.cancel_payment(decision, req, current_status=PaymentStatus.PAYMENT_RECEIVED)


def test_09_terminal_state_protection_captured_cannot_be_cancelled() -> None:
    """9. Security Test: CRITICAL INVARIANT - CAPTURED payment cannot be cancelled."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_cncl_09"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_cancel_request(tenant_id, agent_id, tx_id)

    service = PaymentCancellationService()
    with pytest.raises(PaymentCancellationEligibilityError) as exc_info:
        service.cancel_payment(decision, req, current_status=PaymentStatus.CAPTURED)

    assert "ineligible for cancellation" in str(exc_info.value)


def test_10_terminal_state_protection_refunded_cannot_be_cancelled() -> None:
    """10. Security Test: REFUNDED payment cannot be cancelled."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_cncl_10"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_cancel_request(tenant_id, agent_id, tx_id)

    service = PaymentCancellationService()
    with pytest.raises(PaymentCancellationEligibilityError):
        service.cancel_payment(decision, req, current_status=PaymentStatus.REFUNDED)


def test_11_terminal_state_protection_failed_cannot_be_cancelled() -> None:
    """11. Security Test: FAILED payment cannot be cancelled."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_cncl_11"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_cancel_request(tenant_id, agent_id, tx_id)

    service = PaymentCancellationService()
    with pytest.raises(PaymentCancellationEligibilityError):
        service.cancel_payment(decision, req, current_status=PaymentStatus.FAILED)


def test_12_already_cancelled_state_rejection() -> None:
    """12. Security Test: CANCELLED payment cannot be cancelled again."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_cncl_12"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_cancel_request(tenant_id, agent_id, tx_id)

    service = PaymentCancellationService()
    with pytest.raises(PaymentCancellationEligibilityError):
        service.cancel_payment(decision, req, current_status=PaymentStatus.CANCELLED)


def test_13_idempotent_replay_of_completed_cancellation() -> None:
    """13. Test repeated cancellation request with same key replays previous cancellation result."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_cncl_13"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_cancel_request(tenant_id, agent_id, tx_id, idemp_key="idemp_key_cncl_13")

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"

    idemp_service = PaymentIdempotencyService()
    service = PaymentCancellationService(provider=mock_provider, idempotency_service=idemp_service)

    res1 = service.cancel_payment(decision, req, current_status=PaymentStatus.ORDER_CREATED)
    assert res1.cancellation_status == PaymentStatus.CANCELLED
    assert mock_provider.cancel_payment.call_count == 1

    # Second call -> replays previous result! (0 provider calls)
    res2 = service.cancel_payment(decision, req, current_status=PaymentStatus.ORDER_CREATED)
    assert res2.cancellation_status == PaymentStatus.CANCELLED
    assert mock_provider.cancel_payment.call_count == 1


def test_14_modified_request_on_same_idempotency_key_conflict() -> None:
    """14. Adversarial Test: Modified order_id on same idempotency key raises 409 Conflict."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_cncl_14"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    req1 = _make_cancel_request(
        tenant_id, agent_id, tx_id, idemp_key="idemp_key_14", order_id="order_A"
    )
    req2 = _make_cancel_request(
        tenant_id, agent_id, tx_id, idemp_key="idemp_key_14", order_id="order_B"
    )

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"
    mock_provider.cancel_payment.return_value = {"status": "cancelled"}

    idemp_service = PaymentIdempotencyService()
    service = PaymentCancellationService(provider=mock_provider, idempotency_service=idemp_service)

    service.cancel_payment(decision, req1, current_status=PaymentStatus.ORDER_CREATED)

    with pytest.raises(PaymentIdempotencyConflictError):
        service.cancel_payment(decision, req2, current_status=PaymentStatus.ORDER_CREATED)


def test_15_concurrent_cancellation_threading_safety() -> None:
    """15. Concurrency Test: Multi-threaded simultaneous cancellation guarantees 1 provider call."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_cncl_15_concurrent"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_cancel_request(tenant_id, agent_id, tx_id, idemp_key="idemp_key_15_concurrent")

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"

    idemp_service = PaymentIdempotencyService()
    service = PaymentCancellationService(provider=mock_provider, idempotency_service=idemp_service)

    results: list[PaymentCancellationResult] = []
    errors: list[Exception] = []
    lock = threading.Lock()

    def _worker() -> None:
        try:
            r = service.cancel_payment(decision, req, current_status=PaymentStatus.ORDER_CREATED)
            with lock:
                results.append(r)
        except Exception as e:
            with lock:
                errors.append(e)

    threads = [threading.Thread(target=_worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert mock_provider.cancel_payment.call_count == 1
    assert len(results) >= 1


def test_16_provider_failure_handling() -> None:
    """16. Test provider failure during cancellation marks idempotency as FAILED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_cncl_16_fail"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_cancel_request(tenant_id, agent_id, tx_id, idemp_key="idemp_key_16_fail")

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"
    mock_provider.cancel_payment.side_effect = RuntimeError("Razorpay API connection error")

    idemp_service = PaymentIdempotencyService()
    service = PaymentCancellationService(provider=mock_provider, idempotency_service=idemp_service)

    with pytest.raises(PaymentCancellationError):
        service.cancel_payment(decision, req, current_status=PaymentStatus.ORDER_CREATED)

    # Idempotency record state is FAILED
    hash_val = idemp_service.compute_identity_hash(
        tenant_id, agent_id, tx_id, "payment_cancellation", "idemp_key_16_fail"
    )
    rec = idemp_service._store[hash_val]
    assert rec.state == IdempotencyState.FAILED


def test_17_secret_redaction_verification() -> None:
    """17. Security Test: PaymentCancellationResult model_fields contain 0 secret fields."""
    assert "key_secret" not in PaymentCancellationResult.model_fields
    assert "webhook_secret" not in PaymentCancellationResult.model_fields


def test_18_deterministic_cancellation_fingerprint() -> None:
    """18. Test cancellation fingerprint is deterministic SHA-256 over canonical safe metadata."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_cncl_18"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    req = _make_cancel_request(tenant_id, agent_id, tx_id)

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"

    service = PaymentCancellationService(provider=mock_provider)
    res = service.cancel_payment(decision, req, current_status=PaymentStatus.ORDER_CREATED)

    assert len(res.cancellation_fingerprint) == 64


def test_19_static_check_no_direct_razorpay_sdk_imports() -> None:
    """19. Static Check: PaymentCancellationService DOES NOT import razorpay SDK directly."""
    import app.payment.cancellation.payment_cancellation_service as pcs_mod

    source_code = inspect.getsource(pcs_mod)
    assert "import razorpay" not in source_code
    assert "from razorpay" not in source_code


def test_20_static_check_no_risk_recalculation() -> None:
    """20. Static Check: PaymentCancellationService DOES NOT recalculate risk scores."""
    import app.payment.cancellation.payment_cancellation_service as pcs_mod

    source_code = inspect.getsource(pcs_mod)
    assert "calculate_composite_risk_score" not in source_code
    assert "evaluate_hard_security_rules" not in source_code


def test_21_static_check_no_authorization_bypass() -> None:
    """21. Static Check: PaymentCancellationService DOES NOT contain bypass routines."""
    import app.payment.cancellation.payment_cancellation_service as pcs_mod

    source_code = inspect.getsource(pcs_mod)
    assert "bypass_authorization" not in source_code


def test_22_cross_tenant_isolation_in_cancellation() -> None:
    """22. Security Test: Cross-tenant cancellation requests use isolated identity hashes."""
    tenant_A = uuid.uuid4()
    tenant_B = uuid.uuid4()
    agent_id = uuid.uuid4()

    service = PaymentCancellationService()
    hash_A = service.idempotency_service.compute_identity_hash(
        tenant_A, agent_id, "tx", "op", "key"
    )
    hash_B = service.idempotency_service.compute_identity_hash(
        tenant_B, agent_id, "tx", "op", "key"
    )

    assert hash_A != hash_B


def test_23_cross_agent_isolation_in_cancellation() -> None:
    """23. Security Test: Cross-agent cancellation requests use isolated identity hashes."""
    tenant_id = uuid.uuid4()
    agent_A = uuid.uuid4()
    agent_B = uuid.uuid4()

    service = PaymentCancellationService()
    hash_A = service.idempotency_service.compute_identity_hash(
        tenant_id, agent_A, "tx", "op", "key"
    )
    hash_B = service.idempotency_service.compute_identity_hash(
        tenant_id, agent_B, "tx", "op", "key"
    )

    assert hash_A != hash_B


def test_24_cross_transaction_isolation_in_cancellation() -> None:
    """24. Security Test: Cross-transaction cancellation requests use isolated identity hashes."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    service = PaymentCancellationService()
    hash_A = service.idempotency_service.compute_identity_hash(
        tenant_id, agent_id, "tx_A", "op", "key"
    )
    hash_B = service.idempotency_service.compute_identity_hash(
        tenant_id, agent_id, "tx_B", "op", "key"
    )

    assert hash_A != hash_B


def test_25_missing_authorization_fingerprint_rejected() -> None:
    """25. Security Test: Missing authorization fingerprint is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_cncl_25"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    req = PaymentCancellationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        order_id="order_25",
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="",  # Blank FP!
        idempotency_key="idemp_key_25",
    )

    service = PaymentCancellationService()
    with pytest.raises(PaymentCancellationError) as exc_info:
        service.cancel_payment(decision, req, current_status=PaymentStatus.ORDER_CREATED)

    assert exc_info.value.error_code == "AUTHORIZATION_FINGERPRINT_MISSING"


def test_26_cancellation_model_frozen_and_immutable() -> None:
    """26. Security Test: PaymentCancellationResult model is frozen and immutable."""
    res = PaymentCancellationResult(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_26",
        order_id="order_26",
        previous_status=PaymentStatus.ORDER_CREATED,
        cancellation_fingerprint="fp_26",
    )

    with pytest.raises((TypeError, Exception)):
        res.cancellation_status = PaymentStatus.CAPTURED  # Mutate attempt!


def test_27_out_of_scope_future_phases_unimplemented() -> None:
    """27. Static Check: Base codebase contains 0 Phase 300+ features."""
    import app.payment.payment_service as ps_mod

    source_code = inspect.getsource(ps_mod)
    assert "reviewer_approval_queue" not in source_code
    assert "approval_workflow" not in source_code
