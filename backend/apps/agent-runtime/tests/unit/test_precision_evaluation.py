"""Unit tests for Precision Evaluation (Phase 237)."""

from __future__ import annotations

from app.ml.evaluation.precision_evaluator import PrecisionEvaluator


def test_01_precision_calculation_and_bounds() -> None:
    """1. Test Precision calculation (TP / (TP + FP)) and bounds enforcement."""
    evaluator = PrecisionEvaluator()

    # Perfect Precision: TP=2, FP=0 -> 2/2 = 1.0
    res_perfect = evaluator.evaluate_precision(y_true=[1, 1, 0, 0], y_pred=[1, 1, 0, 0])
    assert res_perfect.precision == 1.0
    assert res_perfect.true_positives == 2
    assert res_perfect.false_positives == 0

    # Mixed Precision: TP=1, FP=1 -> 1/2 = 0.5
    res_mixed = evaluator.evaluate_precision(y_true=[1, 0, 0, 0], y_pred=[1, 1, 0, 0])
    assert res_mixed.precision == 0.5
    assert res_mixed.true_positives == 1
    assert res_mixed.false_positives == 1

    # Zero Precision: TP=0, FP=2 -> 0/2 = 0.0
    res_zero = evaluator.evaluate_precision(y_true=[0, 0, 0, 0], y_pred=[1, 1, 0, 0])
    assert res_zero.precision == 0.0
    assert res_zero.true_positives == 0
    assert res_zero.false_positives == 2


def test_02_precision_zero_division_safety() -> None:
    """2. Test zero-division safety when no positive predictions are made."""
    evaluator = PrecisionEvaluator()

    # No positive predictions: y_pred all 0 -> support=0
    res = evaluator.evaluate_precision(y_true=[1, 1, 0, 0], y_pred=[0, 0, 0, 0], threshold=0.50)
    assert res.precision == 0.0
    assert res.support == 0
    assert res.warning == "NO_POSITIVE_PREDICTIONS"
    assert "proportion of predicted fraud transactions" in res.explanation
