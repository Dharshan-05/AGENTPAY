"""Phase 290 Unit & Security Test Suite — Razorpay Checkout Integration."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from pydantic import SecretStr

from app.payment.payment_service import PaymentService, PaymentServiceError
from app.payment.providers.razorpay.config import RazorpayConfiguration
from app.payment.providers.razorpay.credentials import (
    EnvironmentRazorpayCredentialSource,
    RazorpayCredentialResolver,
)
from app.payment.providers.razorpay.provider import RazorpayProvider
from app.schemas.payment import (
    PaymentOrderResult,
    PaymentServiceRequest,
    RazorpayCheckoutConfig,
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
    tx_id: str = "tx_290_01",
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


def _make_mock_resolver(key_id: str = "rzp_public_key_123") -> RazorpayCredentialResolver:
    mock_settings = MagicMock()
    mock_settings.razorpay_key_id = key_id
    mock_settings.razorpay_key_secret = SecretStr("secret_456")
    mock_settings.razorpay_webhook_secret = SecretStr("webhook_789")
    mock_settings.app_env.value = "test"

    source = EnvironmentRazorpayCredentialSource(settings=mock_settings)
    return RazorpayCredentialResolver(source=source)


def _make_enabled_provider() -> RazorpayProvider:
    config = RazorpayConfiguration(
        key_id="rzp_public_key_123",
        key_secret=SecretStr("secret_456"),
        enabled=True,
        environment_mode="test",
    )
    return RazorpayProvider(config=config)


# --- Phase 290 Unit & Security Tests ---


def test_01_valid_order_produces_checkout_ready_configuration() -> None:
    """1. Test valid authorized payment produces CHECKOUT_READY configuration."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_290_01"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("499.00"),
        currency=SupportedCurrency.INR,
        idempotency_key="idemp_key_290_01",
    )

    provider = _make_enabled_provider()
    resolver = _make_mock_resolver()
    svc = PaymentService(provider=provider, credential_resolver=resolver)

    checkout_config = svc.generate_checkout_configuration(dec_res, req)

    assert isinstance(checkout_config, RazorpayCheckoutConfig)
    assert checkout_config.checkout_status == "CHECKOUT_READY"
    assert checkout_config.order_id.startswith("order_rzp_mock_")
    assert checkout_config.amount == Decimal("499.00")
    assert checkout_config.amount_minor_units == 49900
    assert checkout_config.currency == SupportedCurrency.INR
    assert checkout_config.name == "AGENTPAY"


def test_02_key_id_is_present() -> None:
    """2. Test public key_id is present in checkout configuration."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_290_02"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_290_02",
    )

    svc = PaymentService(
        provider=_make_enabled_provider(), credential_resolver=_make_mock_resolver()
    )
    cfg = svc.generate_checkout_configuration(dec_res, req)

    assert cfg.key_id == "rzp_public_key_123"


def test_03_key_secret_is_absent() -> None:
    """3. Security Test: key_secret is NOT a field on RazorpayCheckoutConfig."""
    assert "key_secret" not in RazorpayCheckoutConfig.model_fields


def test_04_webhook_secret_is_absent() -> None:
    """4. Security Test: webhook_secret is NOT a field on RazorpayCheckoutConfig."""
    assert "webhook_secret" not in RazorpayCheckoutConfig.model_fields


def test_05_credentials_are_not_serialized_in_checkout_dump() -> None:
    """5. Security Test: model_dump() of RazorpayCheckoutConfig contains 0 secret fields."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_290_05"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_290_05",
    )

    svc = PaymentService(
        provider=_make_enabled_provider(), credential_resolver=_make_mock_resolver()
    )
    cfg = svc.generate_checkout_configuration(dec_res, req)
    dump_str = str(cfg.model_dump())

    assert "secret_456" not in dump_str
    assert "webhook_789" not in dump_str


