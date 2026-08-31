"""Unit tests for ATIM Cost Optimization Service (Phase 12 / Group 6)."""

from decimal import Decimal
from unittest.mock import AsyncMock
import uuid

import pytest

from app.application.services.atim_cost_optimization_service import ATIMCostOptimizationService


@pytest.fixture
def cost_service():
    return ATIMCostOptimizationService()


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.mark.asyncio
async def test_01_check_budget_eligibility_success(cost_service, mock_db):
    tenant_id = uuid.uuid4()
    is_eligible, reason = await cost_service.check_budget_eligibility(
        db=mock_db,
        tenant_id=tenant_id,
        estimated_cost_usd=Decimal("0.001500"),
    )

    assert is_eligible is True
    assert "passed" in reason.lower()


@pytest.mark.asyncio
async def test_02_per_request_cost_exceeded(cost_service, mock_db):
    tenant_id = uuid.uuid4()
    # $0.10 exceeds default per-request max of $0.05
    is_eligible, reason = await cost_service.check_budget_eligibility(
        db=mock_db,
        tenant_id=tenant_id,
        estimated_cost_usd=Decimal("0.100000"),
    )

    assert is_eligible is False
    assert "per-request limit" in reason


@pytest.mark.asyncio
async def test_03_daily_budget_accumulation_and_exhaustion(cost_service, mock_db):
    tenant_id = uuid.uuid4()

    # Record $49.99 spend out of $50.00 daily budget
    await cost_service.record_spend(mock_db, tenant_id, Decimal("49.990000"))

    # Next request of $0.02 should breach daily limit ($50.01 > $50.00)
    is_eligible, reason = await cost_service.check_budget_eligibility(
        db=mock_db,
        tenant_id=tenant_id,
        estimated_cost_usd=Decimal("0.020000"),
    )

    assert is_eligible is False
    assert "daily quota" in reason
