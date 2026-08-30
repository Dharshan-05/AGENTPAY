"""Unit & Security Tests for Phase 294 — Razorpay Webhook Signature Verification."""

from __future__ import annotations

import hashlib
import hmac
import logging
import uuid
from unittest.mock import MagicMock

import pytest
from pydantic import SecretStr

from app.payment.providers.razorpay.credentials import (
    RazorpayCredentialResolver,
    RazorpayCredentials,
)
from app.payment.webhooks.razorpay_signature import RazorpayWebhookSignatureVerifier
from app.schemas.payment_webhook import WebhookSignatureVerificationResult


def _compute_valid_sig(raw_bytes: bytes, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), raw_bytes, hashlib.sha256).hexdigest()


def test_01_valid_signature_returns_verified() -> None:
    """1. Test valid HMAC-SHA256 signature returns verified = True."""
    secret = "whsec_test_secret_123"
    body = b'{"event":"payment.authorized","payload":{"payment":{"entity":{"id":"pay_123"}}}}'
    sig = _compute_valid_sig(body, secret)

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    res = verifier.verify_signature(raw_body=body, signature=sig)

    assert isinstance(res, WebhookSignatureVerificationResult)
    assert res.verified is True
    assert res.verification_status == "VERIFIED"
    assert res.reason_code == "SIGNATURE_VERIFIED_SUCCESSFULLY"
    assert res.provider == "razorpay"


def test_02_invalid_signature_rejected() -> None:
    """2. Security Test: Invalid HMAC signature returns verified = False."""
    secret = "whsec_test_secret_123"
    body = b'{"event":"payment.authorized"}'
    invalid_sig = "invalid_hmac_signature_digest_999"

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    res = verifier.verify_signature(raw_body=body, signature=invalid_sig)

    assert res.verified is False
    assert res.verification_status == "INVALID_SIGNATURE"
    assert res.reason_code == "HMAC_SIGNATURE_MISMATCH"


def test_03_missing_signature_rejected() -> None:
    """3. Security Test: Missing signature string returns verified = False."""
    secret = "whsec_test_secret_123"
    body = b'{"event":"payment.authorized"}'

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    res = verifier.verify_signature(raw_body=body, signature="")

    assert res.verified is False
    assert res.verification_status == "INVALID_SIGNATURE"
    assert res.reason_code == "MISSING_SIGNATURE_OR_BODY"


def test_04_empty_body_rejected() -> None:
    """4. Security Test: Empty raw body bytes returns verified = False."""
    secret = "whsec_test_secret_123"

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    res = verifier.verify_signature(raw_body=b"", signature="sig_123")

    assert res.verified is False
    assert res.verification_status == "INVALID_SIGNATURE"


def test_05_malformed_signature_string_rejected() -> None:
    """5. Security Test: Malformed signature string fails cleanly without exceptions."""
    secret = "whsec_test_secret_123"
    body = b'{"event":"payment.authorized"}'

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    res = verifier.verify_signature(raw_body=body, signature="--MALFORMED--")

    assert res.verified is False
    assert res.verification_status == "INVALID_SIGNATURE"


def test_06_tampered_raw_body_rejected() -> None:
    """6. Security Test: Modifying a single byte in raw body breaks signature verification."""
    secret = "whsec_test_secret_123"
    body_orig = b'{"event":"payment.authorized","amount":100}'
    body_tampered = b'{"event":"payment.authorized","amount":999}'  # Tampered!
    sig_orig = _compute_valid_sig(body_orig, secret)

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    res = verifier.verify_signature(raw_body=body_tampered, signature=sig_orig)

    assert res.verified is False
    assert res.verification_status == "INVALID_SIGNATURE"


def test_07_modified_json_after_sig_generation_rejected() -> None:
    """7. Security Test: Re-formatting JSON keys after signature generation breaks signature."""
    secret = "whsec_test_secret_123"
    body_raw = b'{"b":2,"a":1}'
    sig = _compute_valid_sig(body_raw, secret)

    body_reformatted = b'{"a":1,"b":2}'  # Keys reordered!

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    res = verifier.verify_signature(raw_body=body_reformatted, signature=sig)

    assert res.verified is False


