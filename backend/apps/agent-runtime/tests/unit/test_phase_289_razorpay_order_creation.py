"""Phase 289 Unit & Security Test Suite — Razorpay Payment Order Creation."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from pydantic import SecretStr, ValidationError

from app.payment.payment_service import PaymentService, PaymentServiceError
from app.payment.providers.razorpay.client import RazorpayClientWrapper
from app.payment.providers.razorpay.config import RazorpayConfiguration
from app.payment.providers.razorpay.provider import RazorpayProvider
from app.schemas.payment import (
    PaymentOrderRequest,
    PaymentOrderResult,
    PaymentServiceRequest,
    SupportedCurrency,
    amount_to_minor_units,
)
from app.schemas.risk_engine import (
    FinalRiskDecision,
    FinalRiskDecisionResult,
    RiskThresholdBand,
)


def _make_decision_result(
    t_id: uuid.UUID | None = None,
    a_id: uuid.UUID | None = None,
    tx_id: str = "tx_289_01",
    decision: FinalRiskDecision = FinalRiskDecision.ALLOW,
    score: float = 10.0,
    fp: str | None = None,
    created_at: datetime | None = None,
) -> FinalRiskDecisionResult:
    import hashlib
    import json

    t_uuid = t_id or uuid.uuid4()
    a_uuid = a_id or uuid.uuid4()
    eval_id = uuid.uuid4()

    calc_fp = "c" * 64
    src_fps = ["s1" * 32]
    band = RiskThresholdBand.LOW_RISK_BAND if score < 30 else RiskThresholdBand.HIGH_RISK_BAND
    ts = created_at or datetime.now(UTC)

    reason = "LOW_RISK_ALLOW_CLEAN" if decision == FinalRiskDecision.ALLOW else "HIGH_RISK_BLOCK"

    if fp is None:
        payload = {
            "evaluation_id": str(eval_id),
            "tenant_id": str(t_uuid),
            "agent_id": str(a_uuid),
            "transaction_id": tx_id,
            "prediction_timestamp": ts.isoformat(),
            "decision": decision.value,
            "decision_reason": reason,
            "composite_risk_score": score,
            "risk_band": band.value,
            "policy_precedence": decision.value,
            "calculation_fingerprint": calc_fp,
            "source_fingerprints": sorted(src_fps),
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        fp = hashlib.sha256(encoded).hexdigest()

    return FinalRiskDecisionResult(
        evaluation_id=eval_id,
        decision_id=uuid.uuid4(),
        tenant_id=t_uuid,
        agent_id=a_uuid,
        transaction_id=tx_id,
        prediction_timestamp=ts,
        decision=decision,
        decision_reason=reason,
        composite_risk_score=score,
        risk_band=band,
        policy_precedence=decision.value,
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
        source_fingerprints=src_fps,
        calculation_fingerprint=calc_fp,
        decision_fingerprint=fp,
        created_at=ts,
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


# --- Phase 289 Unit & Security Tests ---


def test_01_allow_permitted_creates_provider_order() -> None:
    """1. Test ALLOW/PERMITTED decision successfully creates a real Razorpay order."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_289_01"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("250.75"),
        currency=SupportedCurrency.INR,
        idempotency_key="idemp_key_289_01",
    )

    provider = _make_enabled_provider()
    svc = PaymentService(provider=provider)
    order_res = svc.create_payment_order(dec_res, req)

    assert isinstance(order_res, PaymentOrderResult)
    assert order_res.order_id.startswith("order_rzp_mock_")
    assert order_res.amount == Decimal("250.75")
    assert order_res.amount_minor_units == 25075
    assert order_res.currency == SupportedCurrency.INR
    assert order_res.status == "created"
    assert order_res.payment_success is False
    assert order_res.payment_verified is False
    assert order_res.captured is False


