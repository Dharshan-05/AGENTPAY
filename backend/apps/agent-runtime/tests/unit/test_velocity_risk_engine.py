"""Unit and Security Tests for Velocity Risk Engine (Phase 212)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.application.services.velocity_risk_service import VelocityRiskService
from app.schemas.velocity_detection import VelocityDetectionResult
from app.schemas.velocity_risk import VelocityRiskRequest


@pytest.fixture
def service() -> VelocityRiskService:
    mock_v_service = AsyncMock()
    return VelocityRiskService(velocity_service=mock_v_service)


@pytest.mark.asyncio
async def test_01_calculate_normal_velocity_risk(
    service: VelocityRiskService,
) -> None:
    """1. Test normal velocity returns NORMAL severity and score 0.00."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    service.velocity_service.detect_velocity.return_value = VelocityDetectionResult(  # type: ignore[attr-defined]  # noqa: E501
        tenant_id=tenant_id,
        agent_id=agent_id,
        window_start=pytest.importorskip("datetime").datetime.now(
            pytest.importorskip("datetime").timezone.utc
        ),
        window_end=pytest.importorskip("datetime").datetime.now(
            pytest.importorskip("datetime").timezone.utc
        ),
        transaction_count=1,
        total_amount=Decimal("10.00"),
        transactions_per_minute=Decimal("0.02"),
        transactions_per_hour=Decimal("1.00"),
        baseline_available=True,
        velocity_score=Decimal("0.00"),
        severity="NORMAL",
        detection_state="NORMAL",
        reason_codes=[],
    )

    req = VelocityRiskRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
    )

    mock_db = AsyncMock()
    res = await service.calculate_velocity_risk(mock_db, req)
    assert res.velocity_risk_score == Decimal("0.00")
    assert res.severity == "NORMAL"
