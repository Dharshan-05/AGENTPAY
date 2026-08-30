"""Unit and Security Tests for Behaviour Tracking Engine (Phase 200)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.application.services.behaviour_tracking_service import BehaviourTrackingService
from app.infrastructure.database.models.payment_order import PaymentOrder
from app.schemas.behaviour_tracking import BehaviourTrackingQueryRequest


@pytest.fixture
def service() -> BehaviourTrackingService:
    return BehaviourTrackingService()


@pytest.mark.asyncio
async def test_01_get_agent_events_returns_normalized_events(
    service: BehaviourTrackingService,
) -> None:
    """1. Test retrieving and normalizing agent activity events in tenant scope."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    order_id = uuid.uuid4()

    order = PaymentOrder(
        id=order_id,
        tenant_id=tenant_id,
        agent_id=agent_id,
        order_reference="ORD-001",
        status="completed",
        amount=Decimal("100.00"),
        total_amount=Decimal("100.00"),
        currency_code="USD",
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = [order]

    req = BehaviourTrackingQueryRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        limit=50,
    )

    res = await service.get_agent_events(mock_db, req)
    assert res.total_count == 1
    assert res.events[0].event_id == order_id
    assert res.events[0].outcome == "SUCCESS"
    assert res.events[0].amount == Decimal("100.00")
