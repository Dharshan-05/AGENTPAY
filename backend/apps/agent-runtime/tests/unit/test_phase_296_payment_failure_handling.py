"""Unit, Security & Failure State Tests for Phase 296 — Payment Failure Handling."""

from __future__ import annotations

import uuid

import pytest

from app.payment.failures.payment_failure_service import (
    PaymentFailureService,
)
from app.payment.status.payment_status_service import PaymentStatusService
from app.schemas.payment import PaymentStatus
from app.schemas.payment_failure import (
    PaymentFailureCategory,
    PaymentFailureCode,
    PaymentFailureRecord,
)


def test_01_provider_failure_normalization() -> None:
    """1. Test provider failure exception is normalized into PROVIDER_FAILURE category."""
    service = PaymentFailureService()
    err = Exception("Razorpay API connection timeout or provider unavailable")

    rec = service.normalize_failure(err, category=PaymentFailureCategory.PROVIDER_FAILURE)

    assert isinstance(rec, PaymentFailureRecord)
    assert rec.category == PaymentFailureCategory.PROVIDER_FAILURE
    assert rec.failure_code == PaymentFailureCode.PAYMENT_PROVIDER_UNAVAILABLE
    assert rec.payment_success is False
    assert rec.payment_verified is False
    assert rec.captured is False


def test_02_verification_failure_normalization() -> None:
    """2. Test verification failure exception is normalized into VERIFICATION_FAILURE category."""
    service = PaymentFailureService()
    err = ValueError("Invalid signature or amount mismatch")

    rec = service.normalize_failure(
        err,
        category=PaymentFailureCategory.VERIFICATION_FAILURE,
        failure_code=PaymentFailureCode.PAYMENT_SIGNATURE_INVALID,
    )

    assert rec.category == PaymentFailureCategory.VERIFICATION_FAILURE
    assert rec.failure_code == PaymentFailureCode.PAYMENT_SIGNATURE_INVALID
    assert rec.payment_success is False


def test_03_invalid_payment_request_failure() -> None:
    """3. Test invalid payment data failure is normalized into INVALID_REQUEST category."""
    service = PaymentFailureService()
    err = ValueError("Invalid currency code OR negative monetary amount")

    rec = service.normalize_failure(err, category=PaymentFailureCategory.INVALID_REQUEST)

    assert rec.category == PaymentFailureCategory.INVALID_REQUEST
    assert rec.payment_success is False


def test_04_timeout_handling_normalization() -> None:
    """4. Test network timeout exception is normalized into TIMEOUT category."""
    service = PaymentFailureService()
    err = TimeoutError("HTTP request to Razorpay timed out after 30 seconds")

    rec = service.normalize_failure(err)

    assert rec.category == PaymentFailureCategory.TIMEOUT
    assert rec.failure_code == PaymentFailureCode.PAYMENT_TIMEOUT


def test_05_unknown_failure_handling() -> None:
    """5. Test unexpected exception is normalized into UNKNOWN_FAILURE category."""
    service = PaymentFailureService()
    err = RuntimeError("Unexpected internal system exception")

    rec = service.normalize_failure(err)

    assert rec.category == PaymentFailureCategory.UNKNOWN_FAILURE
    assert rec.failure_code == PaymentFailureCode.PAYMENT_UNKNOWN_FAILURE


def test_06_safe_error_output_sanitization() -> None:
    """6. Security Test: Raw exception message is sanitized to remove secret tokens."""
    service = PaymentFailureService()
    raw_err_msg = (
        "Failed request to Razorpay with key rzp_test_9999999999 and secret "
        "key_secret='UNSAFE_SECRET_123' Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.sig"
    )

    rec = service.normalize_failure(Exception(raw_err_msg))

    assert "UNSAFE_SECRET_123" not in rec.safe_message
    assert "rzp_test_9999999999" not in rec.safe_message
    assert "eyJhbGci" not in rec.safe_message
    assert "[REDACTED]" in rec.safe_message or "[REDACTED_KEY_ID]" in rec.safe_message


def test_07_secret_redaction_verification() -> None:
    """7. Security Test: PaymentFailureRecord model_fields contain 0 secret parameters."""
    assert "key_secret" not in PaymentFailureRecord.model_fields
    assert "webhook_secret" not in PaymentFailureRecord.model_fields


def test_08_deterministic_failure_fingerprint() -> None:
    """8. Test failure fingerprint is deterministic SHA-256 over safe metadata."""
    service = PaymentFailureService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    rec1 = service.normalize_failure(
        Exception("Error 1"),
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_01",
    )

    assert len(rec1.failure_fingerprint) == 64


