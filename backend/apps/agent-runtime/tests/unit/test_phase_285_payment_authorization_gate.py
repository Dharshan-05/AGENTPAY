"""Unit & Security Tests for Phase 285 — Payment Authorization Gate."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.payment.authorization.payment_authorization_gate import PaymentAuthorizationGate
from app.schemas.payment_authorization import (
    PaymentAuthorizationOutcome,
    PaymentAuthorizationRequest,
)
from app.schemas.risk_engine import (
    FinalRiskDecision,
    FinalRiskDecisionResult,
    RiskThresholdBand,
)


def _make_decision_result(
    t_id: uuid.UUID | None = None,
    a_id: uuid.UUID | None = None,
    tx_id: str = "tx_pay_auth_01",
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

    # Recompute canonical decision fingerprint if not provided
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


def test_01_allow_decision_maps_to_permitted() -> None:
    """1. Test FinalRiskDecision.ALLOW maps to PaymentAuthorizationOutcome.PERMITTED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_pay_01"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentAuthorizationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        payment_reference="pay_ref_001",
    )

    gate = PaymentAuthorizationGate()
    result = gate.authorize_payment(dec_res, req)

    assert result.outcome == PaymentAuthorizationOutcome.PERMITTED
    assert result.execution_permitted is True
    assert result.execution_suspended is False
    assert result.approval_required is False
    assert result.authorization_denied is False
    assert result.payment_reference == "pay_ref_001"
    assert len(result.authorization_fingerprint) == 64


def test_02_review_decision_maps_to_suspended() -> None:
    """2. Test FinalRiskDecision.REVIEW maps to PaymentAuthorizationOutcome.SUSPENDED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_pay_02"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.REVIEW, score=50.0
    )
    req = PaymentAuthorizationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
    )

    gate = PaymentAuthorizationGate()
    result = gate.authorize_payment(dec_res, req)

    assert result.outcome == PaymentAuthorizationOutcome.SUSPENDED
    assert result.execution_permitted is False
    assert result.execution_suspended is True
    assert result.approval_required is True
    assert result.authorization_denied is False


def test_03_block_decision_maps_to_denied() -> None:
    """3. Test FinalRiskDecision.BLOCK maps to PaymentAuthorizationOutcome.DENIED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_pay_03"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.BLOCK, score=90.0
    )
    req = PaymentAuthorizationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
    )

    gate = PaymentAuthorizationGate()
    result = gate.authorize_payment(dec_res, req)

    assert result.outcome == PaymentAuthorizationOutcome.DENIED
    assert result.execution_permitted is False
    assert result.execution_suspended is False
    assert result.approval_required is False
    assert result.authorization_denied is True


def test_04_tampered_decision_fingerprint_causes_denied() -> None:
    """4. Security Test: Tampered decision fingerprint causes PaymentAuthorizationOutcome.DENIED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_pay_04"

    dec_res = _make_decision_result(
        t_id=tenant_id,
        a_id=agent_id,
        tx_id=tx_id,
        decision=FinalRiskDecision.ALLOW,
        fp="TAMPERED_" + "0" * 55,
    )
    req = PaymentAuthorizationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
    )

    gate = PaymentAuthorizationGate()
    result = gate.authorize_payment(dec_res, req)

    assert result.outcome == PaymentAuthorizationOutcome.DENIED
    assert result.execution_permitted is False
    assert "FINGERPRINT_TAMPERING_DETECTED" in result.reason_code


def test_05_tenant_mismatch_causes_denied() -> None:
    """5. Security Test: Tenant mismatch between decision and request causes DENIED."""
    tenant_id1 = uuid.uuid4()
    tenant_id2 = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_pay_05"

    dec_res = _make_decision_result(
        t_id=tenant_id1, a_id=agent_id, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentAuthorizationRequest(
        tenant_id=tenant_id2,  # Mismatched tenant!
        agent_id=agent_id,
        transaction_id=tx_id,
    )

    gate = PaymentAuthorizationGate()
    result = gate.authorize_payment(dec_res, req)

    assert result.outcome == PaymentAuthorizationOutcome.DENIED
    assert result.execution_permitted is False
    assert "IDENTITY_TENANT_MISMATCH" in result.reason_code


def test_06_agent_mismatch_causes_denied() -> None:
    """6. Security Test: Agent mismatch between decision and request causes DENIED."""
    tenant_id = uuid.uuid4()
    agent_id1 = uuid.uuid4()
    agent_id2 = uuid.uuid4()
    tx_id = "tx_pay_06"

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id1, tx_id=tx_id, decision=FinalRiskDecision.ALLOW
    )
    req = PaymentAuthorizationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id2,  # Mismatched agent!
        transaction_id=tx_id,
    )

    gate = PaymentAuthorizationGate()
    result = gate.authorize_payment(dec_res, req)

    assert result.outcome == PaymentAuthorizationOutcome.DENIED
    assert result.execution_permitted is False
    assert "IDENTITY_AGENT_MISMATCH" in result.reason_code


def test_07_transaction_mismatch_causes_denied() -> None:
    """7. Security Test: Transaction mismatch between decision and request causes DENIED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    dec_res = _make_decision_result(
        t_id=tenant_id, a_id=agent_id, tx_id="tx_orig", decision=FinalRiskDecision.ALLOW
    )
    req = PaymentAuthorizationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_other",  # Mismatched tx!
    )

    gate = PaymentAuthorizationGate()
    result = gate.authorize_payment(dec_res, req)

    assert result.outcome == PaymentAuthorizationOutcome.DENIED
    assert result.execution_permitted is False
    assert "IDENTITY_TRANSACTION_MISMATCH" in result.reason_code


def test_08_stale_decision_causes_denied() -> None:
    """8. Security Test: Decision older than max_decision_age_seconds causes DENIED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_pay_08"
    stale_time = datetime.now(UTC) - timedelta(seconds=400)

    dec_res = _make_decision_result(
        t_id=tenant_id,
        a_id=agent_id,
        tx_id=tx_id,
        decision=FinalRiskDecision.ALLOW,
        created_at=stale_time,
    )
    req = PaymentAuthorizationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
    )

    gate = PaymentAuthorizationGate()
    result = gate.authorize_payment(dec_res, req, max_decision_age_seconds=300.0)

    assert result.outcome == PaymentAuthorizationOutcome.DENIED
    assert result.execution_permitted is False
    assert "STALE_OR_FUTURE_DECISION" in result.reason_code


def test_09_prohibited_overrides_in_request_rejected() -> None:
    """9. Security Test: Request payload with prohibited decision forgery keys raises ValueError."""
    with pytest.raises(ValueError, match="Prohibited metadata key"):
        PaymentAuthorizationRequest(
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_09",
            context_metadata={"final_decision": "ALLOW"},
        )
