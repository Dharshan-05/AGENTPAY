"""Unit tests for F1 Score Evaluation (Phase 239)."""

from __future__ import annotations

from app.ml.dataset.training_dataset_builder import TrainingDatasetBuilder
from app.ml.evaluation.evaluation_service import ModelEvaluationService
from app.ml.evaluation.f1_evaluator import F1Evaluator
from app.ml.splitting.dataset_splitter import DatasetSplitter
from app.ml.training.xgboost_trainer import XGBoostTrainer
from app.schemas.ml_evaluation import EvaluationThresholdConfig


def test_01_f1_calculation_and_bounds() -> None:
    """1. Test F1 calculation (2*P*R / (P + R)) and bounds enforcement."""
    evaluator = F1Evaluator()

    # Perfect F1: TP=2, FP=0, FN=0 -> 2(2)/(4 + 0 + 0) = 1.0
    res_perfect = evaluator.evaluate_f1(y_true=[1, 1, 0, 0], y_pred=[1, 1, 0, 0])
    assert res_perfect.f1 == 1.0
    assert res_perfect.true_positives == 2
    assert res_perfect.false_positives == 0
    assert res_perfect.false_negatives == 0

    # Mixed F1: TP=1, FP=1, FN=1 -> 2(1)/(2 + 1 + 1) = 0.5
    res_mixed = evaluator.evaluate_f1(y_true=[1, 1, 0, 0], y_pred=[1, 0, 1, 0])
    assert res_mixed.f1 == 0.5
    assert res_mixed.true_positives == 1
    assert res_mixed.false_positives == 1
    assert res_mixed.false_negatives == 1


def test_02_f1_zero_division_safety() -> None:
    """2. Test zero-division safety when no positive support exists."""
    evaluator = F1Evaluator()

    # No positive support: y_true all 0, y_pred all 0 -> 2TP+FP+FN=0
    res = evaluator.evaluate_f1(
        y_true=[0, 0, 0, 0], y_pred=[0, 0, 0, 0], threshold=0.50, threshold_source="VALIDATION"
    )
    assert res.f1 == 0.0
    assert res.support == 0
    assert res.warning == "NO_POSITIVE_SUPPORT"
    assert "F1 score computed on the held-out test set" in res.explanation


def test_03_mandatory_frozen_f1_threshold_test() -> None:
    """3. Mandatory Test: Verify F1 evaluator uses frozen threshold and cannot tune threshold on test set."""  # noqa: E501
    builder = TrainingDatasetBuilder()
    records = []
    for i in range(25):
        records.append(
            {
                "transaction_id": f"tx_{i}",
                "amount": 25.0 * (i + 1),
                "is_fraud": 1 if i % 4 == 0 else 0,
            }
        )

    dataset = builder.build_training_dataset(records)
    splits = DatasetSplitter().split_dataset(dataset, strategy="TEMPORAL")

    model, t_result = XGBoostTrainer().train(splits)
    eval_service = ModelEvaluationService()

    # Set frozen validation threshold at 0.55
    frozen_cfg = EvaluationThresholdConfig(threshold=0.55, threshold_source="VALIDATION")

    res, manifest = eval_service.evaluate_model(
        model, t_result, splits.test_dataset, threshold_config=frozen_cfg
    )

    assert res.f1_result is not None
    assert res.f1_result.threshold == 0.55
    assert res.f1_result.threshold_source == "VALIDATION"
    assert manifest.f1 == res.f1_result.f1
