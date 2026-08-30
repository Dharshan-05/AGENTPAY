"""Unit & Mandatory Security Tests for Risk Threshold Evaluation (Phase 276)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.risk.risk_thresholds import RiskThresholdService
from app.schemas.risk_engine import (
    RiskEvaluationContext,
    RiskScoreCalculationResult,
    RiskScoreUnit,
    RiskThresholdBand,
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


def test_01_low_risk_score_classification() -> None:
    """1. Test LOW risk threshold band classification (score <= 30.0)."""
    ctx = _make_context()
    service = RiskThresholdService()

    calc_res = RiskScoreCalculationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        composite_risk_score=20.0,
        composite_risk_score_decimal=Decimal("20.0"),
        score_unit=RiskScoreUnit.RISK_SCORE,
        included_signal_types=["FRAUDGUARD"],
        excluded_signal_types=[],
        available_signal_types=["FRAUDGUARD"],
        unavailable_signal_types=[],
        applied_weights={"FRAUDGUARD": 2.0},
        total_applied_weight=2.0,
        weight_configuration_version="1.0.0",
        weight_configuration_hash="w" * 64,
        source_fingerprints=["fp_1"],
        policy_precedence="ALLOW",
        calculation_fingerprint="c" * 64,
    )

    eval_res = service.evaluate_thresholds(calc_res, context=ctx)

    assert eval_res.classification == "LOW"
    assert eval_res.matched_threshold_band == RiskThresholdBand.LOW_RISK_BAND
    assert eval_res.risk_score == 20.0
    assert len(eval_res.evaluation_fingerprint) == 64


def test_02_review_band_risk_score_classification() -> None:
    """2. Test REVIEW_BAND risk threshold classification (30.0 < score <= 70.0)."""
    ctx = _make_context()
    service = RiskThresholdService()

    eval_res = service.evaluate_thresholds(Decimal("50.0"), context=ctx)

    assert eval_res.classification == "REVIEW_BAND"
    assert eval_res.matched_threshold_band == RiskThresholdBand.MEDIUM_RISK_BAND


def test_03_high_risk_score_classification() -> None:
    """3. Test HIGH risk threshold classification (score > 70.0)."""
    ctx = _make_context()
    service = RiskThresholdService()

    eval_res = service.evaluate_thresholds(Decimal("85.0"), context=ctx)

    assert eval_res.classification == "HIGH"
    assert eval_res.matched_threshold_band == RiskThresholdBand.HIGH_RISK_BAND


def test_04_invalid_score_bounds_rejection() -> None:
    """4. Mandatory Security Test: Score < 0 or > 100 or NaN fails closed."""
    ctx = _make_context()
    service = RiskThresholdService()

    with pytest.raises(ValueError, match="out of valid range"):
        service.evaluate_thresholds(Decimal("150.0"), context=ctx)

    with pytest.raises(ValueError, match="out of valid range"):
        service.evaluate_thresholds(Decimal("-5.0"), context=ctx)


def test_05_nan_score_rejection() -> None:
    """5. Mandatory Security Test: NaN score fails closed."""
    ctx = _make_context()
    service = RiskThresholdService()

    with pytest.raises(ValueError, match="NaN or Infinity"):
        service.evaluate_thresholds(Decimal("nan"), context=ctx)


def test_06_tenant_mismatch_evaluation_rejection() -> None:
    """6. Mandatory Security Test: Tenant mismatch in calculation result fails closed."""
    ctx = _make_context()
    service = RiskThresholdService()

    other_tenant = uuid.uuid4()
    calc_res = RiskScoreCalculationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=other_tenant,  # Cross-tenant attack!
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        composite_risk_score=20.0,
        composite_risk_score_decimal=Decimal("20.0"),
        score_unit=RiskScoreUnit.RISK_SCORE,
        included_signal_types=[],
        excluded_signal_types=[],
        available_signal_types=[],
        unavailable_signal_types=[],
        applied_weights={},
        total_applied_weight=1.0,
        weight_configuration_version="1.0.0",
        weight_configuration_hash="w" * 64,
        source_fingerprints=[],
        policy_precedence="ALLOW",
        calculation_fingerprint="c" * 64,
    )

    with pytest.raises(ValueError, match="Tenant ID mismatch!"):
        service.evaluate_thresholds(calc_res, context=ctx)


def test_07_deterministic_threshold_evaluation_fingerprint() -> None:
    """7. Test evaluation fingerprint determinism across identical input scores."""
    ctx = _make_context()
    service = RiskThresholdService()

    res1 = service.evaluate_thresholds(Decimal("45.0"), context=ctx)
    res2 = service.evaluate_thresholds(Decimal("45.0"), context=ctx)

    assert res1.evaluation_fingerprint == res2.evaluation_fingerprint


def test_08_phase_boundary_verification() -> None:
    """8. Mandatory Phase Boundary Test: RiskThresholdEvaluationResult MUST NOT contain final authorization decisions."""  # noqa: E501
    ctx = _make_context()
    service = RiskThresholdService()

    res = service.evaluate_thresholds(Decimal("95.0"), context=ctx)

    assert not hasattr(res, "final_decision")
    assert not hasattr(res, "allow_decision")
    assert not hasattr(res, "block_decision")
    assert not hasattr(res, "review_decision")
    assert res.classification != "BLOCK"
    assert res.classification != "ALLOW"
