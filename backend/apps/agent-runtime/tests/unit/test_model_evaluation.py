"""Unit tests for Model Evaluation Foundation (Phase 236)."""

from __future__ import annotations

import pytest

from app.ml.dataset.training_dataset_builder import TrainingDatasetBuilder
from app.ml.evaluation.evaluation_service import ModelEvaluationService
from app.ml.splitting.dataset_splitter import DatasetSplitter
from app.ml.training.training_config import XGBoostTrainingConfig
from app.ml.training.xgboost_trainer import XGBoostTrainer
from app.schemas.ml_evaluation import EvaluationThresholdConfig


def test_01_valid_model_evaluation_on_test_set() -> None:
    """1. Test valid model evaluation execution on held-out TEST dataset."""
    builder = TrainingDatasetBuilder()
    records = []
    for i in range(30):
        records.append(
            {
                "transaction_id": f"tx_{i}",
                "amount": 50.0 * (i + 1),
                "tx_amount_log": 2.0 + i * 0.1,
                "is_fraud": 1 if i % 3 == 0 else 0,
            }
        )

    dataset = builder.build_training_dataset(records)
    splitter = DatasetSplitter()
    splits = splitter.split_dataset(dataset, strategy="TEMPORAL")

    trainer = XGBoostTrainer()
    config = XGBoostTrainingConfig(n_estimators=10, max_depth=3, random_state=42)
    model, t_result = trainer.train(splits, training_config=config)

    eval_service = ModelEvaluationService()
    thresh_cfg = EvaluationThresholdConfig(threshold=0.50, threshold_source="CONFIGURATION")

    eval_result, manifest = eval_service.evaluate_model(
        model, t_result, splits.test_dataset, threshold_config=thresh_cfg, partition_name="TEST"
    )

    assert eval_result.status == "SUCCEEDED"
    assert eval_result.split_partition == "TEST"
    assert eval_result.precision_result.precision >= 0.0
    assert eval_result.recall_result.recall >= 0.0
    assert manifest.threshold == 0.50


def test_02_mandatory_threshold_leakage_test() -> None:
    """2. Mandatory Threshold Leakage Test: Verify frozen threshold cannot be mutated by test set labels."""  # noqa: E501
    builder = TrainingDatasetBuilder()
    records = []
    for i in range(25):
        records.append(
            {
                "transaction_id": f"tx_{i}",
                "amount": 30.0 * (i + 1),
                "is_fraud": 1 if i % 4 == 0 else 0,
            }
        )

    dataset = builder.build_training_dataset(records)
    splits = DatasetSplitter().split_dataset(dataset, strategy="TEMPORAL")

    model, t_result = XGBoostTrainer().train(splits)
    eval_service = ModelEvaluationService()

    # Freeze threshold at 0.60
    frozen_thresh = EvaluationThresholdConfig(threshold=0.60, threshold_source="VALIDATION")

    res1, man1 = eval_service.evaluate_model(
        model, t_result, splits.test_dataset, threshold_config=frozen_thresh
    )  # noqa: E501

    # Mutate test labels
    splits.test_dataset.y = [1] * len(splits.test_dataset.y)

    res2, man2 = eval_service.evaluate_model(
        model, t_result, splits.test_dataset, threshold_config=frozen_thresh
    )  # noqa: E501

    assert man1.threshold == 0.60
    assert man2.threshold == 0.60
    assert man1.threshold_source == "VALIDATION"


def test_03_mandatory_feature_order_and_dataset_mismatch_tests() -> None:
    """3. Mandatory Feature Order and Dataset Mismatch Tests: Fail closed on contract violation."""  # noqa: E501
    builder = TrainingDatasetBuilder()
    records = [
        {"transaction_id": "tx1", "feat_a": 10.0, "feat_b": 20.0, "is_fraud": 0},
        {"transaction_id": "tx2", "feat_a": 30.0, "feat_b": 40.0, "is_fraud": 1},
        {"transaction_id": "tx3", "feat_a": 50.0, "feat_b": 60.0, "is_fraud": 0},
        {"transaction_id": "tx4", "feat_a": 70.0, "feat_b": 80.0, "is_fraud": 1},
    ]

    dataset = builder.build_training_dataset(records)
    splits = DatasetSplitter().split_dataset(dataset, strategy="RANDOM", random_seed=42)

    model, t_result = XGBoostTrainer().train(splits)
    eval_service = ModelEvaluationService()

    # Mismatched dataset fingerprint should raise ValueError
    bad_ds = builder.build_training_dataset(records)
    bad_ds.manifest.dataset_fingerprint = "corrupted_fingerprint"
    with pytest.raises(ValueError, match="Dataset fingerprint mismatch"):
        eval_service.evaluate_model(model, t_result, bad_ds)

    # Mismatched feature names should raise ValueError
    bad_feature_ds = builder.build_training_dataset(records)
    bad_feature_ds.feature_names = ["feat_b", "feat_a"]  # reversed order
    with pytest.raises(ValueError, match="Feature order/name mismatch"):
        eval_service.evaluate_model(model, t_result, bad_feature_ds)
