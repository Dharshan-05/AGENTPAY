"""Unit tests for PR-AUC Evaluation (Phase 241)."""

from __future__ import annotations

from app.ml.evaluation.pr_auc_evaluator import PrAucEvaluator


def test_01_pr_auc_average_precision_calculation() -> None:
    """1. Test PR-AUC Average Precision calculation from continuous probabilities."""
    evaluator = PrAucEvaluator()

    y_true = [1, 1, 0, 0]
    y_prob = [0.95, 0.85, 0.15, 0.05]

    res = evaluator.evaluate_pr_auc(y_true, y_prob)
    assert res.pr_auc == 1.0
    assert res.metric_definition == "AVERAGE_PRECISION"
    assert res.positive_count == 2
    assert res.warning is None


def test_02_mandatory_no_positive_ground_truth_pr_auc_safety() -> None:
    """2. Mandatory Test: No positive ground truth returns pr_auc=None with warning NO_POSITIVE_GROUND_TRUTH."""  # noqa: E501
    evaluator = PrAucEvaluator()

    res = evaluator.evaluate_pr_auc(y_true=[0, 0, 0, 0], y_prob=[0.1, 0.2, 0.3, 0.4])
    assert res.pr_auc is None
    assert res.warning == "NO_POSITIVE_GROUND_TRUTH"
    assert res.metric_definition == "AVERAGE_PRECISION"


def test_03_empty_dataset_pr_auc_handling() -> None:
    """3. Test PR-AUC handling of empty dataset."""
    evaluator = PrAucEvaluator()
    res = evaluator.evaluate_pr_auc(y_true=[], y_prob=[])
    assert res.pr_auc is None
    assert res.warning == "EMPTY_DATASET"
