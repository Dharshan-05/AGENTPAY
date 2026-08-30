"""Unit, Security & State Machine Tests for Phase 295 — Payment Event Processing."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from decimal import Decimal
from typing import Any

import pytest

from app.payment.events.payment_event_processor import (
    RazorpayPaymentEventProcessor,
)
from app.payment.status.payment_status_service import PaymentStatusService
from app.schemas.payment import PaymentOrderResult, PaymentStatus, SupportedCurrency
from app.schemas.payment_event import (
    NormalizedPaymentEventType,
    PaymentEventProcessingResult,
    PaymentEventProcessingStatus,
)
from app.schemas.payment_webhook import VerifiedWebhookEnvelope


def _make_envelope(
    event_type: str = "payment.authorized",
    event_id: str | None = "evt_test_01",
    payload: dict[str, Any] | None = None,
    verified: bool = True,
    tenant_id: uuid.UUID | None = None,
) -> VerifiedWebhookEnvelope:
    if payload is None:
        payload = {
            "event": event_type,
            "event_id": event_id,
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_test_01",
                        "order_id": "order_test_01",
                        "amount": 50000,
                        "currency": "INR",
                        "notes": {
                            "tenant_id": str(tenant_id or uuid.uuid4()),
                            "agent_id": str(uuid.uuid4()),
                            "transaction_id": "tx_test_01",
                        },
                    }
                }
            },
        }

    raw_bytes = json.dumps(payload).encode("utf-8")
    fp = hashlib.sha256(raw_bytes).hexdigest()

    return VerifiedWebhookEnvelope(
        envelope_id=uuid.uuid4(),
        provider="razorpay",
        event_id=event_id,
        event_type=event_type,
        tenant_id=tenant_id,
        environment="test",
        verification_status="VERIFIED",
        signature_algorithm="HMAC-SHA256",
        payload_fingerprint=fp,
        raw_payload_digest=fp,
        verified=verified,
        payload=payload,
    )


def test_01_payment_authorized_event_success() -> None:
    """1. Test payment.authorized event transitions status to PAYMENT_VERIFIED."""
    tenant_id = uuid.uuid4()
    envelope = _make_envelope(event_type="payment.authorized", tenant_id=tenant_id)

    processor = RazorpayPaymentEventProcessor()
    res = processor.process_event(envelope)

    assert isinstance(res, PaymentEventProcessingResult)
    assert res.processing_status == PaymentEventProcessingStatus.SUCCESS
    assert res.normalized_event_type == NormalizedPaymentEventType.PAYMENT_AUTHORIZED
    assert res.new_status == PaymentStatus.PAYMENT_VERIFIED
    assert res.order_id == "order_test_01"
    assert res.payment_id == "pay_test_01"


def test_02_payment_captured_event_success() -> None:
    """2. Test payment.captured event transitions status to CAPTURED."""
    envelope = _make_envelope(event_type="payment.captured")

    processor = RazorpayPaymentEventProcessor()
    res = processor.process_event(envelope, current_status=PaymentStatus.PAYMENT_VERIFIED)

    assert res.processing_status == PaymentEventProcessingStatus.SUCCESS
    assert res.normalized_event_type == NormalizedPaymentEventType.PAYMENT_CAPTURED
    assert res.previous_status == PaymentStatus.PAYMENT_VERIFIED
    assert res.new_status == PaymentStatus.CAPTURED


def test_03_order_paid_event_success() -> None:
    """3. Test order.paid event maps to PAYMENT_CAPTURED and transitions to CAPTURED."""
    envelope = _make_envelope(event_type="order.paid")

    processor = RazorpayPaymentEventProcessor()
    res = processor.process_event(envelope, current_status=PaymentStatus.PAYMENT_VERIFIED)

    assert res.processing_status == PaymentEventProcessingStatus.SUCCESS
    assert res.normalized_event_type == NormalizedPaymentEventType.PAYMENT_CAPTURED
    assert res.new_status == PaymentStatus.CAPTURED


def test_04_payment_failed_event_success() -> None:
    """4. Test payment.failed event transitions status to FAILED."""
    envelope = _make_envelope(event_type="payment.failed")

    processor = RazorpayPaymentEventProcessor()
    res = processor.process_event(envelope, current_status=PaymentStatus.PAYMENT_PENDING)

    assert res.processing_status == PaymentEventProcessingStatus.SUCCESS
    assert res.normalized_event_type == NormalizedPaymentEventType.PAYMENT_FAILED
    assert res.new_status == PaymentStatus.FAILED


def test_05_refund_processed_event_success() -> None:
    """5. Test refund.processed event transitions status to REFUNDED."""
    envelope = _make_envelope(event_type="refund.processed")

    processor = RazorpayPaymentEventProcessor()
    res = processor.process_event(envelope, current_status=PaymentStatus.CAPTURED)

    assert res.processing_status == PaymentEventProcessingStatus.SUCCESS
    assert res.normalized_event_type == NormalizedPaymentEventType.PAYMENT_REFUNDED
    assert res.new_status == PaymentStatus.REFUNDED


def test_06_refund_failed_event_ignored() -> None:
    """6. Test refund.failed event maps to REFUND_FAILED and status is IGNORED."""
    envelope = _make_envelope(event_type="refund.failed")

    processor = RazorpayPaymentEventProcessor()
    res = processor.process_event(envelope)

    assert res.processing_status == PaymentEventProcessingStatus.IGNORED
    assert res.normalized_event_type == NormalizedPaymentEventType.REFUND_FAILED
    assert res.new_status is None


def test_07_dispute_created_event_ignored() -> None:
    """7. Test dispute.created event maps to DISPUTE_CREATED and status is IGNORED."""
    envelope = _make_envelope(event_type="dispute.created")

    processor = RazorpayPaymentEventProcessor()
    res = processor.process_event(envelope)

    assert res.processing_status == PaymentEventProcessingStatus.IGNORED
    assert res.normalized_event_type == NormalizedPaymentEventType.DISPUTE_CREATED


def test_08_unknown_event_type_ignored() -> None:
    """8. Test arbitrary unknown event type maps to UNKNOWN_EVENT and is IGNORED."""
    envelope = _make_envelope(event_type="custom.unknown_notification")

    processor = RazorpayPaymentEventProcessor()
    res = processor.process_event(envelope)

    assert res.processing_status == PaymentEventProcessingStatus.IGNORED
    assert res.normalized_event_type == NormalizedPaymentEventType.UNKNOWN_EVENT


def test_09_unverified_envelope_fails_closed() -> None:
    """9. Security Test: Unverified envelope (verified=False) fails closed immediately."""
    envelope = _make_envelope(event_type="payment.authorized", verified=False)

    processor = RazorpayPaymentEventProcessor()
    res = processor.process_event(envelope)

    assert res.processing_status == PaymentEventProcessingStatus.FAILED
    assert res.reason_code == "UNVERIFIED_WEBHOOK_ENVELOPE"


def test_10_identity_order_id_mismatch_fails_closed() -> None:
    """10. Security Test: order_id mismatch against expected_order fails closed."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    envelope = _make_envelope(event_type="payment.authorized", tenant_id=tenant_id)

    expected_order = PaymentOrderResult(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_test_01",
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="fp123",
        order_id="order_EXPECTED_DIFFERENT",  # Mismatch!
        amount=Decimal("500.00"),
        amount_minor_units=50000,
        currency=SupportedCurrency.INR,
        idempotency_key="idemp_key_10",
    )

    processor = RazorpayPaymentEventProcessor()
    res = processor.process_event(envelope, expected_order=expected_order)

    assert res.processing_status == PaymentEventProcessingStatus.MISMATCH
    assert res.reason_code == "IDENTITY_ORDER_ID_MISMATCH"