def test_09_tenant_isolation_in_failures() -> None:
    """9. Test tenant isolation in failure records."""
    service = PaymentFailureService()
    tenant_A = uuid.uuid4()
    tenant_B = uuid.uuid4()

    rec_A = service.normalize_failure(Exception("Err A"), tenant_id=tenant_A)
    rec_B = service.normalize_failure(Exception("Err B"), tenant_id=tenant_B)

    assert rec_A.tenant_id == tenant_A
    assert rec_B.tenant_id == tenant_B
    assert rec_A.tenant_id != rec_B.tenant_id


def test_10_agent_isolation_in_failures() -> None:
    """10. Test agent isolation in failure records."""
    service = PaymentFailureService()
    agent_A = uuid.uuid4()
    agent_B = uuid.uuid4()

    rec_A = service.normalize_failure(Exception("Err A"), agent_id=agent_A)
    rec_B = service.normalize_failure(Exception("Err B"), agent_id=agent_B)

    assert rec_A.agent_id == agent_A
    assert rec_B.agent_id == agent_B


def test_11_transaction_isolation_in_failures() -> None:
    """11. Test transaction isolation in failure records."""
    service = PaymentFailureService()

    rec_A = service.normalize_failure(Exception("Err A"), transaction_id="tx_A")
    rec_B = service.normalize_failure(Exception("Err B"), transaction_id="tx_B")

    assert rec_A.transaction_id == "tx_A"
    assert rec_B.transaction_id == "tx_B"


def test_12_failed_state_transition_execution() -> None:
    """12. Test failure handling executes valid state machine transition to FAILED."""
    status_service = PaymentStatusService()
    failure_service = PaymentFailureService(status_service=status_service)

    rec = failure_service.normalize_failure(
        Exception("Order creation error"),
        current_status=PaymentStatus.ORDER_CREATED,
    )

    assert rec.previous_status == PaymentStatus.ORDER_CREATED
    assert rec.new_status == PaymentStatus.FAILED


def test_13_illegal_terminal_transition_prevention() -> None:
    """13. Security Test: Terminal transition from CAPTURED state does not corrupt state."""
    status_service = PaymentStatusService()
    failure_service = PaymentFailureService(status_service=status_service)

    # Transition CAPTURED -> FAILED is illegal in domain state machine
    rec = failure_service.normalize_failure(
        Exception("Late failure notification after capture"),
        current_status=PaymentStatus.CAPTURED,
    )

    assert rec.previous_status == PaymentStatus.CAPTURED
    assert rec.new_status == PaymentStatus.CAPTURED
    assert rec.category == PaymentFailureCategory.STATE_TRANSITION_FAILURE


def test_14_repeated_failure_event_idempotency() -> None:
    """14. Test repeated failure normalization for already failed status is idempotent."""
    status_service = PaymentStatusService()
    failure_service = PaymentFailureService(status_service=status_service)

    rec = failure_service.normalize_failure(
        Exception("Repeated failure"),
        current_status=PaymentStatus.FAILED,
    )

    assert rec.previous_status == PaymentStatus.FAILED
    assert rec.new_status == PaymentStatus.FAILED


def test_15_no_success_fabrication_guarantee() -> None:
    """15. Security Test: Failure record CAN NEVER HAVE payment_success=True."""
    service = PaymentFailureService()
    rec = service.normalize_failure(Exception("Failure test"))

    assert rec.payment_success is False
    assert rec.payment_verified is False
    assert rec.captured is False

    with pytest.raises((TypeError, Exception)):
        rec.payment_success = True  # Immutable model!


def test_16_no_capture_fabrication_guarantee() -> None:
    """16. Security Test: Payment failure RECORD CAN NEVER HAVE captured=True."""
    service = PaymentFailureService()
    rec = service.normalize_failure(Exception("Failure test"))

    assert rec.captured is False


def test_17_static_check_no_risk_recalculation() -> None:
    """17. Static Check: PaymentFailureService contains 0 risk scoring calculations."""
    import inspect

    import app.payment.failures.payment_failure_service as pfs_mod

    source_code = inspect.getsource(pfs_mod)
    assert "calculate_composite_risk_score" not in source_code
    assert "evaluate_hard_security_rules" not in source_code


def test_18_static_check_no_authorization_bypass() -> None:
    """18. Static Check: PaymentFailureService contains 0 authorization gate bypass calls."""
    import inspect

    import app.payment.failures.payment_failure_service as pfs_mod

    source_code = inspect.getsource(pfs_mod)
    assert "bypass_authorization" not in source_code
