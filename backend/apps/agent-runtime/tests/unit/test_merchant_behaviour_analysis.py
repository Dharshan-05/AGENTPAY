"""Unit and Security Tests for Merchant Behaviour Analysis Engine (Phase 204)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest

from app.application.services.merchant_behaviour_analysis_service import (
    MerchantBehaviourAnalysisService,
)
from app.schemas.behaviour_baseline import BehaviourBaseline
from app.schemas.behaviour_tracking import BehaviourTrackingQueryResponse
from app.schemas.merchant_behaviour_analysis import MerchantBehaviourAnalysisRequest


@pytest.fixture
def service() -> MerchantBehaviourAnalysisService:
    mock_baseline = AsyncMock()
    mock_tracking = AsyncMock()
    return MerchantBehaviourAnalysisService(
        baseline_service=mock_baseline, tracking_service=mock_tracking
    )


@pytest.mark.asyncio
async def test_01_first_seen_merchant_returns_medium_severity(
    service: MerchantBehaviourAnalysisService,
) -> None:
    """1. Test analysis for first-seen merchant returns FIRST_SEEN familiarity."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    service.baseline_service.compute_baseline.return_value = BehaviourBaseline(  # type: ignore[attr-defined]  # noqa: E501
        agent_id=agent_id,
        tenant_id=tenant_id,
        baseline_available=True,
        state="ESTABLISHED",
        observation_count=10,
        successful_count=10,
        failed_count=0,
        frequent_merchants=[],
    )

    service.tracking_service.get_agent_events.return_value = BehaviourTrackingQueryResponse(  # type: ignore[attr-defined]  # noqa: E501
        tenant_id=tenant_id,
        agent_id=agent_id,
        events=[],
        total_count=0,
    )

    req = MerchantBehaviourAnalysisRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        merchant_id=merchant_id,
    )

    mock_db = AsyncMock()
    res = await service.analyze_merchant_behaviour(mock_db, req)
    assert res.familiarity == "FIRST_SEEN"
    assert res.severity == "MEDIUM"
    assert "FIRST_SEEN_MERCHANT" in res.reason_codes
