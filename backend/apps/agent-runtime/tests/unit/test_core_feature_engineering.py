"""Unit tests for Core Feature Engineering (Phases 221-223)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.ml.features.base import (  # noqa: E501
    FeatureCategory,
    FeatureDefinition,
    FeatureDependencyGraph,
    FeatureSecurityClassification,
    FeatureType,
    FeatureValue,
)
from app.ml.features.behaviour_features import BehaviourFeatureExtractor
from app.ml.features.transaction_features import TransactionFeatureExtractor
from app.schemas.behaviour_risk import BehaviourRiskResult


def test_01_feature_value_and_dependency_graph() -> None:
    """1. Test FeatureValue taxonomy metadata and FeatureDependencyGraph validation."""
    fdef1 = FeatureDefinition(
        name="feat_a",
        feature_type=FeatureType.NUMERIC,
        source="TEST",
        category=FeatureCategory.TRANSACTION,
        security_classification=FeatureSecurityClassification.PUBLIC,
        transformation_description="Test transformation A",
    )
    fdef2 = FeatureDefinition(
        name="feat_b",
        feature_type=FeatureType.NUMERIC,
        source="TEST",
        category=FeatureCategory.TRANSACTION,
        transformation_description="Test transformation B",
        dependencies=["feat_a"],
    )

    graph = FeatureDependencyGraph()
    graph.add_feature(fdef1)
    graph.add_feature(fdef2)

    issues = graph.validate_dependencies()
    assert len(issues) == 0

    fval = FeatureValue(
        definition=fdef1,
        value=Decimal("123.45"),
        tenant_id="t123",
        agent_id="a456",
    )
    d = fval.to_dict()
    assert d["name"] == "feat_a"
    assert d["category"] == "TRANSACTION"
    assert d["security_classification"] == "PUBLIC"


def test_02_transaction_feature_extractor_point_in_time() -> None:
    """2. Test TransactionFeatureExtractor point-in-time correctness."""
    extractor = TransactionFeatureExtractor()
    record = {
        "tenant_id": str(uuid.uuid4()),
        "agent_id": str(uuid.uuid4()),
        "amount": Decimal("100.00"),
        "created_at": "2026-08-26T23:30:00Z",
    }
    pred_ts = datetime(2026, 8, 26, 23, 40, 0, tzinfo=UTC)
    feats = extractor.extract_features(record, prediction_timestamp=pred_ts)
    assert len(feats) == 5
    feat_map = {f.definition.name: f.value for f in feats}
    assert feat_map["tx_amount"] == Decimal("100.00")
    assert feat_map["point_in_time_valid"] is True


@pytest.mark.asyncio
async def test_03_behaviour_feature_extractor_integration() -> None:
    """3. Test BehaviourFeatureExtractor consumes AGENTGUARD BehaviourRiskService output."""
    mock_b_service = AsyncMock()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_b_service.calculate_behaviour_risk.return_value = BehaviourRiskResult(
        tenant_id=tenant_id,
        agent_id=agent_id,
        behaviour_risk_score=Decimal("0.15"),
        severity="NORMAL",
        risk_factors=[],
        confidence=Decimal("1.00"),
    )

    extractor = BehaviourFeatureExtractor(behaviour_service=mock_b_service)
    mock_db = AsyncMock()

    feats = await extractor.extract_features(
        mock_db, tenant_id, agent_id, {"amount": Decimal("50.00")}
    )  # noqa: E501
    assert len(feats) == 3
    feat_map = {f.definition.name: f.value for f in feats}
    assert feat_map["behaviour_risk_score"] == 0.15
    assert feat_map["is_behaviour_cold_start"] is False
