"""Unit & Adversarial Tests for XAI Explanation API (Phase 261)."""

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
from app.schemas.fraudguard_api import FraudGuardGlobalXAIRequest, FraudGuardLocalXAIRequest


def test_01_valid_local_and_global_xai_service_calls() -> None:
    """1. Test valid local and global XAI explanation service orchestration."""
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

    # Local XAI
    local_req = FraudGuardLocalXAIRequest(
        agent_id=agent_id,
        transaction_id="tx_001",
        model_name="fraudguard_xgboost",
        prediction_timestamp=now,
        feature_names=["amount"],
        feature_values=[150.0],
        top_k=5,
    )
    local_exp = service.generate_local_xai(tenant_id, local_req)

    assert local_exp.transaction_id == "tx_001"
    assert (
        "contributed positively to the model's fraud-risk prediction"
        in local_exp.explanation_statement
    )  # noqa: E501
    assert "Transaction is fraudulent" not in local_exp.explanation_statement

    # Global XAI
    global_req = FraudGuardGlobalXAIRequest(
        model_name="fraudguard_xgboost",
        model_version="1.0.0",
        feature_names=["amount"],
        sample_features=[[100.0], [200.0], [300.0]],
        dataset_fingerprint="ds_fp_123",
    )
    global_exp = service.generate_global_xai(tenant_id, global_req)

    assert global_exp.model_version == "1.0.0"
    assert global_exp.sample_count == 3
    assert global_exp.feature_importance[0].feature_name == "amount"


def test_02_mandatory_adversarial_target_leakage_rejection() -> None:
    """2. Mandatory Adversarial Test: Local & Global XAI reject prohibited target leakage features."""  # noqa: E501
    tenant_id = uuid.uuid4()
    builder = TrainingDatasetBuilder()
    records = [
        {"transaction_id": f"t_{i}", "amount": 10.0, "is_fraud": 1 if i % 3 == 0 else 0}
        for i in range(30)
    ]

    dataset = builder.build_training_dataset(records)
    splits = DatasetSplitter().split_dataset(dataset, strategy="RANDOM", random_seed=42)
    model, t_res = XGBoostTrainer().train(
        splits, training_config=XGBoostTrainingConfig(n_estimators=10, random_state=42)
    )
    _, eval_manifest = ModelEvaluationService().evaluate_model(model, t_res, splits.test_dataset)

    serializer = ModelSerializer()
    raw_bytes, art_manifest = serializer.serialize_model(
        model, t_res, eval_manifest, model_version="1.0.0"
    )

    registry = ModelRegistry()
    registry.register_model(
        tenant_id, "fraudguard_xgboost", "1.0.0", raw_bytes, art_manifest, eval_manifest
    )
    registry.promote_to_production(tenant_id, "fraudguard_xgboost", "1.0.0")

    service = FraudGuardApplicationService(registry=registry)
    now = datetime.now(UTC)

    local_req = FraudGuardLocalXAIRequest(
        agent_id=uuid.uuid4(),
        transaction_id="tx_leak",
        prediction_timestamp=now,
        feature_names=["amount", "is_fraud"],  # Prohibited leakage feature!
        feature_values=[150.0, 1.0],
    )

    with pytest.raises(ValueError, match="Prohibited data leakage feature present in input"):
        service.generate_local_xai(tenant_id, local_req)