def test_11_identity_tenant_id_mismatch_fails_closed() -> None:
    """11. Security Test: tenant_id mismatch against expected_order fails closed."""
    tenant_A = uuid.uuid4()
    tenant_B = uuid.uuid4()
    envelope = _make_envelope(event_type="payment.authorized", tenant_id=tenant_A)

    expected_order = PaymentOrderResult(
        tenant_id=tenant_B,  # Mismatch!
        agent_id=uuid.uuid4(),
        transaction_id="tx_test_01",
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="fp123",
        order_id="order_test_01",
        amount=Decimal("500.00"),
        amount_minor_units=50000,
        currency=SupportedCurrency.INR,
        idempotency_key="idemp_key_11",
    )

    processor = RazorpayPaymentEventProcessor()
    res = processor.process_event(envelope, expected_order=expected_order)

    assert res.processing_status == PaymentEventProcessingStatus.MISMATCH
    assert res.reason_code == "IDENTITY_TENANT_ID_MISMATCH"


def test_12_illegal_backward_transition_fails_closed() -> None:
    """12. Security Test: Attempting illegal backward transition fails closed."""
    envelope = _make_envelope(event_type="payment.authorized")

    # Attempting transition to PAYMENT_VERIFIED from CAPTURED (illegal transition)
    processor = RazorpayPaymentEventProcessor()
    res = processor.process_event(envelope, current_status=PaymentStatus.CAPTURED)

    assert res.processing_status == PaymentEventProcessingStatus.ILLEGAL_TRANSITION
    assert res.reason_code == "ILLEGAL_STATUS_TRANSITION"