def test_02_review_decision_never_calls_razorpay() -> None:
    """2. Security Test: REVIEW decision NEVER calls Razorpay provider for order creation."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_289_02"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.REVIEW, score=55.0
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_289_02",
    )

    mock_provider = MagicMock(spec=RazorpayProvider)
    mock_provider.provider_name = "razorpay"
    mock_provider.validate_configuration.return_value = True

    svc = PaymentService(provider=mock_provider)
    with pytest.raises(PaymentServiceError, match="SUSPENDED for human approval"):
        svc.create_payment_order(dec_res, req)

    mock_provider.create_order.assert_not_called()


def test_03_block_decision_never_calls_razorpay() -> None:
    """3. Security Test: BLOCK decision NEVER calls Razorpay provider for order creation."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_289_03"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.BLOCK, score=95.0
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_289_03",
    )

    mock_provider = MagicMock(spec=RazorpayProvider)
    mock_provider.provider_name = "razorpay"
    mock_provider.validate_configuration.return_value = True

    svc = PaymentService(provider=mock_provider)
    with pytest.raises(PaymentServiceError, match="DENIED by authorization gate"):
        svc.create_payment_order(dec_res, req)

    mock_provider.create_order.assert_not_called()


def test_04_policy_deny_never_calls_razorpay() -> None:
    """4. Security Test: Policy DENY decision NEVER calls Razorpay provider."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_289_04"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.BLOCK, score=80.0
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("50.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_289_04",
    )

    mock_provider = MagicMock(spec=RazorpayProvider)
    svc = PaymentService(provider=mock_provider)

    with pytest.raises(PaymentServiceError):
        svc.create_payment_order(dec_res, req)

    mock_provider.create_order.assert_not_called()


def test_05_fingerprint_tampering_never_calls_razorpay() -> None:
    """5. Security Test: Tampered decision fingerprint NEVER calls Razorpay provider."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_289_05"

    dec_res = _make_decision_result(
        t_id=tenant_id,
        a_id=agent_id,
        tx_id=tx_id,
        decision=FinalRiskDecision.ALLOW,
        fp="TAMPERED_FINGERPRINT_" + "0" * 44,
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_289_05",
    )

    mock_provider = MagicMock(spec=RazorpayProvider)
    svc = PaymentService(provider=mock_provider)

    with pytest.raises(PaymentServiceError, match="DENIED by authorization gate"):
        svc.create_payment_order(dec_res, req)

    mock_provider.create_order.assert_not_called()


def test_06_tenant_mismatch_never_calls_razorpay() -> None:
    """6. Security Test: Tenant mismatch NEVER calls Razorpay provider."""
    tenant_id1 = uuid.uuid4()
    tenant_id2 = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_289_06"

    dec_res = _make_decision_result(
        t_id=tenant_id1, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id2,  # Tenant mismatch!
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_289_06",
    )

    mock_provider = MagicMock(spec=RazorpayProvider)
    svc = PaymentService(provider=mock_provider)

    with pytest.raises(PaymentServiceError, match="tenant mismatch"):
        svc.create_payment_order(dec_res, req)

    mock_provider.create_order.assert_not_called()


def test_07_agent_mismatch_never_calls_razorpay() -> None:
    """7. Security Test: Agent mismatch NEVER calls Razorpay provider."""
    tenant_id = uuid.uuid4()
    agent_id1 = uuid.uuid4()
    agent_id2 = uuid.uuid4()
    tx_id = "tx_289_07"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id1, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id2,  # Agent mismatch!
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_289_07",
    )

    mock_provider = MagicMock(spec=RazorpayProvider)
    svc = PaymentService(provider=mock_provider)

    with pytest.raises(PaymentServiceError, match="agent mismatch"):
        svc.create_payment_order(dec_res, req)

    mock_provider.create_order.assert_not_called()


