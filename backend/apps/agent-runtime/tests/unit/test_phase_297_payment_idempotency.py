"""Unit, Security & Adversarial Tests for Phase 297 — Payment Idempotency."""

from __future__ import annotations

import threading
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.payment.idempotency.payment_idempotency_service import (
    PaymentIdempotencyConflictError,
    PaymentIdempotencyError,
    PaymentIdempotencyService,
)
from app.payment.payment_service import PaymentService, PaymentServiceError
from app.schemas.payment import (
    PaymentOrderResult,
    PaymentServiceRequest,
    SupportedCurrency,
)
from app.schemas.payment_authorization import (
    PaymentAuthorizationOutcome,
    PaymentAuthorizationResult,
)
from app.schemas.payment_idempotency import IdempotencyState, PaymentIdempotencyRecord
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


def _make_auth_result(
    decision: FinalRiskDecisionResult,
    outcome: PaymentAuthorizationOutcome = PaymentAuthorizationOutcome.PERMITTED,
    reason_code: str = "PERMITTED",
) -> PaymentAuthorizationResult:
    return PaymentAuthorizationResult(
        authorization_id=uuid.uuid4(),
        decision_id=decision.decision_id,
        evaluation_id=decision.evaluation_id,
        tenant_id=decision.tenant_id,
        agent_id=decision.agent_id,
        transaction_id=decision.transaction_id,
        outcome=outcome,
        reason_code=reason_code,
        execution_permitted=(outcome == PaymentAuthorizationOutcome.PERMITTED),
        execution_suspended=(outcome == PaymentAuthorizationOutcome.SUSPENDED),
        approval_required=False,
        authorization_denied=(outcome == PaymentAuthorizationOutcome.DENIED),
        decision_reason=decision.decision_reason,
        decision_fingerprint=decision.decision_fingerprint,
        authorization_fingerprint="fp_auth",
    )


def test_01_first_request_reserves_key() -> None:
    """1. Test initial request reserves key in IN_PROGRESS state with is_new = True."""
    service = PaymentIdempotencyService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    fp = service.compute_request_fingerprint(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_01",
        operation="create_payment_order",
        request_params={"amount": "100.00", "currency": "INR"},
    )

    rec, is_new = service.reserve_idempotency(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_01",
        operation="create_payment_order",
        idempotency_key="idemp_key_01",
        request_fingerprint=fp,
    )

    assert is_new is True
    assert rec.state == IdempotencyState.IN_PROGRESS
    assert rec.idempotency_key == "idemp_key_01"


def test_02_same_key_same_request_is_idempotent() -> None:
    """2. Test same key + same request returns existing record without creating duplicate."""
    service = PaymentIdempotencyService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    fp = service.compute_request_fingerprint(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_02",
        operation="create_payment_order",
        request_params={"amount": "100.00", "currency": "INR"},
    )

    rec1, is_new1 = service.reserve_idempotency(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_02",
        operation="create_payment_order",
        idempotency_key="idemp_key_02",
        request_fingerprint=fp,
    )
    assert is_new1 is True

    # Complete record
    service.complete_idempotency(rec1.record_id, {"order_id": "order_02", "amount": 100})

    # Second call
    rec2, is_new2 = service.reserve_idempotency(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_02",
        operation="create_payment_order",
        idempotency_key="idemp_key_02",
        request_fingerprint=fp,
    )

    assert is_new2 is False
    assert rec2.state == IdempotencyState.COMPLETED
    assert rec2.safe_result_payload == {"order_id": "order_02", "amount": 100}


