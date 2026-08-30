"""Unit & Security Tests for Decision Enforcement Gate (Phase 285)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.risk.decisions.decision_engine import FinalRiskDecisionEngine
from app.risk.decisions.enforcement_gate import DecisionEnforcementGate
from app.schemas.risk_engine import (
    EnforcementOutcome,
    FinalRiskDecision,
    FinalRiskDecisionResult,
    RiskEvaluationContext,
    RiskThresholdBand,
)


def _make_context(
    t_id: uuid.UUID | None = None,
    a_id: uuid.UUID | None = None,
    tx_id: str = "tx_enf_01",
    ts: datetime | None = None,
) -> RiskEvaluationContext:
    return RiskEvaluationContext(
        tenant_id=t_id or uuid.uuid4(),
        agent_id=a_id or uuid.uuid4(),
        transaction_id=tx_id,
        prediction_timestamp=ts or datetime.now(UTC),
    )


def test_01_valid_allow_decision_permits_execution() -> None:
    """1. Test valid ALLOW decision permits execution (EnforcementOutcome.PERMITTED)."""
    gate = DecisionEnforcementGate()
    ctx = _make_context()
    engine = FinalRiskDecisionEngine()

    dec_fp = engine._compute_decision_fingerprint(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        decision="ALLOW",
        decision_reason="LOW_RISK_ALLOW_CLEAN",
        composite_risk_score=10.0,
        risk_band="LOW_RISK_BAND",
        policy_precedence="ALLOW",
        calculation_fingerprint="c" * 64,
        source_fingerprints=["s1"],
    )

    dec_res = FinalRiskDecisionResult(
        evaluation_id=ctx.evaluation_id,
        decision_id=uuid.uuid4(),
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        decision=FinalRiskDecision.ALLOW,
        decision_reason="LOW_RISK_ALLOW_CLEAN",
        composite_risk_score=10.0,
        risk_band=RiskThresholdBand.LOW_RISK_BAND,
        policy_precedence="ALLOW",
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
        source_fingerprints=["s1"],
        calculation_fingerprint="c" * 64,
        decision_fingerprint=dec_fp,
        created_at=datetime.now(UTC),
    )

    res = gate.enforce_decision(dec_res, ctx)

    assert res.enforcement_outcome == EnforcementOutcome.PERMITTED
    assert res.execution_permitted is True
    assert res.execution_suspended is False
    assert res.authorization_denied is False


def test_02_review_decision_suspends_execution() -> None:
    """2. Test REVIEW decision suspends execution (EnforcementOutcome.SUSPENDED)."""
    gate = DecisionEnforcementGate()
    ctx = _make_context()
    engine = FinalRiskDecisionEngine()

    dec_fp = engine._compute_decision_fingerprint(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        decision="REVIEW",
        decision_reason="MEDIUM_RISK_BAND_REVIEW",
        composite_risk_score=50.0,
        risk_band="MEDIUM_RISK_BAND",
        policy_precedence="ALLOW",
        calculation_fingerprint="c" * 64,
        source_fingerprints=["s1"],
    )

    dec_res = FinalRiskDecisionResult(
        evaluation_id=ctx.evaluation_id,
        decision_id=uuid.uuid4(),
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        decision=FinalRiskDecision.REVIEW,
        decision_reason="MEDIUM_RISK_BAND_REVIEW",
        composite_risk_score=50.0,
        risk_band=RiskThresholdBand.MEDIUM_RISK_BAND,
        policy_precedence="ALLOW",
        hard_security_status="PASSED",
        triggered_rule_ids=[],
        review_reasons=["MEDIUM_RISK_BAND_REVIEW"],
        block_reasons=[],
        available_signal_types=["FRAUDGUARD"],
        unavailable_signal_types=[],
        cold_start=False,
        policy_authoritative=True,
        threshold_configuration_version="1.0.0",
        threshold_configuration_hash="t" * 64,
        weight_configuration_version="1.0.0",
        weight_configuration_hash="w" * 64,
        source_fingerprints=["s1"],
        calculation_fingerprint="c" * 64,
        decision_fingerprint=dec_fp,
        created_at=datetime.now(UTC),
    )

    res = gate.enforce_decision(dec_res, ctx)

    assert res.enforcement_outcome == EnforcementOutcome.SUSPENDED
    assert res.execution_permitted is False
    assert res.execution_suspended is True
    assert res.approval_required is True


def test_03_block_decision_denies_execution() -> None:
    """3. Test BLOCK decision denies execution (EnforcementOutcome.DENIED)."""
    gate = DecisionEnforcementGate()
    ctx = _make_context()
    engine = FinalRiskDecisionEngine()

    dec_fp = engine._compute_decision_fingerprint(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        decision="BLOCK",
        decision_reason="POLICY_DENY_BLOCK",
        composite_risk_score=90.0,
        risk_band="HIGH_RISK_BAND",
        policy_precedence="DENY",
        calculation_fingerprint="c" * 64,
        source_fingerprints=["s1"],
    )

    dec_res = FinalRiskDecisionResult(
        evaluation_id=ctx.evaluation_id,
        decision_id=uuid.uuid4(),
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        decision=FinalRiskDecision.BLOCK,
        decision_reason="POLICY_DENY_BLOCK",
        composite_risk_score=90.0,
        risk_band=RiskThresholdBand.HIGH_RISK_BAND,
        policy_precedence="DENY",
        hard_security_status="TRIGGERED_CRITICAL",
        triggered_rule_ids=["HSR-001"],
        review_reasons=[],
        block_reasons=["POLICY_DENY_BLOCK"],
        available_signal_types=["FRAUDGUARD"],
        unavailable_signal_types=[],
        cold_start=False,
        policy_authoritative=True,
        threshold_configuration_version="1.0.0",
        threshold_configuration_hash="t" * 64,
        weight_configuration_version="1.0.0",
        weight_configuration_hash="w" * 64,
        source_fingerprints=["s1"],
        calculation_fingerprint="c" * 64,
        decision_fingerprint=dec_fp,
        created_at=datetime.now(UTC),
    )

    res = gate.enforce_decision(dec_res, ctx)

    assert res.enforcement_outcome == EnforcementOutcome.DENIED
    assert res.execution_permitted is False
    assert res.authorization_denied is True


def test_04_fingerprint_tampering_fails_closed() -> None:
    """4. Mandatory Security Test: Tampered decision fingerprint causes EnforcementOutcome.DENIED."""  # noqa: E501
    gate = DecisionEnforcementGate()
    ctx = _make_context()

    dec_res = FinalRiskDecisionResult(
        evaluation_id=ctx.evaluation_id,
        decision_id=uuid.uuid4(),
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        decision=FinalRiskDecision.ALLOW,
        decision_reason="LOW_RISK_ALLOW_CLEAN",
        composite_risk_score=10.0,
        risk_band=RiskThresholdBand.LOW_RISK_BAND,
        policy_precedence="ALLOW",
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
        source_fingerprints=["s1"],
        calculation_fingerprint="c" * 64,
        decision_fingerprint="TAMPERED_FINGERPRINT_" + "0" * 44,  # Tampered!
        created_at=datetime.now(UTC),
    )

    res = gate.enforce_decision(dec_res, ctx)

    assert res.enforcement_outcome == EnforcementOutcome.DENIED
    assert res.execution_permitted is False
    assert "FINGERPRINT_TAMPERING_DETECTED" in res.reason_code


def test_05_tenant_mismatch_fails_closed() -> None:
    """5. Mandatory Security Test: Tenant mismatch in context causes EnforcementOutcome.DENIED."""  # noqa: E501
    gate = DecisionEnforcementGate()
    ctx = _make_context()
    other_tenant_ctx = _make_context(t_id=uuid.uuid4(), a_id=ctx.agent_id, tx_id=ctx.transaction_id)
    engine = FinalRiskDecisionEngine()

    dec_fp = engine._compute_decision_fingerprint(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        decision="ALLOW",
        decision_reason="LOW_RISK_ALLOW_CLEAN",
        composite_risk_score=10.0,
        risk_band="LOW_RISK_BAND",
        policy_precedence="ALLOW",
        calculation_fingerprint="c" * 64,
        source_fingerprints=["s1"],
    )

    dec_res = FinalRiskDecisionResult(
        evaluation_id=ctx.evaluation_id,
        decision_id=uuid.uuid4(),
        tenant_id=ctx.tenant_id,  # Tenant A
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        decision=FinalRiskDecision.ALLOW,
        decision_reason="LOW_RISK_ALLOW_CLEAN",
        composite_risk_score=10.0,
        risk_band=RiskThresholdBand.LOW_RISK_BAND,
        policy_precedence="ALLOW",
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
        source_fingerprints=["s1"],
        calculation_fingerprint="c" * 64,
        decision_fingerprint=dec_fp,
        created_at=datetime.now(UTC),
    )

    res = gate.enforce_decision(dec_res, other_tenant_ctx)  # Tenant B context!

    assert res.enforcement_outcome == EnforcementOutcome.DENIED
    assert res.execution_permitted is False
    assert "IDENTITY_TENANT_MISMATCH" in res.reason_code