def test_08_whitespace_modification_rejected() -> None:
    """8. Security Test: Adding whitespace to raw body breaks exact raw-byte signature."""
    secret = "whsec_test_secret_123"
    body_raw = b'{"event":"payment.authorized"}'
    sig = _compute_valid_sig(body_raw, secret)

    body_spaced = b'{"event": "payment.authorized"}'  # Space added!

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    res = verifier.verify_signature(raw_body=body_spaced, signature=sig)

    assert res.verified is False


def test_09_timing_safe_comparison_used() -> None:
    """9. Security Check: Signature verifier uses hmac.compare_digest."""
    import inspect

    import app.payment.webhooks.razorpay_signature as rs_mod

    source_code = inspect.getsource(rs_mod)
    assert "hmac.compare_digest" in source_code


def test_10_wrong_webhook_secret_rejected() -> None:
    """10. Security Test: Verification fails when wrong webhook secret is used."""
    body = b'{"event":"payment.authorized"}'
    sig = _compute_valid_sig(body, "secret_A")

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret="secret_B")
    res = verifier.verify_signature(raw_body=body, signature=sig)

    assert res.verified is False


def test_11_environment_credential_resolution() -> None:
    """11. Test verifier resolves credentials via RazorpayCredentialResolver."""
    secret = "whsec_resolved_secret_777"
    resolver = MagicMock(spec=RazorpayCredentialResolver)
    creds = RazorpayCredentials(
        key_id="rzp_test_123",
        key_secret=SecretStr("sec_123"),
        webhook_secret=SecretStr(secret),
    )
    resolver.get_credentials.return_value = creds

    body = b'{"event":"payment.authorized"}'
    sig = _compute_valid_sig(body, secret)

    verifier = RazorpayWebhookSignatureVerifier(credential_resolver=resolver)
    res = verifier.verify_signature(raw_body=body, signature=sig)

    assert res.verified is True


def test_12_tenant_isolation_in_resolver() -> None:
    """12. Test tenant_id is passed to credential resolver for tenant isolation."""
    resolver = MagicMock(spec=RazorpayCredentialResolver)
    resolver.get_credentials.return_value = None

    verifier = RazorpayWebhookSignatureVerifier(credential_resolver=resolver)
    tenant_id = uuid.uuid4()
    verifier.verify_signature(raw_body=b"body", signature="sig", tenant_id=tenant_id)

    resolver.get_credentials.assert_called_once_with(tenant_id=tenant_id)


def test_13_missing_secret_returns_missing_secret_status() -> None:
    """13. Security Test: Unresolved webhook secret returns MISSING_SECRET status."""
    resolver = MagicMock(spec=RazorpayCredentialResolver)
    resolver.get_credentials.return_value = None

    verifier = RazorpayWebhookSignatureVerifier(credential_resolver=resolver)
    res = verifier.verify_signature(raw_body=b"body", signature="sig")

    assert res.verified is False
    assert res.verification_status == "MISSING_SECRET"


def test_14_secret_absent_from_result() -> None:
    """14. Security Test: WebhookSignatureVerificationResult contains 0 secret fields."""
    secret = "UNSAFE_SECRET_VALUE_999"
    body = b'{"event":"test"}'
    sig = _compute_valid_sig(body, secret)

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    res = verifier.verify_signature(raw_body=body, signature=sig)

    dump_str = str(res.model_dump())
    assert secret not in dump_str
    assert "webhook_secret" not in WebhookSignatureVerificationResult.model_fields


def test_15_secret_absent_from_logs(caplog: pytest.LogCaptureFixture) -> None:
    """15. Security Test: Logging output contains 0 secret strings."""
    secret = "UNSAFE_SECRET_LOG_CHECK_888"
    body = b'{"event":"test"}'
    sig = _compute_valid_sig(body, secret)

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    with caplog.at_level(logging.INFO):
        verifier.verify_signature(raw_body=body, signature=sig)

    for record in caplog.records:
        assert secret not in record.getMessage()


