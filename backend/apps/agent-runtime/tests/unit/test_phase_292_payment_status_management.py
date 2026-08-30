"""Unit & Security Tests for Phase 292 — Payment Status Management."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.payment.status.payment_status_service import (
    PaymentStatusError,
    PaymentStatusService,
)
from app.schemas.payment import (
    PaymentStatus,
    PaymentStatusTransitionRecord,
    PaymentVerificationResult,
    PaymentVerificationStatus,
    SupportedCurrency,
)


def test_26_created_to_order_created_valid() -> None:
    """26. Test CREATED -> ORDER_CREATED transition is valid."""
    svc = PaymentStatusService()
    rec = svc.transition_status(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_292_26",
        order_id="order_292_26",
        previous_status=PaymentStatus.CREATED,
        new_status=PaymentStatus.ORDER_CREATED,
        transition_reason="Order created on Razorpay",
    )

    assert isinstance(rec, PaymentStatusTransitionRecord)
    assert rec.previous_status == PaymentStatus.CREATED
    assert rec.new_status == PaymentStatus.ORDER_CREATED
    assert rec.transition_reason == "Order created on Razorpay"


def test_27_order_created_to_checkout_ready_valid() -> None:
    """27. Test ORDER_CREATED -> CHECKOUT_READY transition is valid."""
    svc = PaymentStatusService()
    rec = svc.transition_status(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_292_27",
        order_id="order_292_27",
        previous_status=PaymentStatus.ORDER_CREATED,
        new_status=PaymentStatus.CHECKOUT_READY,
        transition_reason="Checkout config generated",
    )

    assert rec.previous_status == PaymentStatus.ORDER_CREATED
    assert rec.new_status == PaymentStatus.CHECKOUT_READY


def test_28_checkout_ready_to_payment_pending_valid() -> None:
    """28. Test CHECKOUT_READY -> PAYMENT_PENDING transition is valid."""
    svc = PaymentStatusService()
    rec = svc.transition_status(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_292_28",
        order_id="order_292_28",
        previous_status=PaymentStatus.CHECKOUT_READY,
        new_status=PaymentStatus.PAYMENT_PENDING,
        transition_reason="User opened payment modal",
    )

    assert rec.previous_status == PaymentStatus.CHECKOUT_READY
    assert rec.new_status == PaymentStatus.PAYMENT_PENDING


def test_29_payment_pending_to_payment_received_valid() -> None:
    """29. Test PAYMENT_PENDING -> PAYMENT_RECEIVED transition is valid."""
    svc = PaymentStatusService()
    rec = svc.transition_status(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_292_29",
        order_id="order_292_29",
        payment_id="pay_292_29",
        previous_status=PaymentStatus.PAYMENT_PENDING,
        new_status=PaymentStatus.PAYMENT_RECEIVED,
        transition_reason="Payment payload received from frontend",
    )

    assert rec.previous_status == PaymentStatus.PAYMENT_PENDING
    assert rec.new_status == PaymentStatus.PAYMENT_RECEIVED


def test_30_payment_received_to_payment_verified_valid() -> None:
    """30. Test PAYMENT_RECEIVED -> PAYMENT_VERIFIED transition is valid."""
    svc = PaymentStatusService()
    rec = svc.transition_status(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_292_30",
        order_id="order_292_30",
        payment_id="pay_292_30",
        previous_status=PaymentStatus.PAYMENT_RECEIVED,
        new_status=PaymentStatus.PAYMENT_VERIFIED,
        transition_reason="Signature verification passed",
    )

    assert rec.previous_status == PaymentStatus.PAYMENT_RECEIVED
    assert rec.new_status == PaymentStatus.PAYMENT_VERIFIED


def test_31_payment_verified_to_captured_valid() -> None:
    """31. Test PAYMENT_VERIFIED -> CAPTURED transition is valid."""
    svc = PaymentStatusService()
    rec = svc.transition_status(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_292_31",
        order_id="order_292_31",
        payment_id="pay_292_31",
        previous_status=PaymentStatus.PAYMENT_VERIFIED,
        new_status=PaymentStatus.CAPTURED,
        transition_reason="Payment captured",
    )

    assert rec.previous_status == PaymentStatus.PAYMENT_VERIFIED
    assert rec.new_status == PaymentStatus.CAPTURED


def test_32_captured_to_refunded_valid() -> None:
    """32. Test CAPTURED -> REFUNDED transition is valid."""
    svc = PaymentStatusService()
    rec = svc.transition_status(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_292_32",
        order_id="order_292_32",
        payment_id="pay_292_32",
        previous_status=PaymentStatus.CAPTURED,
        new_status=PaymentStatus.REFUNDED,
        transition_reason="Refund executed",
    )

    assert rec.previous_status == PaymentStatus.CAPTURED
    assert rec.new_status == PaymentStatus.REFUNDED


def test_33_illegal_backward_transition_rejected() -> None:
    """33. Security Test: Backward transition CAPTURED -> CREATED raises PaymentStatusError."""
    svc = PaymentStatusService()
    with pytest.raises(PaymentStatusError, match="Illegal payment status transition"):
        svc.transition_status(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_292_33",
            order_id="order_292_33",
            previous_status=PaymentStatus.CAPTURED,
            new_status=PaymentStatus.CREATED,  # Illegal backward jump!
            transition_reason="Forged reset",
        )


def test_34_terminal_state_mutation_rejected() -> None:
    """34. Security Test: Transitioning from REFUNDED terminal state raises PaymentStatusError."""
    svc = PaymentStatusService()
    with pytest.raises(PaymentStatusError, match="Illegal payment status transition"):
        svc.transition_status(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_292_34",
            order_id="order_292_34",
            previous_status=PaymentStatus.REFUNDED,
            new_status=PaymentStatus.CAPTURED,  # Terminal state mutation!
            transition_reason="Forged un-refund",
        )


def test_35_client_cannot_force_captured() -> None:
    """35. Security Test: Direct jump CREATED -> CAPTURED raises PaymentStatusError."""
    svc = PaymentStatusService()
    with pytest.raises(PaymentStatusError):
        svc.transition_status(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_292_35",
            order_id="order_292_35",
            previous_status=PaymentStatus.CREATED,
            new_status=PaymentStatus.CAPTURED,  # Direct jump!
            transition_reason="Client forged captured status",
        )


def test_36_client_cannot_force_verified() -> None:
    """36. Security Test: Direct jump CREATED -> PAYMENT_VERIFIED raises PaymentStatusError."""
    svc = PaymentStatusService()
    with pytest.raises(PaymentStatusError):
        svc.transition_status(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_292_36",
            order_id="order_292_36",
            previous_status=PaymentStatus.CREATED,
            new_status=PaymentStatus.PAYMENT_VERIFIED,  # Direct jump!
            transition_reason="Client forged verified status",
        )


def test_37_tenant_id_preserved_in_record() -> None:
    """37. Security Test: Status transition record preserves tenant_id."""
    svc = PaymentStatusService()
    t_id = uuid.uuid4()
    rec = svc.transition_status(
        tenant_id=t_id,
        agent_id=uuid.uuid4(),
        transaction_id="tx_292_37",
        order_id="order_292_37",
        previous_status=PaymentStatus.CREATED,
        new_status=PaymentStatus.ORDER_CREATED,
        transition_reason="Test tenant binding",
    )

    assert rec.tenant_id == t_id


def test_38_agent_id_preserved_in_record() -> None:
    """38. Security Test: Status transition record preserves agent_id."""
    svc = PaymentStatusService()
    a_id = uuid.uuid4()
    rec = svc.transition_status(
        tenant_id=uuid.uuid4(),
        agent_id=a_id,
        transaction_id="tx_292_38",
        order_id="order_292_38",
        previous_status=PaymentStatus.CREATED,
        new_status=PaymentStatus.ORDER_CREATED,
        transition_reason="Test agent binding",
    )

    assert rec.agent_id == a_id


def test_39_transaction_id_preserved_in_record() -> None:
    """39. Security Test: Status transition record preserves transaction_id."""
    svc = PaymentStatusService()
    tx_id = "tx_292_39_unique"
    rec = svc.transition_status(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id=tx_id,
        order_id="order_292_39",
        previous_status=PaymentStatus.CREATED,
        new_status=PaymentStatus.ORDER_CREATED,
        transition_reason="Test tx binding",
    )

    assert rec.transaction_id == tx_id


def test_40_amount_immutability_maintained() -> None:
    """40. Security Test: PaymentStatusTransitionRecord is frozen and immutable."""
    rec = PaymentStatusTransitionRecord(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_292_40",
        order_id="order_40",
        previous_status=PaymentStatus.CREATED,
        new_status=PaymentStatus.ORDER_CREATED,
        transition_reason="Test immutability",
        transition_fingerprint="fp_40",
    )

    with pytest.raises((TypeError, Exception)):
        rec.previous_status = PaymentStatus.CAPTURED  # Frozen pydantic model!


def test_41_currency_immutability_maintained() -> None:
    """41. Security Test: SupportedCurrency enum values remain strict ISO codes."""
    assert SupportedCurrency.INR == "INR"
    assert SupportedCurrency.USD == "USD"


def test_42_duplicate_transition_is_idempotent() -> None:
    """42. Test same-state transition is idempotent and returns IDEMPOTENT_SAME_STATE."""
    svc = PaymentStatusService()
    rec = svc.transition_status(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_292_42",
        order_id="order_292_42",
        previous_status=PaymentStatus.PAYMENT_VERIFIED,
        new_status=PaymentStatus.PAYMENT_VERIFIED,  # Duplicate transition!
        transition_reason="Replay test",
    )

    assert rec.previous_status == PaymentStatus.PAYMENT_VERIFIED
    assert rec.new_status == PaymentStatus.PAYMENT_VERIFIED
    assert rec.transition_reason == "IDEMPOTENT_SAME_STATE"


def test_43_conflicting_replay_rejected() -> None:
    """43. Security Test: Replay trying to transition FAILED -> PAYMENT_VERIFIED is rejected."""
    svc = PaymentStatusService()
    with pytest.raises(PaymentStatusError):
        svc.transition_status(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_292_43",
            order_id="order_292_43",
            previous_status=PaymentStatus.FAILED,
            new_status=PaymentStatus.PAYMENT_VERIFIED,  # Conflicting replay!
            transition_reason="Replay attempt",
        )


def test_44_status_fingerprint_deterministic() -> None:
    """44. Test status transition fingerprint is byte-identical for identical inputs."""
    t_id = uuid.uuid4()
    a_id = uuid.uuid4()

    fp1 = PaymentStatusService.calculate_transition_fingerprint(
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_44",
        order_id="order_44",
        payment_id="pay_44",
        prev_status="PAYMENT_RECEIVED",
        new_status="PAYMENT_VERIFIED",
        reason="Verified",
    )

    fp2 = PaymentStatusService.calculate_transition_fingerprint(
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_44",
        order_id="order_44",
        payment_id="pay_44",
        prev_status="PAYMENT_RECEIVED",
        new_status="PAYMENT_VERIFIED",
        reason="Verified",
    )

    assert fp1 == fp2
    assert len(fp1) == 64


def test_45_secrets_absent_from_status_records() -> None:
    """45. Security Test: PaymentStatusTransitionRecord contains 0 secret fields."""
    assert "key_secret" not in PaymentStatusTransitionRecord.model_fields
    assert "webhook_secret" not in PaymentStatusTransitionRecord.model_fields


def test_46_unknown_status_rejected() -> None:
    """46. Security Test: Transitioning from UNKNOWN status raises PaymentStatusError."""
    svc = PaymentStatusService()
    with pytest.raises(PaymentStatusError):
        svc.transition_status(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_292_46",
            order_id="order_292_46",
            previous_status=PaymentStatus.UNKNOWN,
            new_status=PaymentStatus.PAYMENT_VERIFIED,
            transition_reason="Unknown status transition",
        )


def test_47_invalid_transition_fails_closed() -> None:
    """47. Security Test: Invalid transition CANCELLED -> CAPTURED raises PaymentStatusError."""
    svc = PaymentStatusService()
    with pytest.raises(PaymentStatusError) as exc_info:
        svc.transition_status(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_292_47",
            order_id="order_292_47",
            previous_status=PaymentStatus.CANCELLED,
            new_status=PaymentStatus.CAPTURED,
            transition_reason="Cancelled to captured attempt",
        )

    assert exc_info.value.reason_code == "ILLEGAL_STATUS_TRANSITION"


def test_48_verification_status_integration_passed() -> None:
    """48. Integration Test: transition_on_verification VERIFIED moves state to PAYMENT_VERIFIED."""
    svc = PaymentStatusService()
    t_id = uuid.uuid4()
    a_id = uuid.uuid4()

    vr = PaymentVerificationResult(
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_292_48",
        order_id="order_292_48",
        payment_id="pay_292_48",
        status=PaymentVerificationStatus.VERIFIED,
        reason_code="PAYMENT_VERIFIED_SUCCESSFULLY",
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        payment_success=True,
        payment_verified=True,
        captured=False,
        verification_fingerprint="fp_vr_48",
    )

    rec = svc.transition_on_verification(vr, current_status=PaymentStatus.PAYMENT_RECEIVED)

    assert rec.new_status == PaymentStatus.PAYMENT_VERIFIED
    assert rec.verification_fingerprint == "fp_vr_48"


def test_49_verification_status_integration_failed() -> None:
    """49. Integration Test: transition_on_verification with FAILED status moves state to FAILED."""
    svc = PaymentStatusService()
    t_id = uuid.uuid4()
    a_id = uuid.uuid4()

    vr = PaymentVerificationResult(
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_292_49",
        order_id="order_292_49",
        payment_id="pay_292_49",
        status=PaymentVerificationStatus.INVALID_SIGNATURE,
        reason_code="HMAC_SIGNATURE_INVALID",
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        payment_success=False,
        payment_verified=False,
        captured=False,
        verification_fingerprint="fp_vr_49",
    )

    rec = svc.transition_on_verification(vr, current_status=PaymentStatus.PAYMENT_RECEIVED)

    assert rec.new_status == PaymentStatus.FAILED
    assert "VERIFICATION_FAILED" in rec.transition_reason


def test_50_static_sdk_isolation_status_service() -> None:
    """50. Static Check: PaymentStatusService contains 0 razorpay SDK imports."""
    import inspect

    import app.payment.status.payment_status_service as ps_mod

    source_code = inspect.getsource(ps_mod)
    assert "import razorpay" not in source_code
    assert "from razorpay" not in source_code
    assert "calculate_composite_risk_score" not in source_code
    assert "evaluate_hard_security_rules" not in source_code
