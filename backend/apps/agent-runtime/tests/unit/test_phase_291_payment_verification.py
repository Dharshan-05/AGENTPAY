"""Unit & Security Tests for Phase 291 — Payment Verification."""

from __future__ import annotations

import hashlib
import hmac
import logging
import uuid
from decimal import Decimal

import pytest
from pydantic import SecretStr

from app.payment.providers.razorpay.config import RazorpayConfiguration
from app.payment.providers.razorpay.provider import RazorpayProvider
from app.payment.verification.payment_verification import (
    PaymentVerificationService,
)
from app.schemas.payment import (
    PaymentOrderResult,
    PaymentVerificationRequest,
    PaymentVerificationResult,
    PaymentVerificationStatus,
    SupportedCurrency,
)


def _make_enabled_provider(
    key_id: str = "rzp_test_123", secret: str = "secret_456"
) -> RazorpayProvider:
    config = RazorpayConfiguration(
        key_id=key_id,
        key_secret=SecretStr(secret),
        enabled=True,
        environment_mode="test",
    )
    return RazorpayProvider(config=config)


def _make_valid_order_result(
    t_id: uuid.UUID | None = None,
    a_id: uuid.UUID | None = None,
    tx_id: str = "tx_291_01",
    order_id: str = "order_rzp_mock_123",
    amount: Decimal = Decimal("100.00"),
    currency: SupportedCurrency = SupportedCurrency.INR,
    auth_id: uuid.UUID | None = None,
    auth_fp: str = "fp_291_auth",
) -> PaymentOrderResult:
    return PaymentOrderResult(
        order_id=order_id,
        provider_name="razorpay",
        tenant_id=t_id or uuid.uuid4(),
        agent_id=a_id or uuid.uuid4(),
        transaction_id=tx_id,
        amount=amount,
        amount_minor_units=10000,
        currency=currency,
        status="created",
        idempotency_key="idemp_291_01",
        authorization_id=auth_id or uuid.uuid4(),
        authorization_fingerprint=auth_fp,
        payment_success=False,
        payment_verified=False,
        captured=False,
    )


