"""Unit tests for Confusion Matrix Evaluation (Phase 242)."""

from __future__ import annotations

from app.ml.evaluation.confusion_matrix_evaluator import ConfusionMatrixEvaluator


def test_01_confusion_matrix_basic() -> None:
    """1. Test basic confusion matrix calculation (TP, TN, FP, FN, rates)."""
    evaluator = ConfusionMatrixEvaluator()

    # Ground truth: 2 ones, 2 zeros. Prediction: 2 ones, 2 zeros.
    res = evaluator.evaluate_confusion_matrix(y_true=[1, 1, 0, 0], y_pred=[1, 0, 1, 0])
    assert res.true_positives == 1
    assert res.false_negatives == 1
    assert res.false_positives == 1
    assert res.true_negatives == 1
    assert res.total_samples == 4
    assert res.positive_support == 2
    assert res.negative_support == 2
    assert res.true_positive_rate == 0.5
    assert res.true_negative_rate == 0.5
    assert res.false_positive_rate == 0.5
    assert res.false_negative_rate == 0.5


def test_02_confusion_matrix_all_positive_and_all_negative() -> None:
    """2. Test confusion matrix edge cases with all positive or all negative predictions."""
    evaluator = ConfusionMatrixEvaluator()

    # All positive predictions
    res_pos = evaluator.evaluate_confusion_matrix(y_true=[1, 0, 1, 0], y_pred=[1, 1, 1, 1])
    assert res_pos.true_positives == 2
    assert res_pos.false_positives == 2
    assert res_pos.true_negatives == 0
    assert res_pos.false_negatives == 0

    # All negative predictions
    res_neg = evaluator.evaluate_confusion_matrix(y_true=[1, 0, 1, 0], y_pred=[0, 0, 0, 0])
    assert res_neg.true_positives == 0
    assert res_neg.false_positives == 0
    assert res_neg.true_negatives == 2
    assert res_neg.false_negatives == 2
    assert res_neg.warning == "NO_POSITIVE_PREDICTIONS"


def test_03_confusion_matrix_single_class_and_empty_dataset() -> None:
    """3. Test confusion matrix with single class dataset or empty dataset."""
    evaluator = ConfusionMatrixEvaluator()

    # Empty dataset
    res_empty = evaluator.evaluate_confusion_matrix(y_true=[], y_pred=[])
    assert res_empty.total_samples == 0
    assert res_empty.warning == "EMPTY_DATASET"

    # Single class target (all 0s)
    res_zeros = evaluator.evaluate_confusion_matrix(y_true=[0, 0, 0, 0], y_pred=[0, 0, 1, 0])
    assert res_zeros.positive_support == 0
    assert res_zeros.warning == "ZERO_POSITIVE_SUPPORT"
    assert res_zeros.true_positive_rate is None
