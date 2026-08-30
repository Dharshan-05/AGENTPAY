"""Unit & Adversarial Tests for Risk Signal Normalization (Phase 267)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.risk.signal_normalizer import RiskSignalNormalizer
from app.schemas.risk_engine import (
    RiskEvaluationContext,
    RiskScoreUnit,
    RiskSignal,
    RiskSignalType,
)


def _make_context(
    t_id: uuid.UUID | None = None,
    a_id: uuid.UUID | None = None,
    tx_id: str = "tx_001",
    ts: datetime | None = None,
) -> RiskEvaluationContext:
    return RiskEvaluationContext(
        tenant_id=t_id or uuid.uuid4(),
        agent_id=a_id or uuid.uuid4(),
        transaction_id=tx_id,
        prediction_timestamp=ts or datetime.now(UTC),
    )


def test_001_valid_risk_score_0() -> None:
    """TEST 001: Valid risk score 0 -> PASS."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="tx_engine",
        score=0.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    norm = normalizer.normalize_signal(sig, context=ctx)
    assert norm.normalized_score == 0.0


def test_002_valid_risk_score_100() -> None:
    """TEST 002: Valid risk score 100 -> PASS."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="tx_engine",
        score=100.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    norm = normalizer.normalize_signal(sig, context=ctx)
    assert norm.normalized_score == 100.0


def test_003_risk_score_above_100_reject() -> None:
    """TEST 003: Risk score > 100 -> REJECT."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="tx_engine",
        score=105.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    with pytest.raises(ValueError, match="Risk score 105.0 out of valid range"):
        normalizer.normalize_signal(sig, context=ctx)


def test_004_risk_score_below_0_reject() -> None:
    """TEST 004: Risk score < 0 -> REJECT."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="tx_engine",
        score=-5.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    with pytest.raises(ValueError, match="Risk score -5.0 out of valid range"):
        normalizer.normalize_signal(sig, context=ctx)


def test_005_probability_0() -> None:
    """TEST 005: Probability 0 -> PASS (normalized_score = 0.0)."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.FRAUDGUARD,
        source="ml_engine",
        score=0.0,
        score_unit=RiskScoreUnit.PROBABILITY,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    norm = normalizer.normalize_signal(sig, context=ctx)
    assert norm.score == 0.0
    assert norm.normalized_score == 0.0


def test_006_probability_1() -> None:
    """TEST 006: Probability 1 -> PASS (normalized_score = 100.0)."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.FRAUDGUARD,
        source="ml_engine",
        score=1.0,
        score_unit=RiskScoreUnit.PROBABILITY,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    norm = normalizer.normalize_signal(sig, context=ctx)
    assert norm.score == 1.0
    assert norm.normalized_score == 100.0


def test_007_probability_above_1_reject() -> None:
    """TEST 007: Probability > 1 -> REJECT."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.FRAUDGUARD,
        source="ml_engine",
        score=1.2,
        score_unit=RiskScoreUnit.PROBABILITY,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    with pytest.raises(ValueError, match="Probability score 1.2 out of valid range"):
        normalizer.normalize_signal(sig, context=ctx)


def test_008_probability_below_0_reject() -> None:
    """TEST 008: Probability < 0 -> REJECT."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.FRAUDGUARD,
        source="ml_engine",
        score=-0.1,
        score_unit=RiskScoreUnit.PROBABILITY,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    with pytest.raises(ValueError, match="Probability score -0.1 out of valid range"):
        normalizer.normalize_signal(sig, context=ctx)


def test_009_nan_rejection() -> None:
    """TEST 009: NaN -> REJECT."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="tx_engine",
        score=float("nan"),
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    with pytest.raises(ValueError, match="NaN or Infinity value detected"):
        normalizer.normalize_signal(sig, context=ctx)


def test_010_infinity_rejection() -> None:
    """TEST 010: Infinity -> REJECT."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="tx_engine",
        score=float("inf"),
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    with pytest.raises(ValueError, match="NaN or Infinity value detected"):
        normalizer.normalize_signal(sig, context=ctx)


def test_011_confidence_0() -> None:
    """TEST 011: Confidence 0 -> PASS."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.BEHAVIOUR,
        source="beh_engine",
        confidence=0.0,
        score_unit=RiskScoreUnit.CONFIDENCE,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    norm = normalizer.normalize_signal(sig, context=ctx)
    assert norm.confidence == 0.0
    assert norm.normalized_score is None


def test_012_confidence_1() -> None:
    """TEST 012: Confidence 1 -> PASS."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.BEHAVIOUR,
        source="beh_engine",
        confidence=1.0,
        score_unit=RiskScoreUnit.CONFIDENCE,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    norm = normalizer.normalize_signal(sig, context=ctx)
    assert norm.confidence == 1.0
    assert norm.normalized_score is None


def test_013_confidence_above_1_reject() -> None:
    """TEST 013: Confidence > 1 -> REJECT."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    with pytest.raises(ValueError):
        sig = RiskSignal(
            signal_type=RiskSignalType.BEHAVIOUR,
            source="beh_engine",
            confidence=1.5,
            score_unit=RiskScoreUnit.CONFIDENCE,
            timestamp=ctx.prediction_timestamp,
            tenant_id=ctx.tenant_id,
            agent_id=ctx.agent_id,
            transaction_id=ctx.transaction_id,
        )
        normalizer.normalize_signal(sig, context=ctx)


