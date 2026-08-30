"""Unit tests for Model Serialization & Cryptographic Checksum Integrity (Phase 243)."""

from __future__ import annotations

import numpy as np
import pytest

from app.ml.dataset.training_dataset_builder import TrainingDatasetBuilder
from app.ml.serialization.model_serializer import ModelSerializer
from app.ml.splitting.dataset_splitter import DatasetSplitter
from app.ml.training.training_config import XGBoostTrainingConfig
from app.ml.training.xgboost_trainer import XGBoostTrainer


def test_01_model_serialization_round_trip_and_predict_equivalence() -> None:
    """1. Test model serialization, SHA-256 checksum verification, deserialization, and prediction equivalence."""  # noqa: E501
    builder = TrainingDatasetBuilder()
    records = []
    for i in range(30):
        records.append(
            {
                "transaction_id": f"tx_{i}",
                "amount": 40.0 * (i + 1),
                "is_fraud": 1 if i % 3 == 0 else 0,
            }
        )

    dataset = builder.build_training_dataset(records)
    splits = DatasetSplitter().split_dataset(dataset, strategy="RANDOM", random_seed=42)

    trainer = XGBoostTrainer()
    model, t_res = trainer.train(
        splits, training_config=XGBoostTrainingConfig(n_estimators=10, random_state=42)
    )  # noqa: E501

    serializer = ModelSerializer()
    raw_bytes, manifest = serializer.serialize_model(model, t_res, model_version="1.0.0")

    assert len(raw_bytes) > 0
    assert manifest.checksum is not None
    assert serializer.verify_checksum(raw_bytes, manifest) is True

    # Deserialize model back
    loaded_model = serializer.deserialize_model(raw_bytes, manifest)

    # Convert test matrix and verify prediction equivalence within 1e-5 tolerance
    val_matrix = trainer._convert_to_matrix(
        splits.validation_dataset.X, splits.validation_dataset.feature_names
    )  # noqa: E501
    preds_orig = model.predict_proba(val_matrix)
    preds_loaded = loaded_model.predict_proba(val_matrix)

    assert np.allclose(preds_orig, preds_loaded, atol=1e-5)


def test_02_tampered_and_corrupt_artifact_rejection() -> None:
    """2. Test that tampered or corrupted artifact bytes fail closed during deserialization."""
    builder = TrainingDatasetBuilder()
    records = [
        {"transaction_id": "tx1", "feat_a": 1.0, "is_fraud": 0},
        {"transaction_id": "tx2", "feat_a": 2.0, "is_fraud": 1},
        {"transaction_id": "tx3", "feat_a": 3.0, "is_fraud": 0},
        {"transaction_id": "tx4", "feat_a": 4.0, "is_fraud": 1},
    ]

    dataset = builder.build_training_dataset(records)
    splits = DatasetSplitter().split_dataset(dataset, strategy="RANDOM", random_seed=42)

    model, t_res = XGBoostTrainer().train(splits)
    serializer = ModelSerializer()
    raw_bytes, manifest = serializer.serialize_model(model, t_res)

    # Tamper with byte payload
    raw_tampered = bytearray(raw_bytes)
    raw_tampered[0] = (raw_tampered[0] + 1) % 256
    tampered_bytes = bytes(raw_tampered)

    assert serializer.verify_checksum(tampered_bytes, manifest) is False

    with pytest.raises(ValueError, match="Checksum mismatch! Tampered or corrupted artifact"):
        serializer.deserialize_model(tampered_bytes, manifest)