def test_03_duplicate_request_does_not_call_razorpay_twice() -> None:
    """3. Test duplicate create_payment_order call replays result without provider call."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_dup_03"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    mock_gate = MagicMock()
    mock_gate.authorize_payment.return_value = _make_auth_result(decision)

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"
    mock_provider.validate_configuration.return_value = True

    real_order_result = PaymentOrderResult(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="fp_auth",
        order_id="order_rzp_real_03",
        amount=Decimal("100.00"),
        amount_minor_units=10000,
        currency=SupportedCurrency.INR,
        idempotency_key="idemp_key_03",
    )
    mock_provider.create_order.return_value = real_order_result

    idemp_service = PaymentIdempotencyService()
    payment_service = PaymentService(
        authorization_gate=mock_gate,
        provider=mock_provider,
        idempotency_service=idemp_service,
    )

    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        idempotency_key="idemp_key_03",
    )

    # First call -> executes provider create_order
    res1 = payment_service.create_payment_order(decision, req)
    assert res1.order_id == "order_rzp_real_03"
    assert mock_provider.create_order.call_count == 1

    # Second call -> replays previous result from idempotency store! (0 provider calls)
    res2 = payment_service.create_payment_order(decision, req)
    assert res2.order_id == "order_rzp_real_03"
    assert mock_provider.create_order.call_count == 1  # Still 1! Provider NOT called twice!


def test_04_same_key_different_amount_rejected() -> None:
    """4. Adversarial Test: Same idempotency key with modified amount raises 409 Conflict."""
    service = PaymentIdempotencyService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    fp1 = service.compute_request_fingerprint(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_04",
        operation="create_payment_order",
        request_params={"amount": "100.00", "currency": "INR"},
    )
    fp2 = service.compute_request_fingerprint(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_04",
        operation="create_payment_order",
        request_params={"amount": "999.00", "currency": "INR"},  # Modified amount!
    )

    service.reserve_idempotency(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_04",
        operation="create_payment_order",
        idempotency_key="key_04",
        request_fingerprint=fp1,
    )

    # Second call with modified amount -> CONFLICT
    with pytest.raises(PaymentIdempotencyConflictError) as exc_info:
        service.reserve_idempotency(
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id="tx_04",
            operation="create_payment_order",
            idempotency_key="key_04",
            request_fingerprint=fp2,
        )

    assert exc_info.value.error_code == "IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_REQUEST"


def test_05_same_key_different_currency_rejected() -> None:
    """5. Adversarial Test: Same idempotency key with modified currency raises 409 Conflict."""
    service = PaymentIdempotencyService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    fp1 = service.compute_request_fingerprint(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_05",
        operation="create_payment_order",
        request_params={"amount": "100.00", "currency": "INR"},
    )
    fp2 = service.compute_request_fingerprint(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_05",
        operation="create_payment_order",
        request_params={"amount": "100.00", "currency": "USD"},  # Modified currency!
    )

    service.reserve_idempotency(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_05",
        operation="create_payment_order",
        idempotency_key="key_05",
        request_fingerprint=fp1,
    )

    with pytest.raises(PaymentIdempotencyConflictError):
        service.reserve_idempotency(
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id="tx_05",
            operation="create_payment_order",
            idempotency_key="key_05",
            request_fingerprint=fp2,
        )


def test_06_same_key_different_tenant_isolated() -> None:
    """6. Security Test: Same key across different tenants produces isolated identity hashes."""
    service = PaymentIdempotencyService()
    tenant_A = uuid.uuid4()
    tenant_B = uuid.uuid4()
    agent_id = uuid.uuid4()

    hash_A = service.compute_identity_hash(tenant_A, agent_id, "tx_06", "op", "key_06")
    hash_B = service.compute_identity_hash(tenant_B, agent_id, "tx_06", "op", "key_06")

    assert hash_A != hash_B


def test_07_same_key_different_agent_isolated() -> None:
    """7. Security Test: Same key across different agents produces isolated identity hashes."""
    service = PaymentIdempotencyService()
    tenant_id = uuid.uuid4()
    agent_A = uuid.uuid4()
    agent_B = uuid.uuid4()

    hash_A = service.compute_identity_hash(tenant_id, agent_A, "tx_07", "op", "key_07")
    hash_B = service.compute_identity_hash(tenant_id, agent_B, "tx_07", "op", "key_07")

    assert hash_A != hash_B


def test_08_same_key_different_transaction_isolated() -> None:
    """8. Security Test: Same key across different transactions produces isolated hashes."""
    service = PaymentIdempotencyService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    hash_A = service.compute_identity_hash(tenant_id, agent_id, "tx_A", "op", "key_08")
    hash_B = service.compute_identity_hash(tenant_id, agent_id, "tx_B", "op", "key_08")

    assert hash_A != hash_B


def test_09_different_operation_isolated() -> None:
    """9. Test different operation names with same key produce isolated identity hashes."""
    service = PaymentIdempotencyService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    hash_op1 = service.compute_identity_hash(tenant_id, agent_id, "tx_09", "create_order", "key_09")
    hash_op2 = service.compute_identity_hash(tenant_id, agent_id, "tx_09", "eval_payment", "key_09")

    assert hash_op1 != hash_op2


def test_10_in_progress_concurrency_protection() -> None:
    """10. Test IN_PROGRESS state prevents concurrent duplicate execution."""
    service = PaymentIdempotencyService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    fp = service.compute_request_fingerprint(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_10",
        operation="create_payment_order",
        request_params={"amount": "100.00"},
    )

    rec1, is_new1 = service.reserve_idempotency(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_10",
        operation="create_payment_order",
        idempotency_key="key_10",
        request_fingerprint=fp,
    )
    assert is_new1 is True

    # Concurrent second call while IN_PROGRESS
    rec2, is_new2 = service.reserve_idempotency(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_10",
        operation="create_payment_order",
        idempotency_key="key_10",
        request_fingerprint=fp,
    )

    assert is_new2 is False
    assert rec2.state == IdempotencyState.IN_PROGRESS


def test_11_completed_state_replays_result() -> None:
    """11. Test COMPLETED state replays saved safe result payload."""
    service = PaymentIdempotencyService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    fp = service.compute_request_fingerprint(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_11",
        operation="create_payment_order",
        request_params={"amount": "100.00"},
    )

    rec1, _ = service.reserve_idempotency(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_11",
        operation="create_payment_order",
        idempotency_key="key_11",
        request_fingerprint=fp,
    )
    service.complete_idempotency(rec1.record_id, {"order_id": "order_11_saved"})

    rec2, is_new = service.reserve_idempotency(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_11",
        operation="create_payment_order",
        idempotency_key="key_11",
        request_fingerprint=fp,
    )

    assert is_new is False
    assert rec2.state == IdempotencyState.COMPLETED
    assert rec2.safe_result_payload == {"order_id": "order_11_saved"}


def test_12_failed_state_behavior_deterministic() -> None:
    """12. Test FAILED state updates record with failure code."""
    service = PaymentIdempotencyService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    fp = service.compute_request_fingerprint(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_12",
        operation="create_payment_order",
        request_params={"amount": "100.00"},
    )

    rec1, _ = service.reserve_idempotency(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_12",
        operation="create_payment_order",
        idempotency_key="key_12",
        request_fingerprint=fp,
    )
    failed_rec = service.fail_idempotency(rec1.record_id, error_code="PROVIDER_TIMEOUT")

    assert failed_rec.state == IdempotencyState.FAILED
    assert failed_rec.error_code == "PROVIDER_TIMEOUT"


def test_13_concurrent_duplicate_requests_threading_safety() -> None:
    """13. Concurrency Test: Multi-threaded reservation guarantees 1 caller gets is_new=True."""
    service = PaymentIdempotencyService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    fp = service.compute_request_fingerprint(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_13_concurrent",
        operation="create_payment_order",
        request_params={"amount": "100.00"},
    )

    results: list[bool] = []
    lock = threading.Lock()

    def _worker() -> None:
        _, is_new = service.reserve_idempotency(
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id="tx_13_concurrent",
            operation="create_payment_order",
            idempotency_key="key_13_concurrent",
            request_fingerprint=fp,
        )
        with lock:
            results.append(is_new)

    threads = [threading.Thread(target=_worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Exactly 1 thread must be True (new reservation), remaining 9 must be False
    assert results.count(True) == 1
    assert results.count(False) == 9


def test_14_provider_failure_handling_in_idempotency() -> None:
    """14. Test provider failure marks idempotency record as FAILED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_fail_14"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    mock_gate = MagicMock()
    mock_gate.authorize_payment.return_value = _make_auth_result(decision)

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"
    mock_provider.validate_configuration.return_value = True
    mock_provider.create_order.side_effect = RuntimeError("Razorpay provider HTTP timeout")

    idemp_service = PaymentIdempotencyService()
    payment_service = PaymentService(
        authorization_gate=mock_gate,
        provider=mock_provider,
        idempotency_service=idemp_service,
    )

    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        idempotency_key="key_14_fail",
    )

    with pytest.raises(PaymentServiceError):
        payment_service.create_payment_order(decision, req)

    # Check record state in idempotency store
    hash_val = idemp_service.compute_identity_hash(
        tenant_id, agent_id, tx_id, "create_payment_order", "key_14_fail"
    )
    rec = idemp_service._store[hash_val]
    assert rec.state == IdempotencyState.FAILED
    assert rec.error_code == "RuntimeError"


