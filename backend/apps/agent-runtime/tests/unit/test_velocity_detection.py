"""Unit and Security Tests for Velocity Detection Engine (Phase 203)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.application.services.velocity_detection_service import VelocityDetectionService
from app.infrastructure.database.models.payment_order import PaymentOrder
from app.schemas.velocity_detection import VelocityDetectionRequest


@pytest.fixture
def service() -> VelocityDetectionService:
    return VelocityDetectionService()


@pytest.mark.asyncio
async def test_01_normal_velocity(service: VelocityDetectionService) -> None:
    """1. Test velocity analysis with count within allowed threshold."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    req = VelocityDetectionRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        max_allowed_count=10,
    )

    res = await service.detect_velocity(mock_db, req)
    assert res.transaction_count == 0
    assert res.severity == "NORMAL"
    assert res.velocity_score == Decimal("0.00")


@pytest.mark.asyncio
async def test_02_velocity_count_exceeded_critical(
    service: VelocityDetectionService,
) -> None:
    """2. Test transaction count exceeding threshold returns CRITICAL severity."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    orders = [
        PaymentOrder(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            total_amount=Decimal("10.00"),
        )
        for _ in range(5)
    ]

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = orders

    req = VelocityDetectionRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        max_allowed_count=3,
    )

    res = await service.detect_velocity(mock_db, req)
    assert res.transaction_count == 5
    assert res.severity == "CRITICAL"
    assert res.velocity_score == Decimal("1.00")
    assert "VELOCITY_COUNT_EXCEEDED" in res.reason_codes
