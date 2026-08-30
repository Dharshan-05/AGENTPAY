"""Unit, Security & Static Architecture Tests for Phase 288 — Payment Service."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from pydantic import SecretStr, ValidationError

from app.payment.authorization.payment_authorization_gate import PaymentAuthorizationGate
from app.payment.payment_service import (
    PaymentService,
    PaymentServiceError,
)
from app.payment.providers.razorpay.config import RazorpayConfiguration
from app.payment.providers.razorpay.provider import RazorpayProvider
from app.schemas.payment import (
    PaymentServiceOutcome,
    PaymentServiceRequest,
    SupportedCurrency,
)
from app.schemas.risk_engine import (
    FinalRiskDecision,
    FinalRiskDecisionResult,
    RiskThresholdBand,
)


def _make_decision_result(
    t_id: uuid.UUID | None = None,
    a_id: uuid.UUID | None = None,
    tx_id: str = "tx_svc_01",
    decision: FinalRiskDecision = FinalRiskDecision.ALLOW,
    score: float = 10.0,
    fp: str | None = None,
    created_at: datetime | None = None,
) -> FinalRiskDecisionResult:
    t_uuid = t_id or uuid.uuid4()
    a_uuid = a_id or uuid.uuid4()
    eval_id = uuid.uuid4()

    calc_fp = "c" * 64
    src_fps = ["s1" * 32]
    band = RiskThresholdBand.LOW_RISK_BAND if score < 30 else RiskThresholdBand.HIGH_RISK_BAND
    ts = created_at or datetime.now(UTC)

    reason = "LOW_RISK_ALLOW_CLEAN" if decision == FinalRiskDecision.ALLOW else "HIGH_RISK_BLOCK"

    if fp is None:
        import hashlib
        import json

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


def _make_mock_provider() -> RazorpayProvider:
    config = RazorpayConfiguration(
        key_id="rzp_test_123",
        key_secret=SecretStr("secret_456"),
        enabled=True,
        environment_mode="test",
    )
    return RazorpayProvider(config=config)


def test_01_valid_authorized_request_reaches_provider_boundary() -> None:
    """1. Test ALLOW decision reaches AUTHORIZED_FOR_PAYMENT outcome."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_svc_01"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("150.50"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_12345",
    )

    svc = PaymentService(provider=_make_mock_provider())
    result = svc.evaluate_payment_request(dec_res, req)

    assert result.outcome == PaymentServiceOutcome.AUTHORIZED_FOR_PAYMENT
    assert result.amount == Decimal("150.50")
    assert result.currency == SupportedCurrency.USD
    assert result.payment_id is None
    assert result.order_id is None


def test_02_review_request_is_suspended() -> None:
    """2. Test REVIEW decision produces SUSPENDED_FOR_APPROVAL outcome."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_svc_02"

    dec_res = _make_decision_result(
        t_id=tenant_id,
        a_id=agent_id,
        tx_id=tx_id,
        decision=FinalRiskDecision.REVIEW,
        score=50.0,
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("200.00"),
        currency=SupportedCurrency.INR,
        idempotency_key="idemp_key_67890",
    )

    svc = PaymentService(provider=_make_mock_provider())
    result = svc.evaluate_payment_request(dec_res, req)

    assert result.outcome == PaymentServiceOutcome.SUSPENDED_FOR_APPROVAL


def test_03_block_request_is_denied() -> None:
    """3. Test BLOCK decision produces DENIED outcome."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_svc_03"

    dec_res = _make_decision_result(
        t_id=tenant_id,
        a_id=agent_id,
        tx_id=tx_id,
        decision=FinalRiskDecision.BLOCK,
        score=90.0,
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("500.00"),
        currency=SupportedCurrency.EUR,
        idempotency_key="idemp_key_abcde",
    )

    svc = PaymentService(provider=_make_mock_provider())
    result = svc.evaluate_payment_request(dec_res, req)

    assert result.outcome == PaymentServiceOutcome.DENIED


