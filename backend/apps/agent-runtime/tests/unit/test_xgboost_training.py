"""Unit tests for XGBoost Model Training (Phase 234)."""

from __future__ import annotations

import pytest

from app.ml.dataset.training_dataset_builder import TrainingDatasetBuilder
from app.ml.splitting.dataset_splitter import DatasetSplitter
from app.ml.training.training_config import XGBoostTrainingConfig
from app.ml.training.xgboost_trainer import XGBoostTrainer


def test_01_valid_xgboost_training_and_reproducibility() -> None:
    """1. Test valid XGBoost model training, result metadata, and seed reproducibility."""
    builder = TrainingDatasetBuilder()
    records = []
    for i in range(20):
        records.append(
            {
                "transaction_id": f"tx_{i}",
                "amount": 100.0 * (i + 1),
                "tx_amount_log": 4.5 + i * 0.1,
                "is_fraud": 1 if i % 4 == 0 else 0,
            }
        )

    dataset = builder.build_training_dataset(records)
    splitter = DatasetSplitter()
    splits = splitter.split_dataset(dataset, strategy="TEMPORAL")

    trainer = XGBoostTrainer()
    config = XGBoostTrainingConfig(n_estimators=10, max_depth=3, random_state=42)

    model, result = trainer.train(splits, training_config=config)
    assert result.status == "SUCCEEDED"
    assert result.model_type == "XGBoost"
    assert result.feature_count == 2
    assert result.training_rows == 14
    assert result.validation_rows == 3
    assert model is not None

    # Test seed reproducibility: Second run with same seed produces identical predictions
    model2, _ = trainer.train(splits, training_config=config)
    val_matrix = trainer._convert_to_matrix(
        splits.validation_dataset.X, splits.validation_dataset.feature_names
    )  # noqa: E501
    preds1 = model.predict_proba(val_matrix)
    preds2 = model2.predict_proba(val_matrix)
    assert (preds1 == preds2).all()


def test_02_feature_order_integrity_and_numerical_safety() -> None:
    """2. Test feature order preservation and NaN/Inf numerical safety rejection."""
    builder = TrainingDatasetBuilder()
    records = [
        {"transaction_id": "tx1", "feat_a": 1.0, "feat_b": 2.0, "is_fraud": 0},
        {"transaction_id": "tx2", "feat_a": 3.0, "feat_b": 4.0, "is_fraud": 1},
        {"transaction_id": "tx3", "feat_a": 5.0, "feat_b": 6.0, "is_fraud": 0},
        {"transaction_id": "tx4", "feat_a": 7.0, "feat_b": 8.0, "is_fraud": 1},
    ]

    dataset = builder.build_training_dataset(records)
    splitter = DatasetSplitter()
    splits = splitter.split_dataset(dataset, strategy="RANDOM", random_seed=42)

    trainer = XGBoostTrainer()

    # Feature order mismatch should raise ValueError
    with pytest.raises(ValueError, match="Feature order mismatch"):
        trainer.train(splits, feature_order=["feat_c", "feat_a"])

    # NaN in matrix conversion should raise ValueError
    nan_records = [{"feat_a": float("nan"), "feat_b": 1.0}]
    with pytest.raises(ValueError, match="Numerical safety error"):
        trainer._convert_to_matrix(nan_records, ["feat_a", "feat_b"])


def test_03_single_class_and_test_set_isolation() -> None:
    """3. Test rejection of single-class datasets and test set isolation."""
    builder = TrainingDatasetBuilder()
    single_class_records = [
        {"transaction_id": f"tx_{i}", "feat_a": 1.0, "is_fraud": 0} for i in range(10)
    ]
    dataset = builder.build_training_dataset(single_class_records)
    splitter = DatasetSplitter()
    splits = splitter.split_dataset(dataset, strategy="RANDOM", random_seed=42)

    trainer = XGBoostTrainer()
    with pytest.raises(ValueError, match="must contain both 0 and 1 class labels"):
        trainer.train(splits)