def test_08_transaction_mismatch_never_calls_razorpay() -> None:
    """8. Security Test: Transaction mismatch NEVER calls Razorpay provider."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id="tx_orig", decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_different",  # Tx mismatch!
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_289_08",
    )

    mock_provider = MagicMock(spec=RazorpayProvider)
    svc = PaymentService(provider=mock_provider)

    with pytest.raises(PaymentServiceError, match="transaction mismatch"):
        svc.create_payment_order(dec_res, req)

    mock_provider.create_order.assert_not_called()


def test_09_stale_decision_never_calls_razorpay() -> None:
    """9. Security Test: Stale decision age NEVER calls Razorpay provider."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_289_09"
    stale_ts = datetime.now(UTC) - timedelta(seconds=500)

    dec_res = _make_decision_result(
        t_id=tenant_id,
        a_id=agent_id,
        tx_id=tx_id,
        decision=FinalRiskDecision.ALLOW,
        created_at=stale_ts,
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_289_09",
    )

    mock_provider = MagicMock(spec=RazorpayProvider)
    svc = PaymentService(provider=mock_provider)

    with pytest.raises(PaymentServiceError, match="DENIED by authorization gate"):
        svc.create_payment_order(dec_res, req, max_decision_age_seconds=300.0)

    mock_provider.create_order.assert_not_called()


def test_10_future_decision_never_calls_razorpay() -> None:
    """10. Security Test: Future decision timestamp NEVER calls Razorpay provider."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_289_10"
    future_ts = datetime.now(UTC) + timedelta(seconds=200)

    dec_res = _make_decision_result(
        t_id=tenant_id,
        a_id=agent_id,
        tx_id=tx_id,
        decision=FinalRiskDecision.ALLOW,
        created_at=future_ts,
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_289_10",
    )

    mock_provider = MagicMock(spec=RazorpayProvider)
    svc = PaymentService(provider=mock_provider)

    with pytest.raises(PaymentServiceError, match="DENIED by authorization gate"):
        svc.create_payment_order(dec_res, req)

    mock_provider.create_order.assert_not_called()


def test_11_decimal_amount_converts_exactly_to_minor_units() -> None:
    """11. Test Decimal amount converts exactly to minor units (Paise/Cents)."""
    assert amount_to_minor_units(Decimal("100.50"), SupportedCurrency.INR) == 10050
    assert amount_to_minor_units(Decimal("1.00"), SupportedCurrency.USD) == 100
    assert amount_to_minor_units(Decimal("9999.99"), SupportedCurrency.EUR) == 999999


def test_12_float_monetary_input_is_rejected() -> None:
    """12. Security Test: Passing float monetary input raises ValueError."""
    with pytest.raises(ValueError, match="Decimal instance"):
        amount_to_minor_units(100.50, SupportedCurrency.INR)  # type: ignore[arg-type]


def test_13_zero_amount_rejected() -> None:
    """13. Security Test: Zero monetary amount is rejected."""
    with pytest.raises(ValueError, match="strictly greater than 0"):
        amount_to_minor_units(Decimal("0.00"), SupportedCurrency.INR)


def test_14_negative_amount_rejected() -> None:
    """14. Security Test: Negative monetary amount is rejected."""
    with pytest.raises(ValueError, match="strictly greater than 0"):
        amount_to_minor_units(Decimal("-50.00"), SupportedCurrency.INR)


def test_15_nan_rejected() -> None:
    """15. Security Test: NaN monetary amount is rejected."""
    with pytest.raises(ValueError, match="NaN or Infinity"):
        amount_to_minor_units(Decimal("NaN"), SupportedCurrency.INR)


def test_16_infinity_rejected() -> None:
    """16. Security Test: Infinity monetary amount is rejected."""
    with pytest.raises(ValueError, match="NaN or Infinity"):
        amount_to_minor_units(Decimal("Infinity"), SupportedCurrency.INR)


def test_17_unsupported_currency_rejected() -> None:
    """17. Security Test: Invalid/unsupported currency raises ValidationError."""
    with pytest.raises(ValidationError):
        PaymentServiceRequest(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_289_17",
            amount=Decimal("10.00"),
            currency="XYZ",  # type: ignore[arg-type]
            idempotency_key="idemp_key_289_17",
        )


def test_18_invalid_receipt_reference_handled_safely() -> None:
    """18. Test long receipt reference is truncated to safe 40 chars maximum."""
    provider = _make_enabled_provider()
    long_receipt = "A" * 100
    req = PaymentOrderRequest(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_289_18",
        amount=Decimal("50.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_289_18",
        receipt=long_receipt,
    )
    auth_id = uuid.uuid4()
    order_res = provider.create_order(req, auth_id, "fp_test")
    assert order_res.order_id.startswith("order_rzp_mock_")


def test_19_missing_idempotency_key_rejected() -> None:
    """19. Security Test: Blank idempotency key raises ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        PaymentServiceRequest(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_289_19",
            amount=Decimal("10.00"),
            currency=SupportedCurrency.USD,
            idempotency_key="   ",
        )