def test_04_fingerprint_tampering_is_denied() -> None:
    """4. Security Test: Tampered decision fingerprint produces DENIED outcome."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_svc_04"

    dec_res = _make_decision_result(
        t_id=tenant_id,
        a_id=agent_id,
        tx_id=tx_id,
        decision=FinalRiskDecision.ALLOW,
        fp="TAMPERED_" + "0" * 55,
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("50.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_tamper",
    )

    svc = PaymentService(provider=_make_mock_provider())
    result = svc.evaluate_payment_request(dec_res, req)

    assert result.outcome == PaymentServiceOutcome.DENIED


def test_05_tenant_mismatch_is_denied() -> None:
    """5. Security Test: Tenant mismatch produces DENIED outcome."""
    tenant_id1 = uuid.uuid4()
    tenant_id2 = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_svc_05"

    dec_res = _make_decision_result(
        t_id=tenant_id1, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id2,  # Tenant mismatch!
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("50.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_mismatch1",
    )

    svc = PaymentService(provider=_make_mock_provider())
    result = svc.evaluate_payment_request(dec_res, req)

    assert result.outcome == PaymentServiceOutcome.DENIED


def test_06_agent_mismatch_is_denied() -> None:
    """6. Security Test: Agent mismatch produces DENIED outcome."""
    tenant_id = uuid.uuid4()
    agent_id1 = uuid.uuid4()
    agent_id2 = uuid.uuid4()
    tx_id = "tx_svc_06"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id1, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id2,  # Agent mismatch!
        transaction_id=tx_id,
        amount=Decimal("50.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_mismatch2",
    )

    svc = PaymentService(provider=_make_mock_provider())
    result = svc.evaluate_payment_request(dec_res, req)

    assert result.outcome == PaymentServiceOutcome.DENIED


def test_07_transaction_mismatch_is_denied() -> None:
    """7. Security Test: Transaction mismatch produces DENIED outcome."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id="tx_orig", decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_other",  # Tx mismatch!
        amount=Decimal("50.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_mismatch3",
    )

    svc = PaymentService(provider=_make_mock_provider())
    result = svc.evaluate_payment_request(dec_res, req)

    assert result.outcome == PaymentServiceOutcome.DENIED


def test_08_stale_decision_is_denied() -> None:
    """8. Security Test: Stale decision age produces DENIED outcome."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_svc_08"
    stale_time = datetime.now(UTC) - timedelta(seconds=400)

    dec_res = _make_decision_result(
        t_id=tenant_id,
        a_id=agent_id,
        tx_id=tx_id,
        decision=FinalRiskDecision.ALLOW,
        created_at=stale_time,
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("50.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_stale",
    )

    svc = PaymentService(provider=_make_mock_provider())
    result = svc.evaluate_payment_request(dec_res, req, max_decision_age_seconds=300.0)

    assert result.outcome == PaymentServiceOutcome.DENIED


def test_09_zero_amount_rejected() -> None:
    """9. Security Test: Decimal zero amount raises ValueError."""
    with pytest.raises(ValueError, match="strictly greater than 0"):
        PaymentServiceRequest(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_09",
            amount=Decimal("0.00"),
            currency=SupportedCurrency.USD,
            idempotency_key="idemp_key_zero",
        )


def test_10_negative_amount_rejected() -> None:
    """10. Security Test: Decimal negative amount raises ValueError."""
    with pytest.raises(ValueError, match="strictly greater than 0"):
        PaymentServiceRequest(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_10",
            amount=Decimal("-50.00"),
            currency=SupportedCurrency.USD,
            idempotency_key="idemp_key_neg",
        )


def test_11_nan_amount_rejected() -> None:
    """11. Security Test: Decimal NaN amount raises ValidationError."""
    with pytest.raises(ValidationError):
        PaymentServiceRequest(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_11",
            amount=Decimal("NaN"),
            currency=SupportedCurrency.USD,
            idempotency_key="idemp_key_nan",
        )


def test_12_infinity_amount_rejected() -> None:
    """12. Security Test: Decimal Infinity amount raises ValidationError."""
    with pytest.raises(ValidationError):
        PaymentServiceRequest(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_12",
            amount=Decimal("Infinity"),
            currency=SupportedCurrency.USD,
            idempotency_key="idemp_key_inf",
        )


def test_13_decimal_precision_preserved() -> None:
    """13. Test Decimal precision is preserved accurately."""
    req = PaymentServiceRequest(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_13",
        amount=Decimal("123.456789"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_precision",
    )
    assert req.amount == Decimal("123.456789")


def test_14_missing_idempotency_key_rejected() -> None:
    """14. Security Test: Empty idempotency key raises ValueError."""
    with pytest.raises(ValueError, match="Idempotency key cannot be empty"):
        PaymentServiceRequest(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_14",
            amount=Decimal("10.00"),
            currency=SupportedCurrency.USD,
            idempotency_key="   ",
        )


def test_15_invalid_idempotency_key_rejected() -> None:
    """15. Security Test: Idempotency key with invalid characters raises ValueError."""
    with pytest.raises(ValueError, match="invalid characters"):
        PaymentServiceRequest(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_15",
            amount=Decimal("10.00"),
            currency=SupportedCurrency.USD,
            idempotency_key="bad key with spaces!",
        )


def test_16_unsupported_provider_rejected() -> None:
    """16. Security Test: Request targeting unsupported provider produces DENIED outcome."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_svc_16"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("50.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_unsupported",
        provider_name="unsupported_gateway",
    )

    svc = PaymentService(provider=_make_mock_provider())
    result = svc.evaluate_payment_request(dec_res, req)

    assert result.outcome == PaymentServiceOutcome.DENIED
    assert "UNSUPPORTED_PAYMENT_PROVIDER" in result.reason_code


