"""Unit & Determinism Tests for Risk Engine Architecture (Phase 266)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.risk.risk_engine import RiskEngine
from app.schemas.risk_engine import (
    RiskEngineConfig,
    RiskEvaluationContext,
    RiskScoreUnit,
    RiskSignal,
    RiskSignalType,
)


def _make_context(
    t_id: uuid.UUID | None = None,
    a_id: uuid.UUID | None = None,
    tx_id: str = "tx_001",
    eval_id: uuid.UUID | None = None,
    ts: datetime | None = None,
) -> RiskEvaluationContext:
    return RiskEvaluationContext(
        tenant_id=t_id or uuid.UUID("11111111-1111-1111-1111-111111111111"),
        agent_id=a_id or uuid.UUID("22222222-2222-2222-2222-222222222222"),
        transaction_id=tx_id,
        prediction_timestamp=ts or datetime(2026, 8, 26, 12, 0, 0, tzinfo=UTC),
        evaluation_id=eval_id or uuid.UUID("33333333-3333-3333-3333-333333333333"),
    )


def test_026_deterministic_replay() -> None:
    """TEST 026: Deterministic replay -> Same input twice produces identical result fingerprint."""
    ctx = _make_context()
    engine = RiskEngine()

    sig1 = RiskSignal(
        signal_type=RiskSignalType.FRAUDGUARD,
        source="ml_engine",
        score=0.8,
        score_unit=RiskScoreUnit.PROBABILITY,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    sig2 = RiskSignal(
        signal_type=RiskSignalType.VELOCITY,
        source="velocity_service",
        score=45.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )

    res1 = engine.evaluate(ctx, [sig1, sig2])
    res2 = engine.evaluate(ctx, [sig1, sig2])

    assert res1.result_fingerprint == res2.result_fingerprint
    assert res1.configuration_hash == res2.configuration_hash
    assert len(res1.result_fingerprint) == 64


def test_027_different_signal_different_fingerprint() -> None:
    """TEST 027: Different signal -> produces different fingerprint."""
    ctx = _make_context()
    engine = RiskEngine()

    sig1 = RiskSignal(
        signal_type=RiskSignalType.FRAUDGUARD,
        source="ml_engine",
        score=0.8,
        score_unit=RiskScoreUnit.PROBABILITY,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    sig2_different = RiskSignal(
        signal_type=RiskSignalType.FRAUDGUARD,
        source="ml_engine",
        score=0.2,  # Different score!
        score_unit=RiskScoreUnit.PROBABILITY,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )

    res1 = engine.evaluate(ctx, [sig1])
    res2 = engine.evaluate(ctx, [sig2_different])

    assert res1.result_fingerprint != res2.result_fingerprint


def test_028_configuration_change_different_hash() -> None:
    """TEST 028: Configuration change -> produces different configuration hash."""
    ctx = _make_context()
    cfg1 = RiskEngineConfig(configuration_version="1.0.0")
    cfg2 = RiskEngineConfig(configuration_version="2.0.0")

    engine1 = RiskEngine(config=cfg1)
    engine2 = RiskEngine(config=cfg2)

    sig = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="tx_engine",
        score=30.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )

    res1 = engine1.evaluate(ctx, [sig])
    res2 = engine2.evaluate(ctx, [sig])

    assert res1.configuration_hash != res2.configuration_hash


def test_029_signal_ordering_permutation_same_result() -> None:
    """TEST 029: Signal ordering permutation -> produces same normalized order and fingerprint."""
    ctx = _make_context()
    engine = RiskEngine()

    sig1 = RiskSignal(
        signal_type=RiskSignalType.FRAUDGUARD,
        source="ml_engine",
        score=0.7,
        score_unit=RiskScoreUnit.PROBABILITY,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    sig2 = RiskSignal(
        signal_type=RiskSignalType.AGENTGUARD,
        source="agentguard",
        decision="ALLOW",
        score_unit=RiskScoreUnit.DECISION,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )
    sig3 = RiskSignal(
        signal_type=RiskSignalType.VELOCITY,
        source="velocity_service",
        score=50.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
    )

    res_order_1 = engine.evaluate(ctx, [sig1, sig2, sig3])
    res_order_2 = engine.evaluate(ctx, [sig3, sig1, sig2])

    assert res_order_1.result_fingerprint == res_order_2.result_fingerprint
    assert res_order_1.normalized_signals == res_order_2.normalized_signals


def test_030_missing_identity_rejection() -> None:
    """TEST 030: Missing identity -> REJECT."""
    t_id = uuid.uuid4()
    a_id = uuid.uuid4()
    now = datetime.now(UTC)
    sig = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="tx_engine",
        score=50.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        timestamp=now,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_001",
    )

    engine = RiskEngine()

    # Empty/missing tenant_id in context validation
    with pytest.raises(ValueError, match="missing mandatory identity fields"):
        invalid_ctx = RiskEvaluationContext.model_construct(
            tenant_id=None,
            agent_id=a_id,
            transaction_id="tx_001",
            prediction_timestamp=now,
        )
        engine.evaluate(invalid_ctx, [sig])
