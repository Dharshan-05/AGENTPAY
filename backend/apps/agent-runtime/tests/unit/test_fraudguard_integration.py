"""Unit & Mandatory Security Precedence Tests for End-to-End FraudGuard Integration (Phase 265)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.application.services.fraudguard_service import FraudGuardApplicationService
from app.ml.dataset.training_dataset_builder import TrainingDatasetBuilder
from app.ml.evaluation.evaluation_service import ModelEvaluationService
from app.ml.registry.model_registry import ModelRegistry
from app.ml.serialization.model_serializer import ModelSerializer
from app.ml.splitting.dataset_splitter import DatasetSplitter
from app.ml.training.training_config import XGBoostTrainingConfig
from app.ml.training.xgboost_trainer import XGBoostTrainer
from app.schemas.fraudguard_api import FraudGuardEvaluateRequest


def test_01_end_to_end_fraudguard_evaluation() -> None:
    """1. Test unified end-to-end FraudGuard evaluation orchestration and audit manifest generation."""  # noqa: E501
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

    req = FraudGuardEvaluateRequest(
        agent_id=agent_id,
        transaction_id="tx_e2e_001",
        model_name="fraudguard_xgboost",
        prediction_timestamp=now,
        feature_names=["amount"],
        feature_values=[150.0],
        include_xai=True,
    )

    res = service.evaluate_transaction(tenant_id, req)

    assert res.transaction_id == "tx_e2e_001"
    assert res.authoritative_decision == "ALLOW"
    assert res.allow_ml_scoring is True
    assert res.local_explanation is not None
    assert res.audit_manifest["transaction_id"] == "tx_e2e_001"


def test_02_mandatory_security_policy_deny_precedence_in_e2e_evaluation() -> None:
    """2. Mandatory Security Test: Policy DENY overrides ML score in end-to-end evaluation. ML CANNOT override Policy DENY."""  # noqa: E501
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    now = datetime.now(UTC)

    builder = TrainingDatasetBuilder()
    records = [
        {"transaction_id": f"t_{i}", "amount": 10.0, "is_fraud": 1 if i % 3 == 0 else 0}
        for i in range(30)
    ]

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

    policy_deny_signal = {
        "tenant_id": str(tenant_id),
        "agent_id": str(agent_id),
        "decision": "DENY",
        "decision_code": "HIGH_RISK_POLICY_DENY",
        "evaluated_at": now.isoformat(),
    }

    req = FraudGuardEvaluateRequest(
        agent_id=agent_id,
        transaction_id="tx_policy_deny",
        model_name="fraudguard_xgboost",
        prediction_timestamp=now,
        feature_names=["amount"],
        feature_values=[10.0],
        policy_signal=policy_deny_signal,
    )

    res = service.evaluate_transaction(tenant_id, req)

    # Mandatory Security Precedence Checks:
    assert res.authoritative_decision == "DENY"
    assert (
        res.allow_ml_scoring is False
    )  # Policy DENY strictly forbids downstream ML authorization!  # noqa: E501
    assert res.advisory_risk_intelligence.policy_risk is not None
    assert res.advisory_risk_intelligence.policy_risk.policy_risk_score == 100.0  # noqa: E501