def test_06_order_id_is_bound_to_server_created_order() -> None:
    """6. Test checkout configuration is explicitly bound to server-created order."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_290_06"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_290_06",
    )

    svc = PaymentService(
        provider=_make_enabled_provider(), credential_resolver=_make_mock_resolver()
    )
    order_res = svc.create_payment_order(dec_res, req)
    cfg = svc.generate_checkout_configuration(dec_res, req, order_result=order_res)

    assert cfg.order_id == order_res.order_id


def test_07_arbitrary_client_order_id_rejected() -> None:
    """7. Security Test: Passing order_result with mismatched transaction_id is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_290_07"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_290_07",
    )

    # Forged order result with different transaction_id!
    forged_order = PaymentOrderResult(
        order_id="order_forged_999",
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_OTHER_FORGED",  # Mismatch!
        amount=Decimal("100.00"),
        amount_minor_units=10000,
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_forged",
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="fp_forged",
    )

    svc = PaymentService(
        provider=_make_enabled_provider(), credential_resolver=_make_mock_resolver()
    )

    with pytest.raises(PaymentServiceError, match="Order transaction mismatch"):
        svc.generate_checkout_configuration(dec_res, req, order_result=forged_order)


def test_08_tenant_mismatch_rejected() -> None:
    """8. Security Test: Tenant mismatch during checkout generation is rejected."""
    tenant_id1 = uuid.uuid4()
    tenant_id2 = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_290_08"

    dec_res = _make_decision_result(
        t_id=tenant_id1, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id2,  # Tenant mismatch!
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_290_08",
    )

    svc = PaymentService(
        provider=_make_enabled_provider(), credential_resolver=_make_mock_resolver()
    )

    with pytest.raises(PaymentServiceError, match="tenant mismatch"):
        svc.generate_checkout_configuration(dec_res, req)


def test_09_agent_mismatch_rejected() -> None:
    """9. Security Test: Agent mismatch during checkout generation is rejected."""
    tenant_id = uuid.uuid4()
    agent_id1 = uuid.uuid4()
    agent_id2 = uuid.uuid4()
    tx_id = "tx_290_09"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id1, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id2,  # Agent mismatch!
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_290_09",
    )

    svc = PaymentService(
        provider=_make_enabled_provider(), credential_resolver=_make_mock_resolver()
    )

    with pytest.raises(PaymentServiceError, match="agent mismatch"):
        svc.generate_checkout_configuration(dec_res, req)


def test_10_transaction_mismatch_rejected() -> None:
    """10. Security Test: Transaction mismatch during checkout generation is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id="tx_orig", decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_diff",  # Tx mismatch!
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_290_10",
    )

    svc = PaymentService(
        provider=_make_enabled_provider(), credential_resolver=_make_mock_resolver()
    )

    with pytest.raises(PaymentServiceError, match="transaction mismatch"):
        svc.generate_checkout_configuration(dec_res, req)


def test_11_review_cannot_generate_checkout() -> None:
    """11. Security Test: REVIEW decision cannot generate checkout configuration."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_290_11"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.REVIEW, score=50.0
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_290_11",
    )

    svc = PaymentService(
        provider=_make_enabled_provider(), credential_resolver=_make_mock_resolver()
    )

    with pytest.raises(PaymentServiceError, match="SUSPENDED for human approval"):
        svc.generate_checkout_configuration(dec_res, req)


def test_12_block_cannot_generate_checkout() -> None:
    """12. Security Test: BLOCK decision cannot generate checkout configuration."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_290_12"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.BLOCK, score=90.0
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_290_12",
    )

    svc = PaymentService(
        provider=_make_enabled_provider(), credential_resolver=_make_mock_resolver()
    )

    with pytest.raises(PaymentServiceError, match="DENIED by authorization gate"):
        svc.generate_checkout_configuration(dec_res, req)


def test_13_fingerprint_tampering_cannot_generate_checkout() -> None:
    """13. Security Test: Tampered fingerprint cannot generate checkout configuration."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_290_13"

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
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_290_13",
    )

    svc = PaymentService(
        provider=_make_enabled_provider(), credential_resolver=_make_mock_resolver()
    )

    with pytest.raises(PaymentServiceError, match="DENIED by authorization gate"):
        svc.generate_checkout_configuration(dec_res, req)