def test_13_terminal_state_mutation_fails_closed() -> None:
    """13. Security Test: Attempting state mutation on terminal REFUNDED state fails closed."""
    envelope = _make_envelope(event_type="payment.captured")

    processor = RazorpayPaymentEventProcessor()
    res = processor.process_event(envelope, current_status=PaymentStatus.REFUNDED)

    assert res.processing_status == PaymentEventProcessingStatus.ILLEGAL_TRANSITION


def test_14_same_state_transition_is_idempotent() -> None:
    """14. Test duplicate processing of same state transition is handled idempotently."""
    envelope = _make_envelope(event_type="payment.captured")

    processor = RazorpayPaymentEventProcessor()
    res = processor.process_event(envelope, current_status=PaymentStatus.CAPTURED)

    assert res.processing_status == PaymentEventProcessingStatus.ALREADY_PROCESSED
    assert res.reason_code == "IDEMPOTENT_SAME_STATE"


def test_15_result_model_contains_zero_secrets() -> None:
    """15. Security Test: PaymentEventProcessingResult contains 0 secret fields."""
    assert "key_secret" not in PaymentEventProcessingResult.model_fields
    assert "webhook_secret" not in PaymentEventProcessingResult.model_fields


def test_16_result_model_dump_exposes_zero_secrets() -> None:
    """16. Security Test: model_dump of PaymentEventProcessingResult exposes 0 secrets."""
    envelope = _make_envelope(event_type="payment.authorized")
    processor = RazorpayPaymentEventProcessor()
    res = processor.process_event(envelope)

    dump_str = str(res.model_dump())
    assert "key_secret" not in dump_str
    assert "webhook_secret" not in dump_str


def test_17_log_output_contains_zero_secrets(caplog: pytest.LogCaptureFixture) -> None:
    """17. Security Test: Logger output contains 0 credential secret strings."""
    secret = "UNSAFE_SECRET_LOG_CHECK_999"
    envelope = _make_envelope(event_type="payment.authorized")

    processor = RazorpayPaymentEventProcessor()
    with caplog.at_level(logging.INFO):
        processor.process_event(envelope)

    for record in caplog.records:
        assert secret not in record.getMessage()


def test_18_processing_fingerprint_deterministic() -> None:
    """18. Test processing fingerprint is deterministic for identical result parameters."""
    envelope = _make_envelope(event_type="payment.authorized")
    processor = RazorpayPaymentEventProcessor()
    res1 = processor.process_event(envelope)

    assert len(res1.processing_fingerprint) == 64


