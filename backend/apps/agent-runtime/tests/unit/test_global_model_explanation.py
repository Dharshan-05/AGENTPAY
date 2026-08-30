"""Unit & Mandatory Adversarial Tests for Global Model Explanation Service (Phase 259)."""

from __future__ import annotations

import uuid

import numpy as np
import pytest

from app.ml.dataset.training_dataset_builder import TrainingDatasetBuilder
from app.ml.evaluation.evaluation_service import ModelEvaluationService
from app.ml.registry.model_registry import ModelRegistry
from app.ml.serialization.model_serializer import ModelSerializer
from app.ml.splitting.dataset_splitter import DatasetSplitter
from app.ml.training.training_config import XGBoostTrainingConfig
from app.ml.training.xgboost_trainer import XGBoostTrainer
from app.ml.xai.global_explanation import GlobalModelExplanationService


def test_01_valid_global_model_explanation_and_ranking() -> None:
    """1. Test valid global model explanation over target-free dataset and deterministic feature ranking."""  # noqa: E501
    tenant_id = uuid.uuid4()
    builder = TrainingDatasetBuilder()
    records = []
    for i in range(30):
        records.append(
            {
                "transaction_id": f"tx_{i}",
                "amount": 50.0 * (i + 1),
                "is_fraud": 1 if i % 3 == 0 else 0,
            }
        )

    dataset = builder.build_training_dataset(records)
    splits = DatasetSplitter().split_dataset(dataset, strategy="RANDOM", random_seed=42)
    model, t_res = XGBoostTrainer().train(
        splits, training_config=XGBoostTrainingConfig(n_estimators=10, random_state=42)
    )  # noqa: E501
    _, eval_manifest = ModelEvaluationService().evaluate_model(model, t_res, splits.test_dataset)

    serializer = ModelSerializer()
    raw_bytes, art_manifest = serializer.serialize_model(
        model, t_res, eval_manifest, model_version="1.0.0"
    )  # noqa: E501

    registry = ModelRegistry()
    registry.register_model(
        tenant_id, "fraudguard_xgboost", "1.0.0", raw_bytes, art_manifest, eval_manifest
    )  # noqa: E501
    registry.promote_to_production(tenant_id, "fraudguard_xgboost", "1.0.0")

    service = GlobalModelExplanationService(registry=registry)
    X_mat = np.array([[100.0], [200.0], [300.0]], dtype=np.float32)

    res = service.generate_global_explanation(
        tenant_id=tenant_id,
        model_name="fraudguard_xgboost",
        target_model_version="1.0.0",
        X_matrix=X_mat,
        feature_names=["amount"],
        dataset_fingerprint="dataset_fingerprint_123",
    )

    assert res.model_version == "1.0.0"
    assert res.sample_count == 3
    assert res.feature_count == 1
    assert len(res.feature_importance) == 1
    assert res.feature_importance[0].feature_name == "amount"
    assert "has the highest average contribution to the model's output" in res.explanation_statement  # noqa: E501


def test_02_mandatory_global_poisoning_and_target_leakage_rejection() -> None:
    """2. Mandatory Poison Test: Global explanation rejects target leakage features and ignores target labels."""  # noqa: E501
    registry = ModelRegistry()
    service = GlobalModelExplanationService(registry=registry)
    tenant_id = uuid.uuid4()
    X_mat = np.array([[100.0, 1.0]], dtype=np.float32)

    with pytest.raises(
        ValueError, match="Prohibited data leakage feature present in global dataset"
    ):  # noqa: E501
        service.generate_global_explanation(
            tenant_id=tenant_id,
            model_name="fraudguard_xgboost",
            target_model_version="1.0.0",
            X_matrix=X_mat,
            feature_names=["amount", "is_fraud"],  # Target leakage feature!
            dataset_fingerprint="ds123",
        )
