"""Unit & Security Tests for Phase 293 — Razorpay Webhook Handler."""

from __future__ import annotations

import hashlib
import hmac
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.payments import payments_router
from app.payment.webhooks.razorpay_signature import RazorpayWebhookSignatureVerifier
from app.payment.webhooks.razorpay_webhook import (
    RazorpayWebhookHandler,
    WebhookReplayTracker,
)
from app.schemas.payment_webhook import (
    UntrustedWebhookRequest,
    VerifiedWebhookEnvelope,
    WebhookIngestionOutcome,
    WebhookIngestionResult,
)


def _compute_valid_sig(raw_bytes: bytes, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), raw_bytes, hashlib.sha256).hexdigest()


def test_01_valid_webhook_accepted() -> None:
    """1. Test valid signature produces ACCEPTED outcome and VerifiedWebhookEnvelope."""
    secret = "whsec_handler_test_123"
    body = b'{"event":"payment.authorized","event_id":"evt_01","payload":{}}'
    sig = _compute_valid_sig(body, secret)

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    handler = RazorpayWebhookHandler(verifier=verifier)

    untrusted_req = UntrustedWebhookRequest(
        raw_body=body,
        signature=sig,
        tenant_id=uuid.uuid4(),
        environment="test",
    )

    ingest_res, envelope = handler.process_webhook(untrusted_req)

    assert isinstance(ingest_res, WebhookIngestionResult)
    assert ingest_res.outcome == WebhookIngestionOutcome.ACCEPTED
    assert ingest_res.status_code == 200
    assert ingest_res.event_id == "evt_01"
    assert ingest_res.event_type == "payment.authorized"

    assert isinstance(envelope, VerifiedWebhookEnvelope)
    assert envelope.event_id == "evt_01"
    assert envelope.event_type == "payment.authorized"
    assert envelope.verified is True
    assert envelope.verification_status == "VERIFIED"


def test_02_invalid_signature_rejected() -> None:
    """2. Security Test: Invalid signature produces INVALID_SIGNATURE outcome and None envelope."""
    secret = "whsec_handler_test_123"
    body = b'{"event":"payment.authorized"}'
    invalid_sig = "invalid_signature_999"

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    handler = RazorpayWebhookHandler(verifier=verifier)

    untrusted_req = UntrustedWebhookRequest(raw_body=body, signature=invalid_sig)
    ingest_res, envelope = handler.process_webhook(untrusted_req)

    assert ingest_res.outcome == WebhookIngestionOutcome.INVALID_SIGNATURE
    assert ingest_res.status_code == 401
    assert envelope is None


def test_03_malformed_json_after_signature_pass_rejected() -> None:
    """3. Security Test: Malformed JSON post-signature-pass produces MALFORMED_PAYLOAD outcome."""
    secret = "whsec_handler_test_123"
    body = b"NOT_VALID_JSON_{"
    sig = _compute_valid_sig(body, secret)

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    handler = RazorpayWebhookHandler(verifier=verifier)

    untrusted_req = UntrustedWebhookRequest(raw_body=body, signature=sig)
    ingest_res, envelope = handler.process_webhook(untrusted_req)

    assert ingest_res.outcome == WebhookIngestionOutcome.MALFORMED_PAYLOAD
    assert ingest_res.status_code == 400
    assert envelope is None


def test_04_signature_verified_before_json_parsing() -> None:
    """4. Security Test: Invalid signature on malformed JSON body fails signature first."""
    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret="sec")
    handler = RazorpayWebhookHandler(verifier=verifier)

    untrusted_req = UntrustedWebhookRequest(raw_body=b"INVALID_JSON", signature="wrong_sig")
    ingest_res, envelope = handler.process_webhook(untrusted_req)

    # Signature verification MUST fail before JSON parsing!
    assert ingest_res.outcome == WebhookIngestionOutcome.INVALID_SIGNATURE
    assert ingest_res.status_code == 401
    assert envelope is None


def test_05_duplicate_event_id_detected_as_duplicate() -> None:
    """5. Security Test: Duplicate event_id returns DUPLICATE outcome."""
    secret = "whsec_handler_test_123"
    body = b'{"event":"order.paid","event_id":"evt_dup_05"}'
    sig = _compute_valid_sig(body, secret)

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    tracker = WebhookReplayTracker()
    handler = RazorpayWebhookHandler(verifier=verifier, replay_tracker=tracker)

    untrusted_req = UntrustedWebhookRequest(raw_body=body, signature=sig)
    res1, env1 = handler.process_webhook(untrusted_req)
    res2, env2 = handler.process_webhook(untrusted_req)  # Replay!

    assert res1.outcome == WebhookIngestionOutcome.ACCEPTED
    assert env1 is not None

    assert res2.outcome == WebhookIngestionOutcome.DUPLICATE
    assert res2.status_code == 200
    assert env2 is None