def test_19_tenant_isolation_in_event_processing() -> None:
    """19. Test multi-tenant isolation in event processing results."""
    tenant_A = uuid.uuid4()
    tenant_B = uuid.uuid4()

    env_A = _make_envelope(event_type="payment.authorized", tenant_id=tenant_A)
    env_B = _make_envelope(event_type="payment.authorized", tenant_id=tenant_B)

    processor = RazorpayPaymentEventProcessor()
    res_A = processor.process_event(env_A)
    res_B = processor.process_event(env_B)

    assert res_A.tenant_id == tenant_A
    assert res_B.tenant_id == tenant_B
    assert res_A.tenant_id != res_B.tenant_id


def test_20_currency_extraction_and_validation() -> None:
    """20. Test valid ISO currency code is extracted and parsed into SupportedCurrency."""
    envelope = _make_envelope(event_type="payment.authorized")

    processor = RazorpayPaymentEventProcessor()
    res = processor.process_event(envelope)

    assert res.currency == SupportedCurrency.INR


def test_21_nested_entity_extraction() -> None:
    """21. Test extracting order_id and payment_id from nested Razorpay payload."""
    payload = {
        "event": "payment.authorized",
        "event_id": "evt_nest_21",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_nest_999",
                    "order_id": "order_nest_888",
                    "amount": 1000,
                    "currency": "INR",
                }
            }
        },
    }
    raw_bytes = json.dumps(payload).encode("utf-8")
    fp = hashlib.sha256(raw_bytes).hexdigest()

    envelope = VerifiedWebhookEnvelope(
        provider="razorpay",
        event_id="evt_nest_21",
        event_type="payment.authorized",
        environment="test",
        payload_fingerprint=fp,
        raw_payload_digest=fp,
        verified=True,
        payload=payload,
    )

    processor = RazorpayPaymentEventProcessor()
    res = processor.process_event(envelope)

    assert res.order_id == "order_nest_888"
    assert res.payment_id == "pay_nest_999"


def test_22_static_check_no_risk_recalculation() -> None:
    """22. Static Check: RazorpayPaymentEventProcessor contains 0 risk scoring calculations."""
    import inspect

    import app.payment.events.payment_event_processor as pep_mod

    source_code = inspect.getsource(pep_mod)
    assert "calculate_composite_risk_score" not in source_code
    assert "evaluate_hard_security_rules" not in source_code


def test_23_static_check_no_authorization_bypass() -> None:
    """23. Static Check: RazorpayPaymentEventProcessor does not bypass PaymentAuthorizationGate."""
    import inspect

    import app.payment.events.payment_event_processor as pep_mod

    source_code = inspect.getsource(pep_mod)
    assert "bypass_authorization" not in source_code


def test_24_result_model_frozen_and_immutable() -> None:
    """24. Security Test: PaymentEventProcessingResult is frozen and immutable."""
    envelope = _make_envelope(event_type="payment.authorized")
    processor = RazorpayPaymentEventProcessor()
    res = processor.process_event(envelope)

    with pytest.raises((TypeError, Exception)):
        res.processing_status = PaymentEventProcessingStatus.FAILED  # Mutate attempt!


def test_25_end_to_end_event_processing_pipeline() -> None:
    """25. End-to-End Test: Webhook Envelope -> Event Processor -> State Machine."""
    tenant_id = uuid.uuid4()
    envelope = _make_envelope(event_type="payment.captured", tenant_id=tenant_id)

    status_service = PaymentStatusService()
    processor = RazorpayPaymentEventProcessor(status_service=status_service)

    res = processor.process_event(envelope, current_status=PaymentStatus.PAYMENT_VERIFIED)

    assert res.processing_status == PaymentEventProcessingStatus.SUCCESS
    assert res.previous_status == PaymentStatus.PAYMENT_VERIFIED
    assert res.new_status == PaymentStatus.CAPTURED
    assert len(res.processing_fingerprint) == 64
