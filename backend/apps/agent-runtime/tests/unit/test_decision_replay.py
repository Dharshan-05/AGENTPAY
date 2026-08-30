"""Unit & Security Tests for Decision Replay & Deterministic Verification (Phase 284)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from app.risk.integrations.fraudguard_risk import FraudGuardRiskIntegrationService
from app.risk.integrations.policy_risk import PolicyRiskIntegrationService
from app.risk.replay.decision_replay import DecisionReplayEngine, DecisionVerificationService
from app.schemas.fraudguard_api import FraudGuardRiskIntelligenceResponse
from app.schemas.ml_risk import PolicyRiskResult
from app.schemas.risk_engine import (
    DecisionVerificationStatus,
    RiskEvaluationContext,
    RiskSignal,
    RiskThresholdConfiguration,
)


def _make_context(
    t_id: uuid.UUID | None = None,
    a_id: uuid.UUID | None = None,
    tx_id: str = "tx_replay_01",
    ts: datetime | None = None,
) -> RiskEvaluationContext:
    return RiskEvaluationContext(
        tenant_id=t_id or uuid.uuid4(),
        agent_id=a_id or uuid.uuid4(),
        transaction_id=tx_id,
        prediction_timestamp=ts or datetime.now(UTC),
    )


def test_01_identical_replay_produces_verified() -> None:
    """1. Test identical replay yields DecisionVerificationStatus.VERIFIED."""
    ctx = _make_context()
    policy_adapter = PolicyRiskIntegrationService()
    fraud_adapter = FraudGuardRiskIntegrationService()
    replay_engine = DecisionReplayEngine()
    verifier = DecisionVerificationService(replay_engine=replay_engine)

    policy_allow = PolicyRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        policy_risk_score=0.0,
        policy_decision="ALLOW",
        policy_decision_code="PASS",
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        source_fingerprint="s1" * 32,
        result_fingerprint="r1" * 32,
    )

    fraud_low = FraudGuardRiskIntelligenceResponse(
        risk_signal_id=uuid.uuid4(),
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        fraud_probability=0.05,
        transaction_risk_score=5.0,
        risk_level="LOW",
        extracted_factors=[],
        result_fingerprint="r2" * 32,
        evaluated_at=ctx.prediction_timestamp,
    )

    signals: list[RiskSignal] = []
    signals.extend(policy_adapter.integrate_policy_risk(policy_allow, ctx))
    signals.extend(fraud_adapter.integrate_risk_intelligence_response(fraud_low, ctx))

    orig_decision = replay_engine.replay_evaluation(ctx, signals)

    ver_res = verifier.verify_decision(orig_decision, ctx, signals)

    assert ver_res.verification_status == DecisionVerificationStatus.VERIFIED
    assert ver_res.decision_match is True
    assert ver_res.fingerprint_match is True
    assert ver_res.configuration_match is True
    assert ver_res.provenance_match is True
    assert len(ver_res.mismatch_codes) == 0


def test_02_changed_threshold_config_causes_mismatch() -> None:
    """2. Test replay with modified threshold configuration causes MISMATCH."""
    ctx = _make_context()
    policy_adapter = PolicyRiskIntegrationService()
    fraud_adapter = FraudGuardRiskIntegrationService()
    replay_engine = DecisionReplayEngine()
    verifier = DecisionVerificationService(replay_engine=replay_engine)

    policy_allow = PolicyRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        policy_risk_score=0.0,
        policy_decision="ALLOW",
        policy_decision_code="PASS",
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        source_fingerprint="s1" * 32,
        result_fingerprint="r1" * 32,
    )

    fraud_low = FraudGuardRiskIntelligenceResponse(
        risk_signal_id=uuid.uuid4(),
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        fraud_probability=0.05,
        transaction_risk_score=5.0,
        risk_level="LOW",
        extracted_factors=[],
        result_fingerprint="r2" * 32,
        evaluated_at=ctx.prediction_timestamp,
    )

    signals: list[RiskSignal] = []
    signals.extend(policy_adapter.integrate_policy_risk(policy_allow, ctx))
    signals.extend(fraud_adapter.integrate_risk_intelligence_response(fraud_low, ctx))
    orig_decision = replay_engine.replay_evaluation(ctx, signals)

    # Replay with altered threshold config (allow bound = 2.0 instead of default 30.0)
    modified_thresh_config = RiskThresholdConfiguration(
        allow_upper_bound=Decimal("2.0"),
        review_upper_bound=Decimal("10.0"),
        configuration_version="2.0.0",
    )

    ver_res = verifier.verify_decision(
        orig_decision, ctx, signals, threshold_config=modified_thresh_config
    )

    assert ver_res.verification_status == DecisionVerificationStatus.MISMATCH
    assert "CONFIGURATION_HASH_MISMATCH" in ver_res.mismatch_codes


def test_03_tenant_mismatch_during_replay_causes_mismatch() -> None:
    """3. Test replay with cross-tenant context causes MISMATCH."""
    ctx = _make_context()
    policy_adapter = PolicyRiskIntegrationService()
    fraud_adapter = FraudGuardRiskIntegrationService()
    replay_engine = DecisionReplayEngine()
    verifier = DecisionVerificationService(replay_engine=replay_engine)

    policy_allow = PolicyRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        policy_risk_score=0.0,
        policy_decision="ALLOW",
        policy_decision_code="PASS",
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        source_fingerprint="s1" * 32,
        result_fingerprint="r1" * 32,
    )

    fraud_low = FraudGuardRiskIntelligenceResponse(
        risk_signal_id=uuid.uuid4(),
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        fraud_probability=0.05,
        transaction_risk_score=5.0,
        risk_level="LOW",
        extracted_factors=[],
        result_fingerprint="r2" * 32,
        evaluated_at=ctx.prediction_timestamp,
    )

    signals: list[RiskSignal] = []
    signals.extend(policy_adapter.integrate_policy_risk(policy_allow, ctx))
    signals.extend(fraud_adapter.integrate_risk_intelligence_response(fraud_low, ctx))
    orig_decision = replay_engine.replay_evaluation(ctx, signals)

    # Replay under different tenant context
    other_tenant_ctx = _make_context(
        t_id=uuid.uuid4(), a_id=ctx.agent_id, tx_id=ctx.transaction_id, ts=ctx.prediction_timestamp
    )

    ver_res = verifier.verify_decision(orig_decision, other_tenant_ctx, signals)

    assert ver_res.verification_status == DecisionVerificationStatus.INVALID_INPUT
    assert any("REPLAY_EXECUTION_ERROR" in m for m in ver_res.mismatch_codes)
