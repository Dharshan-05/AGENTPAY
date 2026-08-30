"""Unit tests for Recall Evaluation (Phase 238)."""

from __future__ import annotations

from app.ml.evaluation.recall_evaluator import RecallEvaluator


def test_01_recall_calculation_and_bounds() -> None:
    """1. Test Recall calculation (TP / (TP + FN)) and bounds enforcement."""
    evaluator = RecallEvaluator()

    # Perfect Recall: TP=2, FN=0 -> 2/2 = 1.0
    res_perfect = evaluator.evaluate_recall(y_true=[1, 1, 0, 0], y_pred=[1, 1, 0, 0])
    assert res_perfect.recall == 1.0
    assert res_perfect.true_positives == 2
    assert res_perfect.false_negatives == 0

    # Mixed Recall: TP=1, FN=1 -> 1/2 = 0.5
    res_mixed = evaluator.evaluate_recall(y_true=[1, 1, 0, 0], y_pred=[1, 0, 0, 0])
    assert res_mixed.recall == 0.5
    assert res_mixed.true_positives == 1
    assert res_mixed.false_negatives == 1

    # Zero Recall: TP=0, FN=2 -> 0/2 = 0.0
    res_zero = evaluator.evaluate_recall(y_true=[1, 1, 0, 0], y_pred=[0, 0, 0, 0])
    assert res_zero.recall == 0.0
    assert res_zero.true_positives == 0
    assert res_zero.false_negatives == 2


def test_02_recall_zero_division_safety() -> None:
    """2. Test zero-division safety when no ground truth positive fraud samples exist."""
    evaluator = RecallEvaluator()

    # No positive ground truth: y_true all 0 -> support=0
    res = evaluator.evaluate_recall(y_true=[0, 0, 0, 0], y_pred=[1, 1, 0, 0], threshold=0.50)
    assert res.recall == 0.0
    assert res.support == 0
    assert res.warning == "NO_POSITIVE_GROUND_TRUTH"
    assert "proportion of actual fraudulent transactions" in res.explanation
