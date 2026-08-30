"""Unit & Mandatory Adversarial Tests for SHAP Integration Service (Phase 256)."""

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
from app.ml.xai.shap_integration import ShapIntegrationService


def test_01_valid_shap_attribution_and_determinism() -> None:
    """1. Test valid SHAP attribution calculation for production model and deterministic fingerprints."""  # noqa: E501
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

    service = ShapIntegrationService(registry=registry)
    X_mat = np.array([[150.0]], dtype=np.float32)

    res1 = service.calculate_shap_attributions(
        tenant_id=tenant_id,
        model_name="fraudguard_xgboost",
        X_matrix=X_mat,
        feature_names=["amount"],
        prediction_probability=0.35,
        transaction_id="tx_001",
    )

    assert len(res1.shap_values) == 1
    assert res1.feature_names == ["amount"]

    # Deterministic fingerprint check
    res2 = service.calculate_shap_attributions(
        tenant_id=tenant_id,
        model_name="fraudguard_xgboost",
        X_matrix=X_mat,
        feature_names=["amount"],
        prediction_probability=0.35,
        transaction_id="tx_001",
    )
    assert res1.shap_values == res2.shap_values
    assert res1.result_fingerprint == res2.result_fingerprint


def test_02_mandatory_adversarial_target_leakage_rejection() -> None:
    """2. Mandatory Adversarial Test: Prohibited target leakage features (is_fraud, etc.) raise ValueError."""  # noqa: E501
    service = ShapIntegrationService(registry=ModelRegistry())
    tenant_id = uuid.uuid4()
    X_mat = np.array([[150.0, 1.0]], dtype=np.float32)

    with pytest.raises(ValueError, match="Prohibited data leakage feature present in input"):
        service.calculate_shap_attributions(
            tenant_id=tenant_id,
            model_name="fraudguard_xgboost",
            X_matrix=X_mat,
            feature_names=["amount", "is_fraud"],  # Prohibited leakage feature!
            prediction_probability=0.5,
        )


def test_03_mandatory_adversarial_cross_tenant_and_feature_mismatch_rejection() -> None:
    """3. Mandatory Adversarial Test: Cross-tenant SHAP and feature order mismatch fail closed."""
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()

    builder = TrainingDatasetBuilder()
    records = [
        {"transaction_id": "tx1", "feat_a": 10.0, "is_fraud": 0},
        {"transaction_id": "tx2", "feat_a": 20.0, "is_fraud": 1},
        {"transaction_id": "tx3", "feat_a": 30.0, "is_fraud": 0},
        {"transaction_id": "tx4", "feat_a": 40.0, "is_fraud": 1},
    ]

    dataset = builder.build_training_dataset(records)
    splits = DatasetSplitter().split_dataset(dataset, strategy="RANDOM", random_seed=42)
    model, t_res = XGBoostTrainer().train(
        splits, training_config=XGBoostTrainingConfig(n_estimators=10, random_state=42)
    )
    _, eval_manifest = ModelEvaluationService().evaluate_model(model, t_res, splits.test_dataset)
    raw_bytes, art_manifest = ModelSerializer().serialize_model(model, t_res, eval_manifest)

    registry = ModelRegistry()
    registry.register_model(
        tenant_a, "fraudguard_xgboost", "1.0.0", raw_bytes, art_manifest, eval_manifest
    )  # noqa: E501
    registry.promote_to_production(tenant_a, "fraudguard_xgboost", "1.0.0")

    service = ShapIntegrationService(registry=registry)
    X_mat = np.array([[15.0]], dtype=np.float32)

    # Tenant B attempting cross-tenant SHAP lookup fails closed
    with pytest.raises(ValueError, match="No active PRODUCTION model found"):
        service.calculate_shap_attributions(tenant_b, "fraudguard_xgboost", X_mat, ["feat_a"], 0.5)

    # Feature contract mismatch (wrong feature name) fails closed
    with pytest.raises(ValueError, match="Feature contract mismatch!"):
        service.calculate_shap_attributions(
            tenant_a, "fraudguard_xgboost", X_mat, ["feat_wrong"], 0.5
        )  # noqa: E501
