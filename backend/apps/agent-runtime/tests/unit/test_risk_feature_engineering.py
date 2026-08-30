"""Unit tests for Risk Feature Engineering & Feature Validation (Phases 224-229)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.ml.feature_validation.feature_validator import FeatureValidator
from app.ml.features.base import FeatureDefinition, FeatureType, FeatureValue
from app.ml.features.intent_features import IntentRiskFeatureExtractor
from app.ml.features.merchant_features import MerchantRiskFeatureExtractor
from app.ml.features.trust_features import AgentTrustFeatureExtractor
from app.ml.features.velocity_features import VelocityFeatureExtractor
from app.schemas.merchant_behaviour_analysis import MerchantBehaviourAnalysisResult
from app.schemas.velocity_risk import VelocityRiskResult


@pytest.mark.asyncio
async def test_01_merchant_and_velocity_extractors() -> None:
    """1. Test Merchant and Velocity feature extractors."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    mock_m_service = AsyncMock()
    mock_m_service.analyze_merchant_behaviour.return_value = MerchantBehaviourAnalysisResult(
        tenant_id=tenant_id,
        agent_id=agent_id,
        merchant_id=merchant_id,
        familiarity="FAMILIAR",
        transaction_count=5,
        total_amount=Decimal("500.00"),
        average_amount=Decimal("100.00"),
        merchant_share=Decimal("0.50"),
        severity="NORMAL",
        merchant_score=Decimal("0.80"),
    )
    m_extractor = MerchantRiskFeatureExtractor(merchant_service=mock_m_service)
    mock_db = AsyncMock()

    m_feats = await m_extractor.extract_features(mock_db, tenant_id, agent_id, merchant_id)
    assert len(m_feats) == 2
    assert m_feats[0].value == 0.80
    assert m_feats[1].value is False

    mock_v_service = AsyncMock()
    mock_v_service.calculate_velocity_risk.return_value = VelocityRiskResult(
        tenant_id=tenant_id,
        agent_id=agent_id,
        velocity_risk_score=Decimal("0.25"),
        severity="NORMAL",
        burst_detected=False,
        window_minutes=60,
    )
    v_extractor = VelocityFeatureExtractor(velocity_risk_service=mock_v_service)

    v_feats = await v_extractor.extract_features(mock_db, tenant_id, agent_id, window_minutes=60)
    assert len(v_feats) == 2
    assert v_feats[0].value == 0.25
    assert v_feats[1].value is False


@pytest.mark.asyncio
async def test_02_policy_intent_trust_extractors() -> None:
    """2. Test Policy, Intent, and Trust feature extractors."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    i_extractor = IntentRiskFeatureExtractor()
    record = {"amount": Decimal("100.00"), "currency": "USD"}
    i_feats = i_extractor.extract_features(tenant_id, agent_id, record)
    assert len(i_feats) == 2
    assert i_feats[0].value == 0.00
    assert i_feats[1].value is True

    t_extractor = AgentTrustFeatureExtractor()
    t_feats = t_extractor.extract_features(tenant_id, agent_id, Decimal("0.90"))
    assert len(t_feats) == 3
    t_map = {f.definition.name: f.value for f in t_feats}
    assert t_map["trust_score"] == 0.90
    assert t_map["risk_score"] < 0.20
    assert t_map["trust_score"] != t_map["risk_score"]


def test_03_feature_validator_nan_and_leakage() -> None:
    """3. Test FeatureValidator detects NaN values and tenant leakage."""
    validator = FeatureValidator()
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()

    fdef = FeatureDefinition(
        name="test_nan",
        feature_type=FeatureType.NUMERIC,
        source="TEST",
        transformation_description="Test NaN",
    )

    feats = [
        FeatureValue(definition=fdef, value=float("nan"), tenant_id=str(t1)),
        FeatureValue(definition=fdef, value=1.0, tenant_id=str(t2)),  # tenant leak
    ]

    res = validator.validate_features(feats, expected_tenant_id=t1)
    assert res.valid is False
    assert any(v.code == "NAN_VALUE" for v in res.violations)
    assert any(v.code == "TENANT_LEAKAGE" for v in res.violations)
