"""Unit & Adversarial Security Tests for FraudGuard Inference Engine (Phase 246)."""

from __future__ import annotations

import uuid

import pytest

from app.ml.dataset.training_dataset_builder import TrainingDatasetBuilder
from app.ml.evaluation.evaluation_service import ModelEvaluationService
from app.ml.inference.inference_engine import FraudGuardInferenceEngine
from app.ml.registry.model_registry import ModelRegistry
from app.ml.serialization.model_serializer import ModelSerializer
from app.ml.splitting.dataset_splitter import DatasetSplitter
from app.ml.training.training_config import XGBoostTrainingConfig
from app.ml.training.xgboost_trainer import XGBoostTrainer
from app.schemas.ml_inference import InferenceRequest


def test_01_valid_production_inference_and_determinism() -> None:
    """1. Test valid production inference, result outputs, and deterministic reproducibility."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

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

    engine = FraudGuardInferenceEngine(registry=registry)

    request = InferenceRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_test_001",
        feature_values={"amount": 150.0},
    )

    res1, manifest1 = engine.predict_fraud(request)
    assert res1.status == "SUCCEEDED"
    assert 0.0 <= res1.fraud_probability <= 1.0
    assert res1.model_version == "1.0.0"

    # Deterministic inference check
    res2, manifest2 = engine.predict_fraud(request)
    assert res1.fraud_probability == res2.fraud_probability
    assert res1.request_fingerprint == res2.request_fingerprint
    assert manifest1.result_fingerprint == manifest2.result_fingerprint


def test_02_non_production_model_rejection() -> None:
    """2. Mandatory Test: Rejects inference requests for STAGING, DRAFT, or RETIRED models."""
    tenant_id = uuid.uuid4()
    builder = TrainingDatasetBuilder()
    records = [
        {"transaction_id": "tx1", "feat_a": 10.0, "is_fraud": 0},
        {"transaction_id": "tx2", "feat_a": 20.0, "is_fraud": 1},
        {"transaction_id": "tx3", "feat_a": 30.0, "is_fraud": 0},
        {"transaction_id": "tx4", "feat_a": 40.0, "is_fraud": 1},
    ]

    dataset = builder.build_training_dataset(records)
    splits = DatasetSplitter().split_dataset(dataset, strategy="RANDOM", random_seed=42)
    model, t_res = XGBoostTrainer().train(splits)
    _, eval_manifest = ModelEvaluationService().evaluate_model(model, t_res, splits.test_dataset)
    raw_bytes, art_manifest = ModelSerializer().serialize_model(model, t_res, eval_manifest)

    registry = ModelRegistry()
    registry.register_model(
        tenant_id, "fraudguard_xgboost", "1.0.0", raw_bytes, art_manifest, eval_manifest
    )  # noqa: E501
    registry.promote_to_staging(tenant_id, "fraudguard_xgboost", "1.0.0")

    engine = FraudGuardInferenceEngine(registry=registry)
    request = InferenceRequest(
        tenant_id=tenant_id, transaction_id="tx1", feature_values={"feat_a": 15.0}
    )  # noqa: E501

    # STAGING model inference must fail closed!
    with pytest.raises(ValueError, match="No active PRODUCTION model found"):
        engine.predict_fraud(request)


def test_03_tenant_mismatch_and_checksum_tampering_rejection() -> None:
    """3. Mandatory Test: Rejects cross-tenant inference attempts and tampered artifacts."""
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
    model, t_res = XGBoostTrainer().train(splits)
    _, eval_manifest = ModelEvaluationService().evaluate_model(model, t_res, splits.test_dataset)
    raw_bytes, art_manifest = ModelSerializer().serialize_model(model, t_res, eval_manifest)

    registry = ModelRegistry()
    registry.register_model(
        tenant_a, "fraudguard_xgboost", "1.0.0", raw_bytes, art_manifest, eval_manifest
    )  # noqa: E501
    registry.promote_to_production(tenant_a, "fraudguard_xgboost", "1.0.0")

    engine = FraudGuardInferenceEngine(registry=registry)

    # Tenant B attempting to call Tenant A's production model must fail closed
    request_b = InferenceRequest(
        tenant_id=tenant_b, transaction_id="tx_b", feature_values={"feat_a": 15.0}
    )  # noqa: E501
    with pytest.raises(ValueError, match="No active PRODUCTION model found"):
        engine.predict_fraud(request_b)

    # Tamper with stored artifact bytes in registry
    registry._artifacts[tenant_a][("fraudguard_xgboost", "1.0.0")] = b"tampered_bytes_payload"

    request_a = InferenceRequest(
        tenant_id=tenant_a, transaction_id="tx_a", feature_values={"feat_a": 15.0}
    )  # noqa: E501
    with pytest.raises(ValueError, match="Model artifact checksum verification failed"):
        engine.predict_fraud(request_a)
