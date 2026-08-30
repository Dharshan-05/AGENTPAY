"""Unit and Security Tests for Behaviour Risk Engine (Phase 211)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.application.services.behaviour_risk_service import BehaviourRiskService
from app.schemas.behaviour_baseline import BehaviourBaseline
from app.schemas.behaviour_risk import BehaviourRiskRequest


@pytest.fixture
def service() -> BehaviourRiskService:
    mock_baseline = AsyncMock()
    mock_deviation = AsyncMock()
    return BehaviourRiskService(baseline_service=mock_baseline, deviation_service=mock_deviation)


@pytest.mark.asyncio
async def test_01_cold_start_behaviour_risk(
    service: BehaviourRiskService,
) -> None:
    """1. Test baseline unavailable returns COLD_START behaviour risk."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    service.baseline_service.compute_baseline.return_value = BehaviourBaseline(  # type: ignore[attr-defined]  # noqa: E501
        agent_id=agent_id,
        tenant_id=tenant_id,
        baseline_available=False,
        state="COLD_START",
        observation_count=0,
        successful_count=0,
        failed_count=0,
    )

    req = BehaviourRiskRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
    )

    mock_db = AsyncMock()
    res = await service.calculate_behaviour_risk(mock_db, req)
    assert res.severity == "COLD_START"
    assert res.behaviour_risk_score == Decimal("0.00")
    assert res.confidence == Decimal("0.00")