def test_014_confidence_not_treated_as_risk() -> None:
    """TEST 014: Confidence incorrectly treated as risk -> REJECT (normalized_score must be None!)."""  # noqa: E501
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.BEHAVIOUR,
        source="beh_engine",
        confidence=0.95,
        score_unit=RiskScoreUnit.CONFIDENCE,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    norm = normalizer.normalize_signal(sig, context=ctx)
    assert norm.confidence == 0.95
    assert norm.normalized_score is None  # Invariant: Confidence is NOT converted to risk score!


def test_015_cross_tenant_signal_reject() -> None:
    """TEST 015: Cross-tenant signal -> REJECT."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="tx_engine",
        score=50.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ctx.prediction_timestamp,
        tenant_id=uuid.uuid4(),  # Different tenant!
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    with pytest.raises(ValueError, match="Tenant ID mismatch!"):
        normalizer.normalize_signal(sig, context=ctx)


def test_016_cross_agent_signal_reject() -> None:
    """TEST 016: Cross-agent signal -> REJECT."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="tx_engine",
        score=50.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=uuid.uuid4(),  # Different agent!
        transaction_id=ctx.transaction_id,
    )
    with pytest.raises(ValueError, match="Agent ID mismatch!"):
        normalizer.normalize_signal(sig, context=ctx)


def test_017_cross_transaction_signal_reject() -> None:
    """TEST 017: Cross-transaction signal -> REJECT."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="tx_engine",
        score=50.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id="other_tx_999",  # Different tx!
    )
    with pytest.raises(ValueError, match="Transaction ID mismatch!"):
        normalizer.normalize_signal(sig, context=ctx)


def test_018_future_timestamp_reject() -> None:
    """TEST 018: Future timestamp -> REJECT."""
    now = datetime.now(UTC)
    ctx = _make_context(ts=now)
    future_ts = datetime(2030, 1, 1, tzinfo=UTC)
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="tx_engine",
        score=50.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=future_ts,  # Future timestamp!
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    with pytest.raises(ValueError, match="Signal timestamp .* is in the future"):
        normalizer.normalize_signal(sig, context=ctx)


def test_019_cold_start_signal_preserved() -> None:
    """TEST 019: Cold-start signal -> cold_start preserved."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.BEHAVIOUR,
        source="beh_engine",
        score=50.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        cold_start=True,
    )
    norm = normalizer.normalize_signal(sig, context=ctx)
    assert norm.cold_start is True


def test_020_unavailable_signal_preserved() -> None:
    """TEST 020: Unavailable signal -> availability preserved, no fake zero-risk value."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.MERCHANT,
        source="merchant_service",
        score=None,
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        availability=False,
    )
    norm = normalizer.normalize_signal(sig, context=ctx)
    assert norm.availability is False
    assert norm.normalized_score is None  # No manufactured zero!


def test_021_duplicate_identical_signal_deduplicated() -> None:
    """TEST 021: Duplicate identical signal -> deterministic deduplication."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    ts = ctx.prediction_timestamp
    sig1 = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="tx_engine",
        score=40.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ts,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    sig2 = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="tx_engine",
        score=40.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ts,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    res = normalizer.normalize_signals([sig1, sig2], context=ctx)
    assert len(res) == 1


def test_022_conflicting_duplicate_signal_reject() -> None:
    """TEST 022: Conflicting duplicate signal -> REJECT."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    ts = ctx.prediction_timestamp
    sig1 = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="tx_engine",
        score=40.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ts,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    sig2 = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="tx_engine",
        score=90.0,  # Conflicting score!
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ts,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    with pytest.raises(ValueError, match="Conflicting duplicate signal detected"):
        normalizer.normalize_signals([sig1, sig2], context=ctx)


def test_023_target_leakage_field_reject() -> None:
    """TEST 023: Target leakage field in metadata -> REJECT."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="tx_engine",
        score=50.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        metadata={"is_fraud": 1},  # Prohibited data leakage field!
    )
    with pytest.raises(ValueError, match="Prohibited target leakage field"):
        normalizer.normalize_signal(sig, context=ctx)


def test_024_decision_signal_preserved() -> None:
    """TEST 024: Decision signal -> categorical semantics preserved."""
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.POLICY,
        source="policy_engine",
        decision="REVIEW",
        score_unit=RiskScoreUnit.DECISION,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    norm = normalizer.normalize_signal(sig, context=ctx)
    assert norm.decision == "REVIEW"
    assert norm.normalized_score is None


def test_025_agentguard_deny_signal_preserved() -> None:
    """TEST 025: AGENTGUARD DENY-shaped signal -> preserved as categorical/authoritative metadata only."""  # noqa: E501
    ctx = _make_context()
    normalizer = RiskSignalNormalizer()
    sig = RiskSignal(
        signal_type=RiskSignalType.AGENTGUARD,
        source="agentguard_engine",
        decision="DENY",
        score_unit=RiskScoreUnit.DECISION,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        metadata={"violation_code": "POLICY_LIMIT_EXCEEDED"},
    )
    norm = normalizer.normalize_signal(sig, context=ctx)
    assert norm.signal_type == RiskSignalType.AGENTGUARD
    assert norm.decision == "DENY"
    assert norm.normalized_score is None
    assert norm.metadata["violation_code"] == "POLICY_LIMIT_EXCEEDED"
