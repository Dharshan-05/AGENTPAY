"""Unit and Security Tests for Daily Spending Limits Engine (Phase 190)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.daily_spending_limit_service import DailySpendingLimitService


@pytest.fixture
def service() -> DailySpendingLimitService:
    service = DailySpendingLimitService()
    service.usage_provider.get_daily_spending_usage = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_daily_spending_limit_within_bounds(
    service: DailySpendingLimitService,
) -> None:
    """1. Test daily cumulative usage plus requested amount within limit."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    # Mock current daily usage to $200.00
    service.usage_provider.get_daily_spending_usage.return_value = Decimal("200.00")  # type: ignore[attr-defined]  # noqa: E501

    mock_db = MagicMock()
    res = await service.evaluate_daily_spending_limit(
        mock_db,
        tenant_id,
        agent_id,
        amount=Decimal("150.00"),
        configured_daily_limit=Decimal("500.00"),
    )
    assert res.decision == "WITHIN_LIMIT"
    assert res.current_usage == Decimal("200.00")
    assert res.projected_usage == Decimal("350.00")
    assert res.remaining_limit == Decimal("300.00")


@pytest.mark.asyncio
async def test_02_daily_spending_limit_exceeded(
    service: DailySpendingLimitService,
) -> None:
    """2. Test daily cumulative usage plus requested amount exceeding limit."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    # Mock current daily usage to $400.00
    service.usage_provider.get_daily_spending_usage.return_value = Decimal("400.00")  # type: ignore[attr-defined]  # noqa: E501

    mock_db = MagicMock()
    res = await service.evaluate_daily_spending_limit(
        mock_db,
        tenant_id,
        agent_id,
        amount=Decimal("150.00"),
        configured_daily_limit=Decimal("500.00"),
    )
    assert res.decision == "LIMIT_EXCEEDED"
    assert res.projected_usage == Decimal("550.00")