def test_15_deterministic_request_fingerprint() -> None:
    """15. Test request fingerprint is deterministic SHA-256 over canonical parameters."""
    service = PaymentIdempotencyService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    fp1 = service.compute_request_fingerprint(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_15",
        operation="op",
        request_params={"b": 2, "a": 1},
    )
    fp2 = service.compute_request_fingerprint(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_15",
        operation="op",
        request_params={"a": 1, "b": 2},  # Reordered keys!
    )

    assert fp1 == fp2
    assert len(fp1) == 64


def test_16_secret_redaction_in_idempotency_record() -> None:
    """16. Security Test: PaymentIdempotencyRecord model_fields contain 0 secret fields."""
    assert "key_secret" not in PaymentIdempotencyRecord.model_fields
    assert "webhook_secret" not in PaymentIdempotencyRecord.model_fields


def test_17_tenant_isolation_in_idempotency_store() -> None:
    """17. Security Test: Multi-tenant isolation in idempotency store."""
    service = PaymentIdempotencyService()
    tenant_A = uuid.uuid4()
    tenant_B = uuid.uuid4()
    agent_id = uuid.uuid4()

    fp_A = service.compute_request_fingerprint(tenant_A, agent_id, "tx_17", "op", {"amt": 100})
    fp_B = service.compute_request_fingerprint(tenant_B, agent_id, "tx_17", "op", {"amt": 100})

    rec_A, new_A = service.reserve_idempotency(tenant_A, agent_id, "tx_17", "op", "key_17", fp_A)
    rec_B, new_B = service.reserve_idempotency(tenant_B, agent_id, "tx_17", "op", "key_17", fp_B)

    assert new_A is True
    assert new_B is True
    assert rec_A.tenant_id != rec_B.tenant_id


