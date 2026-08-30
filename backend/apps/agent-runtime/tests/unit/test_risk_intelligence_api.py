"""Unit & Mandatory Security Tests for Risk Intelligence API (Phase 264)."""

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
from app.schemas.fraudguard_api import FraudGuardRiskIntelligenceRequest


def test_01_risk_intelligence_pipeline_and_unit_separation() -> None:
    """1. Test risk intelligence pipeline orchestration and probability [0,1] vs score [0,100] unit separation."""  # noqa: E501
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

    policy_sig = {
        "tenant_id": str(tenant_id),
        "agent_id": str(agent_id),
        "decision": "DENY",
        "decision_code": "POLICY_LIMIT_EXCEEDED",
        "evaluated_at": now.isoformat(),
    }

    req = FraudGuardRiskIntelligenceRequest(
        agent_id=agent_id,
        transaction_id="tx_ri_001",
        model_name="fraudguard_xgboost",
        prediction_timestamp=now,
        feature_names=["amount"],
        feature_values=[150.0],
        policy_signal=policy_sig,
    )

    res = service.run_risk_intelligence(tenant_id, req)

    # Unit Separation check:
    assert 0.0 <= res.fraud_probability <= 1.0
    assert 0.0 <= res.transaction_risk_score <= 100.0

    # Policy DENY precedence check:
    assert res.policy_decision == "DENY"
    assert res.allow_ml_scoring is False