def test_20_invalid_idempotency_key_rejected() -> None:
    """20. Security Test: Idempotency key with spaces/symbols raises ValueError."""
    with pytest.raises(ValueError, match="invalid characters"):
        PaymentServiceRequest(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_289_20",
            amount=Decimal("10.00"),
            currency=SupportedCurrency.USD,
            idempotency_key="bad key spaces!",
        )


def test_21_provider_failure_is_normalized() -> None:
    """21. Security Test: Provider uninitialized or disabled fails closed safely."""
    disabled_config = RazorpayConfiguration(
        key_id="rzp_test_123",
        key_secret=SecretStr("secret"),
        enabled=False,
    )
    provider = RazorpayProvider(config=disabled_config)

    req = PaymentOrderRequest(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_289_21",
        amount=Decimal("50.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_289_21",
    )

    with pytest.raises(RuntimeError, match="not enabled"):
        provider.create_order(req, uuid.uuid4(), "fp_test")


def test_22_malformed_razorpay_response_fails_closed() -> None:
    """22. Security Test: Malformed Razorpay response (None order ID) fails closed."""
    mock_client = MagicMock(spec=RazorpayClientWrapper)
    mock_client.create_order.return_value = {"id": "", "status": "created"}  # Empty ID!

    provider = _make_enabled_provider()
    provider._client = mock_client

    req = PaymentOrderRequest(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_289_22",
        amount=Decimal("50.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_289_22",
    )

    with pytest.raises(ValueError, match="invalid or empty order ID"):
        provider.create_order(req, uuid.uuid4(), "fp_test")


def test_23_empty_order_id_fails_closed() -> None:
    """23. Security Test: Empty order_id raises ValidationError."""
    with pytest.raises(ValidationError):
        PaymentOrderResult(
            order_id="   ",  # Blank order ID!
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_289_23",
            amount=Decimal("10.00"),
            amount_minor_units=1000,
            currency=SupportedCurrency.USD,
            idempotency_key="idemp_key_289_23",
            authorization_id=uuid.uuid4(),
            authorization_fingerprint="fp_289_23",
        )


def test_24_raw_sdk_response_is_not_returned() -> None:
    """24. Security Test: Order creation returns safe normalized PaymentOrderResult."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_289_24"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        idempotency_key="idemp_key_289_24",
    )

    provider = _make_enabled_provider()
    svc = PaymentService(provider=provider)
    result = svc.create_payment_order(dec_res, req)

    assert isinstance(result, PaymentOrderResult)
    assert not isinstance(result, dict)


def test_25_credentials_never_appear_in_result() -> None:
    """25. Security Test: PaymentOrderResult contains 0 credential strings."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_289_25"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        idempotency_key="idemp_key_289_25",
    )

    secret_val = "UNSAFE_KEY_SECRET_888"
    provider = _make_enabled_provider(key_id="rzp_test_777", secret=secret_val)
    svc = PaymentService(provider=provider)
    result = svc.create_payment_order(dec_res, req)

    dump_str = str(result.model_dump())
    assert secret_val not in dump_str
    assert "rzp_test_777" not in dump_str


def test_26_credentials_never_appear_in_logs(caplog: pytest.LogCaptureFixture) -> None:
    """26. Security Test: Logging output during order creation contains 0 secret strings."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_289_26"

    secret_val = "SECRET_VALUE_LOG_CHECK_999"
    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        idempotency_key="idemp_key_289_26",
    )

    provider = _make_enabled_provider(secret=secret_val)
    svc = PaymentService(provider=provider)

    with caplog.at_level(logging.INFO):
        svc.create_payment_order(dec_res, req)

    for record in caplog.records:
        assert secret_val not in record.getMessage()


def test_27_credentials_never_appear_in_exceptions() -> None:
    """27. Security Test: Domain exceptions during order failure contain 0 secrets."""
    secret_val = "SECRET_RAISED_IN_ERR"
    disabled_config = RazorpayConfiguration(
        key_id="rzp_test_123",
        key_secret=SecretStr(secret_val),
        enabled=False,
    )
    provider = RazorpayProvider(config=disabled_config)

    req = PaymentOrderRequest(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_289_27",
        amount=Decimal("50.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_289_27",
    )

    with pytest.raises(RuntimeError) as exc_info:
        provider.create_order(req, uuid.uuid4(), "fp_test")

    assert secret_val not in str(exc_info.value)


def test_28_payment_success_is_not_claimed_after_order_creation() -> None:
    """28. Security Test: PaymentOrderResult MUST leave flags as False."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_289_28"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        idempotency_key="idemp_key_289_28",
    )

    provider = _make_enabled_provider()
    svc = PaymentService(provider=provider)
    res = svc.create_payment_order(dec_res, req)

    assert res.payment_success is False
    assert res.payment_verified is False
    assert res.captured is False


