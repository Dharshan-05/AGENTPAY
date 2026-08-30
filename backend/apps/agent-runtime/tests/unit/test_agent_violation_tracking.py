"""Unit and Security Tests for Agent Violation Tracking Engine (Phase 209)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.application.services.agent_violation_tracking_service import (
    AgentViolationTrackingService,
)
from app.infrastructure.database.models.payment_order import PaymentOrder
from app.schemas.agent_violations import AgentViolationQueryRequest


@pytest.fixture
def service() -> AgentViolationTrackingService:
    return AgentViolationTrackingService()


@pytest.mark.asyncio
async def test_01_get_agent_violations(
    service: AgentViolationTrackingService,
) -> None:
    """1. Test querying failed payment orders as agent violations."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    order_id = uuid.uuid4()

    order = PaymentOrder(
        id=order_id,
        tenant_id=tenant_id,
        agent_id=agent_id,
        status="failed",
        total_amount=Decimal("100.00"),
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = [order]

    req = AgentViolationQueryRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
    )

    res = await service.get_agent_violations(mock_db, req)
    assert res.total_count == 1
    assert res.violations[0].violation_id == order_id
    assert res.violations[0].severity == "HIGH"
