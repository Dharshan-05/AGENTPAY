"""Unit and Security Tests for Category Behaviour Analysis Engine (Phase 205)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest

from app.application.services.category_behaviour_analysis_service import (
    CategoryBehaviourAnalysisService,
)
from app.schemas.behaviour_baseline import BehaviourBaseline
from app.schemas.behaviour_tracking import BehaviourTrackingQueryResponse
from app.schemas.category_behaviour_analysis import CategoryBehaviourAnalysisRequest


@pytest.fixture
def service() -> CategoryBehaviourAnalysisService:
    mock_baseline = AsyncMock()
    mock_tracking = AsyncMock()
    return CategoryBehaviourAnalysisService(
        baseline_service=mock_baseline, tracking_service=mock_tracking
    )


@pytest.mark.asyncio
async def test_01_first_seen_category_returns_medium_severity(
    service: CategoryBehaviourAnalysisService,
) -> None:
    """1. Test analysis for first-seen category returns FIRST_SEEN familiarity."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    service.baseline_service.compute_baseline.return_value = BehaviourBaseline(  # type: ignore[attr-defined]  # noqa: E501
        agent_id=agent_id,
        tenant_id=tenant_id,
        baseline_available=True,
        state="ESTABLISHED",
        observation_count=10,
        successful_count=10,
        failed_count=0,
        frequent_categories=[],
    )

    service.tracking_service.get_agent_events.return_value = BehaviourTrackingQueryResponse(  # type: ignore[attr-defined]  # noqa: E501
        tenant_id=tenant_id,
        agent_id=agent_id,
        events=[],
        total_count=0,
    )

    req = CategoryBehaviourAnalysisRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        category="Electronics",
    )

    mock_db = AsyncMock()
    res = await service.analyze_category_behaviour(mock_db, req)
    assert res.normalized_category == "electronics"
    assert res.familiarity == "FIRST_SEEN"
    assert res.severity == "MEDIUM"
    assert "FIRST_SEEN_CATEGORY" in res.reason_codes
