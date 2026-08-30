"""Unit tests for ROC-AUC Evaluation (Phase 240)."""

from __future__ import annotations

from app.ml.evaluation.roc_auc_evaluator import RocAucEvaluator


def test_01_roc_auc_probability_calculation() -> None:
    """1. Test ROC-AUC calculation from continuous prediction probabilities."""
    evaluator = RocAucEvaluator()

    y_true = [1, 1, 0, 0]
    y_prob = [0.90, 0.80, 0.20, 0.10]

    res = evaluator.evaluate_roc_auc(y_true, y_prob)
    assert res.roc_auc == 1.0
    assert res.positive_count == 2
    assert res.negative_count == 2
    assert res.warning is None


def test_02_mandatory_single_class_roc_auc_safety() -> None:
    """2. Mandatory Test: Single-class dataset must return roc_auc=None with warning SINGLE_CLASS_TARGET."""  # noqa: E501
    evaluator = RocAucEvaluator()

    # All zeros
    res_zeros = evaluator.evaluate_roc_auc(y_true=[0, 0, 0, 0], y_prob=[0.1, 0.2, 0.3, 0.4])
    assert res_zeros.roc_auc is None
    assert res_zeros.warning == "SINGLE_CLASS_TARGET"

    # All ones
    res_ones = evaluator.evaluate_roc_auc(y_true=[1, 1, 1, 1], y_prob=[0.6, 0.7, 0.8, 0.9])
    assert res_ones.roc_auc is None
    assert res_ones.warning == "SINGLE_CLASS_TARGET"


def test_03_empty_dataset_handling() -> None:
    """3. Test ROC-AUC handling of empty dataset."""
    evaluator = RocAucEvaluator()
    res = evaluator.evaluate_roc_auc(y_true=[], y_prob=[])
    assert res.roc_auc is None
    assert res.warning == "EMPTY_DATASET"