def test_18_no_fake_payment_order_ids() -> None:
    """18. Security Test: Idempotency service does not manufacture fake order IDs."""
    service = PaymentIdempotencyService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    fp = service.compute_request_fingerprint(tenant_id, agent_id, "tx_18", "op", {})
    rec, _ = service.reserve_idempotency(tenant_id, agent_id, "tx_18", "op", "key_18", fp)

    dump_str = str(rec.model_dump())
    assert "order_fake_" not in dump_str
    assert "pay_fake_" not in dump_str


def test_19_authorization_gate_cannot_be_bypassed() -> None:
    """19. Security Test: Idempotency layer does not bypass PaymentAuthorizationGate."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_gate_19"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    # Denying gate!
    mock_gate = MagicMock()
    mock_gate.authorize_payment.return_value = _make_auth_result(
        decision,
        outcome=PaymentAuthorizationOutcome.DENIED,
        reason_code="RISK_HIGH_DENIED",
    )

    mock_provider = MagicMock()
    mock_provider.provider_name = "razorpay"

    idemp_service = PaymentIdempotencyService()
    payment_service = PaymentService(
        authorization_gate=mock_gate,
        provider=mock_provider,
        idempotency_service=idemp_service,
    )

    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        idempotency_key="key_19_gate_denied",
    )

    with pytest.raises(PaymentServiceError) as exc_info:
        payment_service.create_payment_order(decision, req)

    assert "DENIED by authorization gate" in str(exc_info.value)
    assert mock_provider.create_order.call_count == 0


def test_20_malformed_idempotency_key_rejected() -> None:
    """20. Security Test: Empty or blank idempotency key raises INVALID_IDEMPOTENCY_KEY error."""
    service = PaymentIdempotencyService()
    tenant_id = uuid.uuid4()

    with pytest.raises(PaymentIdempotencyError) as exc_info:
        service.compute_identity_hash(tenant_id, uuid.uuid4(), "tx_20", "op", "   ")

    assert exc_info.value.error_code == "INVALID_IDEMPOTENCY_KEY"


def test_21_static_check_no_risk_recalculation() -> None:
    """21. Static Check: PaymentIdempotencyService contains 0 risk scoring calculations."""
    import inspect

    import app.payment.idempotency.payment_idempotency_service as pis_mod

    source_code = inspect.getsource(pis_mod)
    assert "calculate_composite_risk_score" not in source_code
    assert "evaluate_hard_security_rules" not in source_code


def test_22_static_check_no_independent_authorization() -> None:
    """22. Static Check: PaymentIdempotencyService does not authorize payments independently."""
    import inspect

    import app.payment.idempotency.payment_idempotency_service as pis_mod

    source_code = inspect.getsource(pis_mod)
    assert "authorize_payment" not in source_code


def test_23_idempotency_record_frozen_and_immutable() -> None:
    """23. Security Test: PaymentIdempotencyRecord is frozen and immutable."""
    service = PaymentIdempotencyService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    fp = service.compute_request_fingerprint(tenant_id, agent_id, "tx_23", "op", {})
    rec, _ = service.reserve_idempotency(tenant_id, agent_id, "tx_23", "op", "key_23", fp)

    with pytest.raises((TypeError, Exception)):
        rec.state = IdempotencyState.COMPLETED  # Mutate attempt!


def test_24_out_of_scope_future_phases_unimplemented() -> None:
    """24. Static Check: Payment codebase contains 0 Phase 298+ features."""
    import inspect

    import app.payment.payment_service as ps_mod

    source_code = inspect.getsource(ps_mod)
    assert "execute_refund" not in source_code
    assert "execute_cancellation" not in source_code
    assert "reviewer_approval_queue" not in source_code


def test_25_idempotency_capacity_eviction() -> None:
    """25. Test PaymentIdempotencyService capacity eviction behavior."""
    service = PaymentIdempotencyService(max_capacity=5)
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    for i in range(5):
        fp = service.compute_request_fingerprint(tenant_id, agent_id, f"tx_{i}", "op", {})
        rec, is_new = service.reserve_idempotency(
            tenant_id, agent_id, f"tx_{i}", "op", f"key_{i}", fp
        )
        assert is_new is True

    # 6th insertion triggers eviction
    fp6 = service.compute_request_fingerprint(tenant_id, agent_id, "tx_6", "op", {})
    rec6, is_new6 = service.reserve_idempotency(tenant_id, agent_id, "tx_6", "op", "key_6", fp6)
    assert is_new6 is True