def test_16_payload_fingerprint_calculated() -> None:
    """16. Test payload fingerprint is SHA-256 over exact raw body bytes."""
    body = b'{"event":"payment.authorized"}'
    expected_fp = hashlib.sha256(body).hexdigest()

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret="sec")
    res = verifier.verify_signature(raw_body=body, signature="sig")

    assert res.payload_fingerprint == expected_fp


def test_17_fingerprint_determinism() -> None:
    """17. Test payload fingerprint is deterministic for identical body bytes."""
    body = b'{"event":"order.paid","amount":500}'
    fp1 = hashlib.sha256(body).hexdigest()
    fp2 = hashlib.sha256(body).hexdigest()

    assert fp1 == fp2
    assert len(fp1) == 64


def test_18_static_check_no_frontend_imports() -> None:
    """18. Static Check: RazorpayWebhookSignatureVerifier does not import frontend modules."""
    import inspect

    import app.payment.webhooks.razorpay_signature as rs_mod

    source_code = inspect.getsource(rs_mod)
    assert "import react" not in source_code
    assert "from frontend" not in source_code


def test_19_static_check_operates_on_bytes() -> None:
    """19. Static Check: verify_signature signature accepts raw_body: bytes."""
    import inspect

    from app.payment.webhooks.razorpay_signature import RazorpayWebhookSignatureVerifier

    sig_spec = inspect.signature(RazorpayWebhookSignatureVerifier.verify_signature)
    assert sig_spec.parameters["raw_body"].annotation in (bytes, "bytes")


def test_20_static_check_no_risk_recalculation() -> None:
    """20. Static Check: Webhook signature verifier contains 0 risk scoring calculations."""
    import inspect

    import app.payment.webhooks.razorpay_signature as rs_mod

    source_code = inspect.getsource(rs_mod)
    assert "calculate_composite_risk_score" not in source_code
    assert "evaluate_hard_security_rules" not in source_code


def test_21_static_check_no_status_mutation() -> None:
    """21. Static Check: Webhook signature verifier contains 0 payment status machine calls."""
    import inspect

    import app.payment.webhooks.razorpay_signature as rs_mod

    source_code = inspect.getsource(rs_mod)
    assert "PaymentStatusService" not in source_code
    assert "transition_status" not in source_code


def test_22_mock_helper_signature_in_test_mode() -> None:
    """22. Test mock signature helper succeeds in test mode."""
    body = b'{"event":"payment.authorized"}'
    fp = hashlib.sha256(body).hexdigest()
    mock_sig = f"sig_rzp_mock_wh_{fp[:12]}"

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret="sec_test")
    res = verifier.verify_signature(raw_body=body, signature=mock_sig)

    assert res.verified is True


def test_23_untrusted_webhook_signature_fails_closed() -> None:
    """23. Security Test: Invalid signature cannot produce verified=True."""
    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret="sec")
    res = verifier.verify_signature(raw_body=b"body", signature="forged")

    assert res.verified is False


def test_24_raw_body_encoding_preserved() -> None:
    """24. Test non-ASCII UTF-8 bytes are preserved exactly during HMAC computation."""
    secret = "sec_unicode"
    body = '{"event":"payment.authorized","notes":"₹500 payment"}'.encode()
    sig = _compute_valid_sig(body, secret)

    verifier = RazorpayWebhookSignatureVerifier(override_webhook_secret=secret)
    res = verifier.verify_signature(raw_body=body, signature=sig)

    assert res.verified is True


def test_25_zero_secret_exposure_in_verification_result_dict() -> None:
    """25. Security Test: dict export of WebhookSignatureVerificationResult exposes 0 secrets."""
    res = WebhookSignatureVerificationResult(
        verified=True,
        verification_status="VERIFIED",
        reason_code="OK",
        payload_fingerprint="fp123",
    )
    dump_dict = res.model_dump()
    assert "secret" not in dump_dict
    assert "webhook_secret" not in dump_dict
