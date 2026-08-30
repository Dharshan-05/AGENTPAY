"""Unit and Adversarial Security Tests for Model Registry (Phase 245)."""

from __future__ import annotations

import uuid

import pytest

from app.ml.dataset.training_dataset_builder import TrainingDatasetBuilder
from app.ml.evaluation.evaluation_service import ModelEvaluationService
from app.ml.registry.model_registry import ModelRegistry
from app.ml.serialization.model_serializer import ModelSerializer
from app.ml.splitting.dataset_splitter import DatasetSplitter
from app.ml.training.training_config import XGBoostTrainingConfig
from app.ml.training.xgboost_trainer import XGBoostTrainer
from app.schemas.ml_registry import QualityGateConfig
from app.schemas.ml_versioning import ModelLifecycleState


def test_01_model_registration_promotion_and_quality_gates() -> None:
    """1. Test model registration, quality gate enforcement, and production promotion."""
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

    trainer = XGBoostTrainer()
    model, t_res = trainer.train(
        splits, training_config=XGBoostTrainingConfig(n_estimators=10, random_state=42)
    )  # noqa: E501

    eval_service = ModelEvaluationService()
    eval_res, eval_manifest = eval_service.evaluate_model(model, t_res, splits.test_dataset)

    serializer = ModelSerializer()
    raw_bytes, art_manifest = serializer.serialize_model(
        model, t_res, eval_manifest, model_version="1.0.0"
    )  # noqa: E501

    registry = ModelRegistry()

    # Register model
    reg_manifest = registry.register_model(
        tenant_id=tenant_id,
        model_name="fraudguard_xgb",
        model_version="1.0.0",
        raw_bytes=raw_bytes,
        artifact_manifest=art_manifest,
        evaluation_manifest=eval_manifest,
    )
    assert reg_manifest.lifecycle_state == ModelLifecycleState.REGISTERED

    # Promote to Staging
    stg_manifest = registry.promote_to_staging(tenant_id, "fraudguard_xgb", "1.0.0")
    assert stg_manifest.lifecycle_state == ModelLifecycleState.STAGING

    # Promote to Production with Quality Gates
    gates = QualityGateConfig(minimum_precision=0.0, minimum_recall=0.0)
    prod_manifest = registry.promote_to_production(
        tenant_id, "fraudguard_xgb", "1.0.0", quality_gates=gates
    )  # noqa: E501
    assert prod_manifest.lifecycle_state == ModelLifecycleState.PRODUCTION

    # Resolve production model
    active_prod = registry.resolve_production_model(tenant_id, "fraudguard_xgb")
    assert active_prod.model_version == "1.0.0"


def test_02_production_uniqueness_and_rollback() -> None:
    """2. Test production model uniqueness constraint and rollback functionality."""
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

    trainer = XGBoostTrainer()
    model, t_res = trainer.train(splits)
    eval_service = ModelEvaluationService()
    _, eval_manifest = eval_service.evaluate_model(model, t_res, splits.test_dataset)

    serializer = ModelSerializer()
    raw_bytes1, art_manifest1 = serializer.serialize_model(
        model, t_res, eval_manifest, model_version="1.0.0"
    )  # noqa: E501
    raw_bytes2, art_manifest2 = serializer.serialize_model(
        model, t_res, eval_manifest, model_version="2.0.0"
    )  # noqa: E501

    registry = ModelRegistry()
    registry.register_model(
        tenant_id, "fraudguard_xgb", "1.0.0", raw_bytes1, art_manifest1, eval_manifest
    )  # noqa: E501
    registry.register_model(
        tenant_id, "fraudguard_xgb", "2.0.0", raw_bytes2, art_manifest2, eval_manifest
    )  # noqa: E501

    registry.promote_to_production(tenant_id, "fraudguard_xgb", "1.0.0")
    assert registry.resolve_production_model(tenant_id, "fraudguard_xgb").model_version == "1.0.0"

    # Promoting v2.0.0 must atomically demote v1.0.0 to DEPRECATED
    registry.promote_to_production(tenant_id, "fraudguard_xgb", "2.0.0")
    assert registry.resolve_production_model(tenant_id, "fraudguard_xgb").model_version == "2.0.0"
    assert (
        registry.get_model(tenant_id, "fraudguard_xgb", "1.0.0").lifecycle_state
        == ModelLifecycleState.DEPRECATED
    )  # noqa: E501

    # Rollback to v1.0.0
    registry.rollback_production_model(tenant_id, "fraudguard_xgb", "1.0.0")
    assert registry.resolve_production_model(tenant_id, "fraudguard_xgb").model_version == "1.0.0"
    assert (
        registry.get_model(tenant_id, "fraudguard_xgb", "2.0.0").lifecycle_state
        == ModelLifecycleState.DEPRECATED
    )  # noqa: E501


def test_03_adversarial_cross_tenant_isolation_test() -> None:
    """3. Adversarial Security Test: Verify Tenant A model CANNOT be accessed or promoted by Tenant B."""  # noqa: E501
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
    _, eval_m = ModelEvaluationService().evaluate_model(model, t_res, splits.test_dataset)
    raw_bytes, art_m = ModelSerializer().serialize_model(model, t_res, eval_m)

    registry = ModelRegistry()
    registry.register_model(tenant_a, "fraudguard_xgb", "1.0.0", raw_bytes, art_m, eval_m)
    registry.promote_to_production(tenant_a, "fraudguard_xgb", "1.0.0")

    # Tenant B attempt to get Tenant A's model must fail closed
    with pytest.raises(ValueError, match="Model 'fraudguard_xgb:v1.0.0' not found for tenant"):
        registry.get_model(tenant_b, "fraudguard_xgb", "1.0.0")

    # Tenant B attempt to resolve production model must fail closed
    with pytest.raises(ValueError, match="No active PRODUCTION model found"):
        registry.resolve_production_model(tenant_b, "fraudguard_xgb")

    # Tenant B attempt to promote Tenant A's model must fail closed
    with pytest.raises(ValueError, match="not found for tenant"):
        registry.promote_to_production(tenant_b, "fraudguard_xgb", "1.0.0")


def test_04_adversarial_quality_gate_failure_test() -> None:
    """4. Adversarial Test: Quality Gate failure MUST reject production promotion."""
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
    _, eval_m = ModelEvaluationService().evaluate_model(model, t_res, splits.test_dataset)
    raw_bytes, art_m = ModelSerializer().serialize_model(model, t_res, eval_m)

    registry = ModelRegistry()
    registry.register_model(tenant_id, "fraudguard_xgb", "1.0.0", raw_bytes, art_m, eval_m)

    # Set impossibly high quality gate minimums
    strict_gates = QualityGateConfig(minimum_precision=0.99, minimum_recall=0.99)
    with pytest.raises(ValueError, match="Quality Gate Failed"):
        registry.promote_to_production(
            tenant_id, "fraudguard_xgb", "1.0.0", quality_gates=strict_gates
        )  # noqa: E501
