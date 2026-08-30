"""Unit & Adversarial Tests for FraudGuard Inference API (Phase 263)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.application.services.fraudguard_service import FraudGuardApplicationService
from app.ml.dataset.training_dataset_builder import TrainingDatasetBuilder
from app.ml.evaluation.evaluation_service import ModelEvaluationService
from app.ml.registry.model_registry import ModelRegistry
from app.ml.serialization.model_serializer import ModelSerializer
from app.ml.splitting.dataset_splitter import DatasetSplitter
from app.ml.training.training_config import XGBoostTrainingConfig
from app.ml.training.xgboost_trainer import XGBoostTrainer
from app.schemas.fraudguard_api import FraudGuardInferenceRequest


def test_01_valid_fraudguard_inference_api_orchestration() -> None:
    """1. Test valid real-time FraudGuard inference API orchestration."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    now = datetime.now(UTC)

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

    service = FraudGuardApplicationService(registry=registry)

    req = FraudGuardInferenceRequest(
        agent_id=agent_id,
        transaction_id="tx_api_001",
        model_name="fraudguard_xgboost",
        prediction_timestamp=now,
        feature_names=["amount"],
        feature_values=[150.0],
    )

    res = service.run_inference(tenant_id, req)

    assert res.transaction_id == "tx_api_001"
    assert res.model_name == "fraudguard_xgboost"
    assert res.model_version == "1.0.0"
    assert 0.0 <= res.fraud_probability <= 1.0
    assert len(res.result_fingerprint) == 64


def test_02_mandatory_adversarial_cross_tenant_inference_rejection() -> None:
    """2. Mandatory Adversarial Test: Cross-tenant inference fails closed."""
    _tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    now = datetime.now(UTC)

    service = FraudGuardApplicationService(registry=ModelRegistry())

    req = FraudGuardInferenceRequest(
        agent_id=uuid.uuid4(),
        transaction_id="tx_cross",
        model_name="fraudguard_xgboost",
        prediction_timestamp=now,
        feature_names=["amount"],
        feature_values=[100.0],
    )

    # Tenant B attempting inference on non-existent Tenant B production model fails closed
    with pytest.raises(ValueError, match="No active PRODUCTION model found"):
        service.run_inference(tenant_b, req)