def test_14_stale_decision_cannot_generate_checkout() -> None:
    """14. Security Test: Stale decision age cannot generate checkout configuration."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_290_14"
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
        idempotency_key="idemp_key_290_14",
    )

    svc = PaymentService(
        provider=_make_enabled_provider(), credential_resolver=_make_mock_resolver()
    )

    with pytest.raises(PaymentServiceError, match="DENIED by authorization gate"):
        svc.generate_checkout_configuration(dec_res, req, max_decision_age_seconds=300.0)


def test_15_future_decision_cannot_generate_checkout() -> None:
    """15. Security Test: Future decision timestamp cannot generate checkout."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_290_15"
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
        idempotency_key="idemp_key_290_15",
    )

    svc = PaymentService(
        provider=_make_enabled_provider(), credential_resolver=_make_mock_resolver()
    )

    with pytest.raises(PaymentServiceError, match="DENIED by authorization gate"):
        svc.generate_checkout_configuration(dec_res, req)


def test_16_checkout_config_contains_no_secrets() -> None:
    """16. Security Test: RazorpayCheckoutConfig string contains 0 secrets."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_290_16"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_290_16",
    )

    svc = PaymentService(
        provider=_make_enabled_provider(), credential_resolver=_make_mock_resolver()
    )
    cfg = svc.generate_checkout_configuration(dec_res, req)

    cfg_str = str(cfg)
    assert "secret_456" not in cfg_str
    assert "webhook_789" not in cfg_str


def test_17_checkout_config_does_not_claim_payment_success() -> None:
    """17. Security Test: checkout_config.payment_success MUST be False."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_290_17"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_290_17",
    )

    svc = PaymentService(
        provider=_make_enabled_provider(), credential_resolver=_make_mock_resolver()
    )
    cfg = svc.generate_checkout_configuration(dec_res, req)

    assert cfg.payment_success is False


def test_18_checkout_config_does_not_claim_verification() -> None:
    """18. Security Test: checkout_config.payment_verified MUST be False."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_290_18"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_290_18",
    )

    svc = PaymentService(
        provider=_make_enabled_provider(), credential_resolver=_make_mock_resolver()
    )
    cfg = svc.generate_checkout_configuration(dec_res, req)

    assert cfg.payment_verified is False


def test_19_no_signature_verification_occurs() -> None:
    """19. Static Check: PaymentService contains 0 signature verification functions."""
    import inspect

    import app.payment.payment_service as ps_mod

    source_code = inspect.getsource(ps_mod)
    assert "verify_signature" not in source_code


def test_20_no_webhook_implementation_is_added() -> None:
    """20. Static Check: PaymentService contains 0 webhook handling functions."""
    import inspect

    import app.payment.payment_service as ps_mod

    source_code = inspect.getsource(ps_mod)
    assert "handle_webhook" not in source_code


def test_21_no_payment_capture_is_added() -> None:
    """21. Static Check: PaymentService contains 0 payment capture functions."""
    import inspect

    import app.payment.payment_service as ps_mod

    source_code = inspect.getsource(ps_mod)
    assert "capture_payment" not in source_code


def test_22_no_status_lifecycle_is_added() -> None:
    """22. Static Check: PaymentService contains 0 payment status machine state modifications."""
    import inspect

    import app.payment.payment_service as ps_mod

    source_code = inspect.getsource(ps_mod)
    assert "payment_status_machine" not in source_code


def test_23_no_arbitrary_callback_url_injection() -> None:
    """23. Security Test: RazorpayCheckoutConfig forbids arbitrary callback injection fields."""
    assert "callback_url" not in RazorpayCheckoutConfig.model_fields
    assert "redirect_url" not in RazorpayCheckoutConfig.model_fields


def test_24_no_arbitrary_script_injection() -> None:
    """24. Security Test: RazorpayCheckoutConfig forbids arbitrary script injection fields."""
    assert "script_url" not in RazorpayCheckoutConfig.model_fields
    assert "eval_js" not in RazorpayCheckoutConfig.model_fields


def test_25_checkout_configuration_is_deterministic() -> None:
    """25. Test checkout configuration output is deterministic for identical inputs."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_290_25"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentServiceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.USD,
        idempotency_key="idemp_key_290_25",
    )

    svc = PaymentService(
        provider=_make_enabled_provider(), credential_resolver=_make_mock_resolver()
    )
    cfg1 = svc.generate_checkout_configuration(dec_res, req)
    cfg2 = svc.generate_checkout_configuration(dec_res, req)

    assert cfg1.key_id == cfg2.key_id
    assert cfg1.amount == cfg2.amount
    assert cfg1.currency == cfg2.currency
    assert cfg1.checkout_status == cfg2.checkout_status