def test_01_valid_signature_produces_verified() -> None:
    """1. Test valid Razorpay signature and matching order context produces VERIFIED status."""
    order_res = _make_valid_order_result()
    payment_id = "pay_rzp_mock_999"
    key_secret = "secret_456"

    # Compute valid HMAC-SHA256 signature
    msg = f"{order_res.order_id}|{payment_id}".encode()
    sig = hmac.new(key_secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()

    req = PaymentVerificationRequest(
        tenant_id=order_res.tenant_id,
        agent_id=order_res.agent_id,
        transaction_id=order_res.transaction_id,
        order_id=order_res.order_id,
        payment_id=payment_id,
        signature=sig,
        amount=order_res.amount,
        currency=order_res.currency,
        authorization_id=order_res.authorization_id,
        authorization_fingerprint=order_res.authorization_fingerprint,
        idempotency_key="idemp_291_01",
    )

    svc = PaymentVerificationService(provider=_make_enabled_provider())
    res = svc.verify_payment(req, order_result=order_res)

    assert isinstance(res, PaymentVerificationResult)
    assert res.status == PaymentVerificationStatus.VERIFIED
    assert res.payment_success is True
    assert res.payment_verified is True
    assert res.captured is False
    assert res.reason_code == "PAYMENT_VERIFIED_SUCCESSFULLY"


def test_02_invalid_signature_rejected() -> None:
    """2. Security Test: Invalid HMAC signature produces INVALID_SIGNATURE failure."""
    order_res = _make_valid_order_result()
    req = PaymentVerificationRequest(
        tenant_id=order_res.tenant_id,
        agent_id=order_res.agent_id,
        transaction_id=order_res.transaction_id,
        order_id=order_res.order_id,
        payment_id="pay_rzp_mock_999",
        signature="invalid_signature_forged_digest_123",
        amount=order_res.amount,
        currency=order_res.currency,
        authorization_id=order_res.authorization_id,
        authorization_fingerprint=order_res.authorization_fingerprint,
        idempotency_key="idemp_291_02",
    )

    svc = PaymentVerificationService(provider=_make_enabled_provider())
    res = svc.verify_payment(req, order_result=order_res)

    assert res.status == PaymentVerificationStatus.INVALID_SIGNATURE
    assert res.payment_success is False
    assert res.payment_verified is False


def test_03_tampered_order_id_rejected() -> None:
    """3. Security Test: Tampered order_id produces INVALID_ORDER failure."""
    order_res = _make_valid_order_result(order_id="order_orig_123")
    req = PaymentVerificationRequest(
        tenant_id=order_res.tenant_id,
        agent_id=order_res.agent_id,
        transaction_id=order_res.transaction_id,
        order_id="order_TAMPERED_999",  # Tampered!
        payment_id="pay_rzp_mock_999",
        signature="sig_test",
        amount=order_res.amount,
        currency=order_res.currency,
        authorization_id=order_res.authorization_id,
        authorization_fingerprint=order_res.authorization_fingerprint,
        idempotency_key="idemp_291_03",
    )

    svc = PaymentVerificationService(provider=_make_enabled_provider())
    res = svc.verify_payment(req, order_result=order_res)

    assert res.status == PaymentVerificationStatus.INVALID_ORDER
    assert res.payment_success is False


def test_04_tampered_payment_id_rejected() -> None:
    """4. Security Test: Empty payment_id produces INVALID_PAYMENT failure."""
    order_res = _make_valid_order_result()
    with pytest.raises(ValueError):
        PaymentVerificationRequest(
            tenant_id=order_res.tenant_id,
            agent_id=order_res.agent_id,
            transaction_id=order_res.transaction_id,
            order_id=order_res.order_id,
            payment_id="   ",  # Empty!
            signature="sig_test",
            amount=order_res.amount,
            currency=order_res.currency,
            authorization_id=order_res.authorization_id,
            authorization_fingerprint=order_res.authorization_fingerprint,
            idempotency_key="idemp_291_04",
        )


def test_05_tenant_mismatch_rejected() -> None:
    """5. Security Test: Tenant ID mismatch produces IDENTITY_MISMATCH failure."""
    order_res = _make_valid_order_result()
    req = PaymentVerificationRequest(
        tenant_id=uuid.uuid4(),  # Different tenant!
        agent_id=order_res.agent_id,
        transaction_id=order_res.transaction_id,
        order_id=order_res.order_id,
        payment_id="pay_999",
        signature="sig_test",
        amount=order_res.amount,
        currency=order_res.currency,
        authorization_id=order_res.authorization_id,
        authorization_fingerprint=order_res.authorization_fingerprint,
        idempotency_key="idemp_291_05",
    )

    svc = PaymentVerificationService(provider=_make_enabled_provider())
    res = svc.verify_payment(req, order_result=order_res)

    assert res.status == PaymentVerificationStatus.IDENTITY_MISMATCH
    assert res.payment_success is False


def test_06_agent_mismatch_rejected() -> None:
    """6. Security Test: Agent ID mismatch produces IDENTITY_MISMATCH failure."""
    order_res = _make_valid_order_result()
    req = PaymentVerificationRequest(
        tenant_id=order_res.tenant_id,
        agent_id=uuid.uuid4(),  # Different agent!
        transaction_id=order_res.transaction_id,
        order_id=order_res.order_id,
        payment_id="pay_999",
        signature="sig_test",
        amount=order_res.amount,
        currency=order_res.currency,
        authorization_id=order_res.authorization_id,
        authorization_fingerprint=order_res.authorization_fingerprint,
        idempotency_key="idemp_291_06",
    )

    svc = PaymentVerificationService(provider=_make_enabled_provider())
    res = svc.verify_payment(req, order_result=order_res)

    assert res.status == PaymentVerificationStatus.IDENTITY_MISMATCH
    assert res.payment_success is False


def test_07_transaction_mismatch_rejected() -> None:
    """7. Security Test: Transaction ID mismatch produces IDENTITY_MISMATCH failure."""
    order_res = _make_valid_order_result()
    req = PaymentVerificationRequest(
        tenant_id=order_res.tenant_id,
        agent_id=order_res.agent_id,
        transaction_id="tx_TAMPERED",  # Different tx!
        order_id=order_res.order_id,
        payment_id="pay_999",
        signature="sig_test",
        amount=order_res.amount,
        currency=order_res.currency,
        authorization_id=order_res.authorization_id,
        authorization_fingerprint=order_res.authorization_fingerprint,
        idempotency_key="idemp_291_07",
    )

    svc = PaymentVerificationService(provider=_make_enabled_provider())
    res = svc.verify_payment(req, order_result=order_res)

    assert res.status == PaymentVerificationStatus.IDENTITY_MISMATCH
    assert res.payment_success is False


def test_08_amount_mismatch_rejected() -> None:
    """8. Security Test: Amount mismatch produces AMOUNT_MISMATCH failure."""
    order_res = _make_valid_order_result(amount=Decimal("100.00"))
    req = PaymentVerificationRequest(
        tenant_id=order_res.tenant_id,
        agent_id=order_res.agent_id,
        transaction_id=order_res.transaction_id,
        order_id=order_res.order_id,
        payment_id="pay_999",
        signature="sig_test",
        amount=Decimal("500.00"),  # Amount mismatch!
        currency=order_res.currency,
        authorization_id=order_res.authorization_id,
        authorization_fingerprint=order_res.authorization_fingerprint,
        idempotency_key="idemp_291_08",
    )

    svc = PaymentVerificationService(provider=_make_enabled_provider())
    res = svc.verify_payment(req, order_result=order_res)

    assert res.status == PaymentVerificationStatus.AMOUNT_MISMATCH
    assert res.payment_success is False


def test_09_currency_mismatch_rejected() -> None:
    """9. Security Test: Currency mismatch produces CURRENCY_MISMATCH failure."""
    order_res = _make_valid_order_result(currency=SupportedCurrency.INR)
    req = PaymentVerificationRequest(
        tenant_id=order_res.tenant_id,
        agent_id=order_res.agent_id,
        transaction_id=order_res.transaction_id,
        order_id=order_res.order_id,
        payment_id="pay_999",
        signature="sig_test",
        amount=order_res.amount,
        currency=SupportedCurrency.USD,  # Currency mismatch!
        authorization_id=order_res.authorization_id,
        authorization_fingerprint=order_res.authorization_fingerprint,
        idempotency_key="idemp_291_09",
    )

    svc = PaymentVerificationService(provider=_make_enabled_provider())
    res = svc.verify_payment(req, order_result=order_res)

    assert res.status == PaymentVerificationStatus.CURRENCY_MISMATCH
    assert res.payment_success is False


def test_10_authorization_fingerprint_mismatch_rejected() -> None:
    """10. Security Test: Authorization fingerprint mismatch produces IDENTITY_MISMATCH."""
    order_res = _make_valid_order_result(auth_fp="fp_original_123")
    req = PaymentVerificationRequest(
        tenant_id=order_res.tenant_id,
        agent_id=order_res.agent_id,
        transaction_id=order_res.transaction_id,
        order_id=order_res.order_id,
        payment_id="pay_999",
        signature="sig_test",
        amount=order_res.amount,
        currency=order_res.currency,
        authorization_id=order_res.authorization_id,
        authorization_fingerprint="fp_TAMPERED_999",  # FP mismatch!
        idempotency_key="idemp_291_10",
    )

    svc = PaymentVerificationService(provider=_make_enabled_provider())
    res = svc.verify_payment(req, order_result=order_res)

    assert res.status == PaymentVerificationStatus.IDENTITY_MISMATCH
    assert res.payment_success is False


def test_11_missing_payment_id_rejected() -> None:
    """11. Security Test: PaymentVerificationRequest rejects blank payment_id."""
    with pytest.raises(ValueError):
        PaymentVerificationRequest(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_11",
            order_id="order_11",
            payment_id="",
            signature="sig_11",
            amount=Decimal("100.00"),
            currency=SupportedCurrency.USD,
            authorization_id=uuid.uuid4(),
            authorization_fingerprint="fp_11",
            idempotency_key="idemp_11",
        )


def test_12_empty_signature_rejected() -> None:
    """12. Security Test: PaymentVerificationRequest rejects blank signature."""
    with pytest.raises(ValueError):
        PaymentVerificationRequest(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_12",
            order_id="order_12",
            payment_id="pay_12",
            signature="   ",
            amount=Decimal("100.00"),
            currency=SupportedCurrency.USD,
            authorization_id=uuid.uuid4(),
            authorization_fingerprint="fp_12",
            idempotency_key="idemp_12",
        )


def test_13_malformed_signature_rejected() -> None:
    """13. Security Test: Malformed signature fails HMAC verification cleanly."""
    order_res = _make_valid_order_result()
    req = PaymentVerificationRequest(
        tenant_id=order_res.tenant_id,
        agent_id=order_res.agent_id,
        transaction_id=order_res.transaction_id,
        order_id=order_res.order_id,
        payment_id="pay_rzp_mock_999",
        signature="---MALFORMED---",
        amount=order_res.amount,
        currency=order_res.currency,
        authorization_id=order_res.authorization_id,
        authorization_fingerprint=order_res.authorization_fingerprint,
        idempotency_key="idemp_291_13",
    )

    svc = PaymentVerificationService(provider=_make_enabled_provider())
    res = svc.verify_payment(req, order_result=order_res)

    assert res.status == PaymentVerificationStatus.INVALID_SIGNATURE
    assert res.payment_success is False


def test_14_key_secret_never_appears_in_result() -> None:
    """14. Security Test: Verification result contains 0 secret strings."""
    secret_val = "SECRET_STRING_MUST_NEVER_LEAK_999"
    provider = _make_enabled_provider(secret=secret_val)

    order_res = _make_valid_order_result()
    msg = f"{order_res.order_id}|pay_test".encode()
    sig = hmac.new(secret_val.encode("utf-8"), msg, hashlib.sha256).hexdigest()

    req = PaymentVerificationRequest(
        tenant_id=order_res.tenant_id,
        agent_id=order_res.agent_id,
        transaction_id=order_res.transaction_id,
        order_id=order_res.order_id,
        payment_id="pay_test",
        signature=sig,
        amount=order_res.amount,
        currency=order_res.currency,
        authorization_id=order_res.authorization_id,
        authorization_fingerprint=order_res.authorization_fingerprint,
        idempotency_key="idemp_291_14",
    )

    svc = PaymentVerificationService(provider=provider)
    res = svc.verify_payment(req, order_result=order_res)

    dump_str = str(res.model_dump())
    assert secret_val not in dump_str


def test_15_key_secret_never_appears_in_logs(caplog: pytest.LogCaptureFixture) -> None:
    """15. Security Test: Logging output during verification contains 0 secrets."""
    secret_val = "UNSAFE_SECRET_LOG_CHECK_888"
    provider = _make_enabled_provider(secret=secret_val)
    order_res = _make_valid_order_result()

    req = PaymentVerificationRequest(
        tenant_id=order_res.tenant_id,
        agent_id=order_res.agent_id,
        transaction_id=order_res.transaction_id,
        order_id=order_res.order_id,
        payment_id="pay_test",
        signature="invalid_sig",
        amount=order_res.amount,
        currency=order_res.currency,
        authorization_id=order_res.authorization_id,
        authorization_fingerprint=order_res.authorization_fingerprint,
        idempotency_key="idemp_291_15",
    )

    svc = PaymentVerificationService(provider=provider)
    with caplog.at_level(logging.INFO):
        svc.verify_payment(req, order_result=order_res)

    for record in caplog.records:
        assert secret_val not in record.getMessage()


def test_16_webhook_secret_never_exposed() -> None:
    """16. Security Test: PaymentVerificationResult has 0 webhook_secret attributes."""
    assert "webhook_secret" not in PaymentVerificationResult.model_fields
    assert "key_secret" not in PaymentVerificationResult.model_fields


def test_17_verification_cannot_bypass_authorization() -> None:
    """17. Security Test: Verification with mismatched authorization ID is rejected."""
    order_res = _make_valid_order_result(auth_id=uuid.uuid4())
    req = PaymentVerificationRequest(
        tenant_id=order_res.tenant_id,
        agent_id=order_res.agent_id,
        transaction_id=order_res.transaction_id,
        order_id=order_res.order_id,
        payment_id="pay_999",
        signature="sig_test",
        amount=order_res.amount,
        currency=order_res.currency,
        authorization_id=uuid.uuid4(),  # Mismatched authorization ID!
        authorization_fingerprint=order_res.authorization_fingerprint,
        idempotency_key="idemp_291_17",
    )

    svc = PaymentVerificationService(provider=_make_enabled_provider())
    res = svc.verify_payment(req, order_result=order_res)

    assert res.status == PaymentVerificationStatus.IDENTITY_MISMATCH
    assert res.payment_success is False


def test_18_block_decision_cannot_reach_verification() -> None:
    """18. Security Test: Un-authorized order cannot produce successful verification."""
    order_res = _make_valid_order_result(auth_fp="fp_unauthorized_block")
    req = PaymentVerificationRequest(
        tenant_id=order_res.tenant_id,
        agent_id=order_res.agent_id,
        transaction_id=order_res.transaction_id,
        order_id=order_res.order_id,
        payment_id="pay_999",
        signature="sig_test",
        amount=order_res.amount,
        currency=order_res.currency,
        authorization_id=order_res.authorization_id,
        authorization_fingerprint="fp_TAMPERED_BLOCK",
        idempotency_key="idemp_291_18",
    )

    svc = PaymentVerificationService(provider=_make_enabled_provider())
    res = svc.verify_payment(req, order_result=order_res)

    assert res.status != PaymentVerificationStatus.VERIFIED
    assert res.payment_success is False


def test_19_review_decision_cannot_reach_verification() -> None:
    """19. Security Test: Suspended decision order fails identity check."""
    order_res = _make_valid_order_result(auth_fp="fp_suspended_review")
    req = PaymentVerificationRequest(
        tenant_id=order_res.tenant_id,
        agent_id=order_res.agent_id,
        transaction_id=order_res.transaction_id,
        order_id=order_res.order_id,
        payment_id="pay_999",
        signature="sig_test",
        amount=order_res.amount,
        currency=order_res.currency,
        authorization_id=order_res.authorization_id,
        authorization_fingerprint="fp_FORGED_REVIEW",
        idempotency_key="idemp_291_19",
    )

    svc = PaymentVerificationService(provider=_make_enabled_provider())
    res = svc.verify_payment(req, order_result=order_res)

    assert res.status != PaymentVerificationStatus.VERIFIED
    assert res.payment_success is False


def test_20_duplicate_verification_is_deterministic() -> None:
    """20. Test duplicate verification calls produce identical results."""
    order_res = _make_valid_order_result()
    payment_id = "pay_rzp_mock_999"
    key_secret = "secret_456"

    msg = f"{order_res.order_id}|{payment_id}".encode()
    sig = hmac.new(key_secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()

    req = PaymentVerificationRequest(
        tenant_id=order_res.tenant_id,
        agent_id=order_res.agent_id,
        transaction_id=order_res.transaction_id,
        order_id=order_res.order_id,
        payment_id=payment_id,
        signature=sig,
        amount=order_res.amount,
        currency=order_res.currency,
        authorization_id=order_res.authorization_id,
        authorization_fingerprint=order_res.authorization_fingerprint,
        idempotency_key="idemp_291_20",
    )

    svc = PaymentVerificationService(provider=_make_enabled_provider())
    res1 = svc.verify_payment(req, order_result=order_res)
    res2 = svc.verify_payment(req, order_result=order_res)

    assert res1.status == res2.status
    assert res1.verification_fingerprint == res2.verification_fingerprint
    assert res1.payment_success == res2.payment_success


def test_21_provider_failure_fails_closed() -> None:
    """21. Security Test: Disabled provider causes UNAVAILABLE failure."""
    disabled_config = RazorpayConfiguration(enabled=False)
    disabled_provider = RazorpayProvider(config=disabled_config)

    order_res = _make_valid_order_result()
    req = PaymentVerificationRequest(
        tenant_id=order_res.tenant_id,
        agent_id=order_res.agent_id,
        transaction_id=order_res.transaction_id,
        order_id=order_res.order_id,
        payment_id="pay_999",
        signature="sig_test",
        amount=order_res.amount,
        currency=order_res.currency,
        authorization_id=order_res.authorization_id,
        authorization_fingerprint=order_res.authorization_fingerprint,
        idempotency_key="idemp_291_21",
    )

    svc = PaymentVerificationService(provider=disabled_provider)
    res = svc.verify_payment(req, order_result=order_res)

    assert res.status == PaymentVerificationStatus.UNAVAILABLE
    assert res.payment_success is False


def test_22_static_sdk_isolation_verification_service() -> None:
    """22. Static Check: PaymentVerificationService contains 0 razorpay SDK imports."""
    import inspect

    import app.payment.verification.payment_verification as pv_mod

    source_code = inspect.getsource(pv_mod)
    assert "import razorpay" not in source_code
    assert "from razorpay" not in source_code


def test_23_no_risk_recalculation_in_verification() -> None:
    """23. Static Check: PaymentVerificationService contains 0 risk scoring calculations."""
    import inspect

    import app.payment.verification.payment_verification as pv_mod

    source_code = inspect.getsource(pv_mod)
    assert "calculate_composite_risk_score" not in source_code
    assert "evaluate_hard_security_rules" not in source_code


def test_24_no_fake_payment_success() -> None:
    """24. Security Test: Unverified result MUST have payment_success=False."""
    order_res = _make_valid_order_result()
    req = PaymentVerificationRequest(
        tenant_id=order_res.tenant_id,
        agent_id=order_res.agent_id,
        transaction_id=order_res.transaction_id,
        order_id=order_res.order_id,
        payment_id="pay_test",
        signature="invalid_signature",
        amount=order_res.amount,
        currency=order_res.currency,
        authorization_id=order_res.authorization_id,
        authorization_fingerprint=order_res.authorization_fingerprint,
        idempotency_key="idemp_291_24",
    )

    svc = PaymentVerificationService(provider=_make_enabled_provider())
    res = svc.verify_payment(req, order_result=order_res)

    assert res.payment_success is False
    assert res.payment_verified is False


def test_25_fingerprint_determinism() -> None:
    """25. Test verification fingerprint calculation is byte-identical for identical inputs."""
    t_id = uuid.uuid4()
    a_id = uuid.uuid4()
    auth_id = uuid.uuid4()

    fp1 = PaymentVerificationService.calculate_verification_fingerprint(
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_25",
        order_id="order_25",
        payment_id="pay_25",
        amount=Decimal("100.00"),
        currency="INR",
        auth_id=auth_id,
        auth_fp="fp_25",
    )

    fp2 = PaymentVerificationService.calculate_verification_fingerprint(
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_25",
        order_id="order_25",
        payment_id="pay_25",
        amount=Decimal("100.00"),
        currency="INR",
        auth_id=auth_id,
        auth_fp="fp_25",
    )

    assert fp1 == fp2
    assert len(fp1) == 64
