"""Unit & Security Tests for Final Decision Contract & Immutability (Phase 281)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.risk.decisions.decision_engine import FinalRiskDecisionEngine
from app.schemas.risk_engine import (
    FinalRiskDecision,
    FinalRiskDecisionResult,
    RiskEvaluationContext,
    RiskThresholdBand,
)


def _make_context() -> RiskEvaluationContext:
    return RiskEvaluationContext(
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_contract_01",
        prediction_timestamp=datetime.now(UTC),
    )


def test_01_final_decision_result_immutability() -> None:
    """1. Mandatory Security Test: FinalRiskDecisionResult is immutable (frozen=True)."""
    res = FinalRiskDecisionResult(
        evaluation_id=uuid.uuid4(),
        decision_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_01",
        prediction_timestamp=datetime.now(UTC),
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
        source_fingerprints=["fp1"],
        calculation_fingerprint="c" * 64,
        decision_fingerprint="df" * 32,
    )

    with pytest.raises(ValidationError, match="Instance is frozen"):
        res.decision = FinalRiskDecision.BLOCK  # Attempted mutation!


def test_02_deterministic_fingerprint_generation() -> None:
    """2. Test SHA-256 decision fingerprint determinism."""
    engine = FinalRiskDecisionEngine()
    ctx = _make_context()

    fp1 = engine._compute_decision_fingerprint(
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
        source_fingerprints=["s2", "s1"],  # Sorted internally
    )

    fp2 = engine._compute_decision_fingerprint(
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
        source_fingerprints=["s1", "s2"],  # Different input order
    )

    assert fp1 == fp2
    assert len(fp1) == 64