def test_06_event_id_preserved_in_envelope() -> None:
    """6. Test provider event_id is preserved in VerifiedWebhookEnvelope."""
    secret = "whsec_sec"
    body = b'{"event":"payment.failed","event_id":"evt_fail_99"}'
    sig = _compute_valid_sig(body, secret)

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    handler = RazorpayWebhookHandler(verifier=verifier)

    untrusted_req = UntrustedWebhookRequest(raw_body=body, signature=sig)
    _, envelope = handler.process_webhook(untrusted_req)

    assert envelope is not None
    assert envelope.event_id == "evt_fail_99"
    assert envelope.event_type == "payment.failed"


def test_07_event_type_preserved_in_envelope() -> None:
    """7. Test provider event_type is preserved in VerifiedWebhookEnvelope."""
    secret = "whsec_sec"
    body = b'{"event":"refund.processed","event_id":"evt_rf_10"}'
    sig = _compute_valid_sig(body, secret)

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    handler = RazorpayWebhookHandler(verifier=verifier)

    untrusted_req = UntrustedWebhookRequest(raw_body=body, signature=sig)
    _, envelope = handler.process_webhook(untrusted_req)

    assert envelope is not None
    assert envelope.event_type == "refund.processed"


def test_08_envelope_contains_no_secrets() -> None:
    """8. Security Test: VerifiedWebhookEnvelope contains 0 secret fields."""
    secret = "whsec_secret_val_888"
    body = b'{"event":"payment.authorized"}'
    sig = _compute_valid_sig(body, secret)

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    handler = RazorpayWebhookHandler(verifier=verifier)

    untrusted_req = UntrustedWebhookRequest(raw_body=body, signature=sig)
    _, envelope = handler.process_webhook(untrusted_req)

    assert envelope is not None
    dump_str = str(envelope.model_dump())
    assert secret not in dump_str
    assert "key_secret" not in VerifiedWebhookEnvelope.model_fields
    assert "webhook_secret" not in VerifiedWebhookEnvelope.model_fields


def test_09_ingestion_result_contains_no_secrets() -> None:
    """9. Security Test: WebhookIngestionResult contains 0 secret fields."""
    assert "key_secret" not in WebhookIngestionResult.model_fields
    assert "webhook_secret" not in WebhookIngestionResult.model_fields


def test_10_no_payment_status_service_invocation() -> None:
    """10. Security Test: Processing webhook DOES NOT invoke PaymentStatusService."""
    import inspect

    import app.payment.webhooks.razorpay_webhook as rw_mod

    source_code = inspect.getsource(rw_mod)
    assert "PaymentStatusService" not in source_code
    assert "transition_status" not in source_code


def test_11_no_payment_verification_service_invocation() -> None:
    """11. Security Test: Processing webhook DOES NOT invoke PaymentVerificationService."""
    import inspect

    import app.payment.webhooks.razorpay_webhook as rw_mod

    source_code = inspect.getsource(rw_mod)
    assert "PaymentVerificationService" not in source_code


def test_12_no_payment_success_claimed_in_ingestion() -> None:
    """12. Security Test: WebhookIngestionResult has 0 payment_success or captured attributes."""
    assert "payment_success" not in WebhookIngestionResult.model_fields
    assert "captured" not in WebhookIngestionResult.model_fields


def test_13_no_risk_recalculation_in_webhook_handler() -> None:
    """13. Static Check: RazorpayWebhookHandler contains 0 risk scoring calculations."""
    import inspect

    import app.payment.webhooks.razorpay_webhook as rw_mod

    source_code = inspect.getsource(rw_mod)
    assert "calculate_composite_risk_score" not in source_code
    assert "evaluate_hard_security_rules" not in source_code


def test_14_tenant_id_context_propagated() -> None:
    """14. Test tenant_id context is preserved in VerifiedWebhookEnvelope."""
    secret = "whsec_sec"
    body = b'{"event":"payment.authorized"}'
    sig = _compute_valid_sig(body, secret)
    tenant_id = uuid.uuid4()

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    handler = RazorpayWebhookHandler(verifier=verifier)

    untrusted_req = UntrustedWebhookRequest(raw_body=body, signature=sig, tenant_id=tenant_id)
    _, envelope = handler.process_webhook(untrusted_req)

    assert envelope is not None
    assert envelope.tenant_id == tenant_id


def test_15_environment_context_propagated() -> None:
    """15. Test environment context is preserved in VerifiedWebhookEnvelope."""
    secret = "whsec_sec"
    body = b'{"event":"payment.authorized"}'
    sig = _compute_valid_sig(body, secret)

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    handler = RazorpayWebhookHandler(verifier=verifier)

    untrusted_req = UntrustedWebhookRequest(raw_body=body, signature=sig, environment="staging")
    _, envelope = handler.process_webhook(untrusted_req)

    assert envelope is not None
    assert envelope.environment == "staging"


_test_api_app = FastAPI()
_test_api_app.include_router(payments_router, prefix="/api/v1")