def test_17_razorpay_sdk_is_not_imported_by_payment_service() -> None:
    """17. Static Check: PaymentService module does not import razorpay SDK directly."""
    import inspect

    import app.payment.payment_service as ps_module

    source_code = inspect.getsource(ps_module)
    assert "import razorpay" not in source_code
    assert "from razorpay" not in source_code


def test_18_payment_service_does_not_recalculate_risk() -> None:
    """18. Static Check: PaymentService does not call risk scoring engines."""
    import inspect

    import app.payment.payment_service as ps_module

    source_code = inspect.getsource(ps_module)
    assert "RiskScoreCalculator" not in source_code
    assert "RiskThresholdService" not in source_code
    assert "HardSecurityRulesEngine" not in source_code


def test_19_payment_service_cannot_bypass_payment_authorization_gate() -> None:
    """19. Static Check: PaymentService delegates to PaymentAuthorizationGate."""
    mock_gate = MagicMock(spec=PaymentAuthorizationGate)
    mock_gate.authorize_payment.side_effect = AssertionError("Gate called!")

    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_svc_19"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("50.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_gate",
    )

    svc = PaymentService(authorization_gate=mock_gate, provider=_make_mock_provider())
    with pytest.raises(AssertionError, match="Gate called!"):
        svc.evaluate_payment_request(dec_res, req)


def test_20_no_fake_payment_or_order_ids_generated() -> None:
    """20. Security Test: PaymentServiceResult leaves payment_id and order_id as None."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_svc_20"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        idempotency_key="idemp_key_nofake",
    )

    svc = PaymentService(provider=_make_mock_provider())
    result = svc.evaluate_payment_request(dec_res, req)

    assert result.payment_id is None
    assert result.order_id is None


def test_21_create_payment_order_requires_authorization() -> None:
    """21. Authorization Guard: create_payment_order fails without valid decision."""
    svc = PaymentService()
    tenant_id1 = uuid.uuid4()
    tenant_id2 = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_288_21"

    dec_res = _make_decision_result(
        t_id=tenant_id1, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id2,  # Tenant mismatch!
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("50.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_288_21",
    )

    with pytest.raises(PaymentServiceError, match="tenant mismatch"):
        svc.create_payment_order(dec_res, req)


def test_22_provider_credentials_never_appear_in_result() -> None:
    """22. Security Test: Service result contains no credential information."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_svc_22"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("50.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_nocreds",
    )

    svc = PaymentService(provider=_make_mock_provider())
    result = svc.evaluate_payment_request(dec_res, req)

    result_str = str(result.model_dump())
    assert "secret_456" not in result_str
    assert "rzp_test_123" not in result_str


def test_23_provider_credentials_never_appear_in_logs(caplog: pytest.LogCaptureFixture) -> None:
    """23. Security Test: Service logging output never contains provider credentials."""
    secret_val = "SECRET_CRED_45678"
    config = RazorpayConfiguration(
        key_id="rzp_test_999",
        key_secret=SecretStr(secret_val),
        enabled=True,
        environment_mode="test",
    )
    provider = RazorpayProvider(config=config)

    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_svc_23"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("50.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_nologs",
    )

    svc = PaymentService(provider=provider)
    with caplog.at_level(logging.INFO):
        svc.evaluate_payment_request(dec_res, req)

    for record in caplog.records:
        assert secret_val not in record.getMessage()


def test_24_prohibited_overrides_in_payment_request_rejected() -> None:
    """24. Security Test: Prohibited decision forgery keys in context_metadata raise ValueError."""
    with pytest.raises(ValueError, match="Prohibited metadata key"):
        PaymentServiceRequest(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_24",
            amount=Decimal("50.00"),
            currency=SupportedCurrency.USD,
            idempotency_key="idemp_key_override",
            context_metadata={"final_decision": "ALLOW"},
        )


def test_25_invalid_provider_configuration_causes_denied_outcome() -> None:
    """25. Security Test: Invalid provider configuration returns DENIED outcome."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_svc_25"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("50.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_invalidprov",
    )

    disabled_config = RazorpayConfiguration(
        key_id="rzp_test_123",
        key_secret=SecretStr("secret"),
        enabled=False,  # Provider disabled!
    )
    svc = PaymentService(provider=RazorpayProvider(config=disabled_config))
    result = svc.evaluate_payment_request(dec_res, req)

    assert result.outcome == PaymentServiceOutcome.DENIED
    assert "PROVIDER_CREDENTIALS_INVALID" in result.reason_code