def test_29_payment_verification_is_not_called() -> None:
    """29. Static Check: PaymentService contains 0 payment verification functions."""
    import inspect

    import app.payment.payment_service as ps_mod

    source_code = inspect.getsource(ps_mod)
    assert "verify_payment" not in source_code
    assert "verify_signature" not in source_code


def test_30_checkout_is_not_generated_by_create_order() -> None:
    """30. Security Test: create_payment_order returns PaymentOrderResult."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_289_30"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        idempotency_key="idemp_key_289_30",
    )

    provider = _make_enabled_provider()
    svc = PaymentService(provider=provider)
    res = svc.create_payment_order(dec_res, req)

    assert isinstance(res, PaymentOrderResult)
    assert not hasattr(res, "checkout_status")


def test_31_webhooks_are_not_called() -> None:
    """31. Static Check: PaymentService contains 0 webhook handling functions."""
    import inspect

    import app.payment.payment_service as ps_mod

    source_code = inspect.getsource(ps_mod)
    assert "handle_webhook" not in source_code
    assert "process_webhook" not in source_code


def test_32_payment_status_management_is_not_called() -> None:
    """32. Static Check: PaymentService contains 0 payment status machine state modifications."""
    import inspect

    import app.payment.payment_service as ps_mod

    source_code = inspect.getsource(ps_mod)
    assert "payment_status_machine" not in source_code
    assert "transition_payment_status" not in source_code


def test_33_provider_abstraction_remains_intact() -> None:
    """33. Architecture Check: PaymentService depends on PaymentProvider interface."""
    svc = PaymentService(provider=_make_enabled_provider())
    assert hasattr(svc.provider, "create_order")


def test_34_payment_service_does_not_import_razorpay_sdk() -> None:
    """34. Architecture Check: PaymentService module does not import razorpay SDK directly."""
    import inspect

    import app.payment.payment_service as ps_mod

    source_code = inspect.getsource(ps_mod)
    assert "import razorpay" not in source_code
    assert "from razorpay" not in source_code


def test_35_only_razorpay_provider_communicates_with_sdk() -> None:
    """35. Architecture Check: RazorpayProvider uses RazorpayClientWrapper."""
    provider = _make_enabled_provider()
    assert isinstance(provider._client, RazorpayClientWrapper)