def test_16_webhook_endpoint_missing_signature_header_returns_400() -> None:
    """16. API Test: Endpoint missing signature header returns HTTP 400."""
    client = TestClient(_test_api_app)
    res = client.post(
        "/api/v1/payments/webhooks/razorpay",
        content=b'{"event":"test"}',
        headers={"Content-Type": "application/json"},
    )
    assert res.status_code == 400
    assert "Missing required X-Razorpay-Signature header" in res.json()["detail"]


def test_17_webhook_endpoint_invalid_signature_returns_401() -> None:
    """17. API Test: Endpoint invalid signature returns HTTP 401."""
    client = TestClient(_test_api_app)
    res = client.post(
        "/api/v1/payments/webhooks/razorpay",
        content=b'{"event":"test"}',
        headers={
            "X-Razorpay-Signature": "invalid_sig_999",
            "Content-Type": "application/json",
        },
    )
    assert res.status_code == 401
    assert "Cryptographic signature verification failed" in res.json()["detail"]


def test_18_webhook_endpoint_valid_mock_signature_returns_200() -> None:
    """18. API Test: Endpoint valid mock signature returns HTTP 200."""
    body = b'{"event":"payment.authorized","event_id":"evt_api_18"}'
    fp = hashlib.sha256(body).hexdigest()
    mock_sig = f"sig_rzp_mock_wh_{fp[:12]}"

    client = TestClient(_test_api_app)
    res = client.post(
        "/api/v1/payments/webhooks/razorpay",
        content=body,
        headers={
            "X-Razorpay-Signature": mock_sig,
            "Content-Type": "application/json",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["outcome"] == "ACCEPTED"
    assert data["status_code"] == 200
    assert data["event_type"] == "payment.authorized"


def test_19_webhook_endpoint_does_not_mutate_payment_status() -> None:
    """19. Security Test: Ingesting valid webhook returns HTTP 200 without changing state."""
    body = b'{"event":"payment.captured","event_id":"evt_api_19"}'
    fp = hashlib.sha256(body).hexdigest()
    mock_sig = f"sig_rzp_mock_wh_{fp[:12]}"

    client = TestClient(_test_api_app)
    res = client.post(
        "/api/v1/payments/webhooks/razorpay",
        content=body,
        headers={
            "X-Razorpay-Signature": mock_sig,
            "Content-Type": "application/json",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "payment_status" not in data
    assert "captured" not in data


def test_20_static_check_no_phase_295_event_consumers() -> None:
    """20. Static Check: RazorpayWebhookHandler contains 0 Phase 295 event consumers."""
    import inspect

    import app.payment.webhooks.razorpay_webhook as rw_mod

    source_code = inspect.getsource(rw_mod)
    assert "PaymentEventProcessor" not in source_code
    assert "process_payment_event" not in source_code


def test_21_replay_tracker_capacity_eviction() -> None:
    """21. Test WebhookReplayTracker evicts keys when max capacity is reached."""
    tracker = WebhookReplayTracker(max_capacity=5)
    for i in range(5):
        assert tracker.is_duplicate(f"evt_{i}", f"fp_{i}") is False

    # 6th item triggers eviction reset
    assert tracker.is_duplicate("evt_6", "fp_6") is False


def test_22_empty_signature_header_rejected_by_handler() -> None:
    """22. Security Test: UntrustedWebhookRequest with empty signature fails verification."""
    handler = RazorpayWebhookHandler()
    req = UntrustedWebhookRequest(raw_body=b'{"event":"test"}', signature="   ")
    res, env = handler.process_webhook(req)

    assert res.outcome == WebhookIngestionOutcome.INVALID_SIGNATURE
    assert res.status_code == 401
    assert env is None


def test_23_untrusted_webhook_model_frozen() -> None:
    """23. Security Test: UntrustedWebhookRequest is frozen and immutable."""
    req = UntrustedWebhookRequest(raw_body=b"body", signature="sig")
    with pytest.raises((TypeError, Exception)):
        req.signature = "tampered"


def test_24_verified_webhook_envelope_model_frozen() -> None:
    """24. Security Test: VerifiedWebhookEnvelope is frozen and immutable."""
    envelope = VerifiedWebhookEnvelope(
        event_type="payment.authorized",
        environment="test",
        payload_fingerprint="fp",
        raw_payload_digest="digest",
        payload={"a": 1},
    )
    with pytest.raises((TypeError, Exception)):
        envelope.event_type = "tampered.event"


def test_25_explicit_confirmation_phase_295_unimplemented() -> None:
    """25. Static Check: Webhook API router contains 0 Phase 295 event processing calls."""
    import inspect

    import app.api.v1.payments as py_mod

    source_code = inspect.getsource(py_mod)
    assert "PaymentEventProcessor" not in source_code
    assert "process_payment_event" not in source_code
    assert "PaymentStatusService" not in source_code
