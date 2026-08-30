"""Unit and Security Tests for Behaviour Baseline Engine (Phase 201)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.application.services.behaviour_baseline_service import BehaviourBaselineService
from app.schemas.behaviour_tracking import BehaviourEvent, BehaviourTrackingQueryResponse


@pytest.fixture
def service() -> BehaviourBaselineService:
    mock_tracking = AsyncMock()
    return BehaviourBaselineService(tracking_service=mock_tracking)


@pytest.mark.asyncio
async def test_01_insufficient_history_returns_cold_start(
    service: BehaviourBaselineService,
) -> None:
    """1. Test baseline computation with < min_observations returns COLD_START."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    service.tracking_service.get_agent_events.return_value = BehaviourTrackingQueryResponse(  # type: ignore[attr-defined]  # noqa: E501
        tenant_id=tenant_id,
        agent_id=agent_id,
        events=[],
        total_count=0,
    )

    mock_db = AsyncMock()
    res = await service.compute_baseline(mock_db, tenant_id, agent_id, min_observations=5)
    assert res.baseline_available is False
    assert res.state == "COLD_START"


@pytest.mark.asyncio
async def test_02_established_baseline_computes_statistics(
    service: BehaviourBaselineService,
) -> None:
    """2. Test baseline computation with sufficient observations returns ESTABLISHED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    events = [
        BehaviourEvent(
            event_id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            event_type="PAYMENT",
            occurred_at=datetime.now(UTC),
            amount=Decimal("100.00"),
            currency="USD",
            status="completed",
            outcome="SUCCESS",
        )
        for _ in range(6)
    ]

    service.tracking_service.get_agent_events.return_value = BehaviourTrackingQueryResponse(  # type: ignore[attr-defined]  # noqa: E501
        tenant_id=tenant_id,
        agent_id=agent_id,
        events=events,
        total_count=6,
    )

    mock_db = AsyncMock()
    res = await service.compute_baseline(mock_db, tenant_id, agent_id, min_observations=5)
    assert res.baseline_available is True
    assert res.state == "ESTABLISHED"
    assert res.amount_stats is not None
    assert res.amount_stats.average_amount == Decimal("100.00")
