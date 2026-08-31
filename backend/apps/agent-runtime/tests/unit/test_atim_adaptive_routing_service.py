"""Unit tests for ATIM Adaptive Routing Service (Phase 12 / Group 6)."""

from decimal import Decimal
from unittest.mock import AsyncMock
import uuid

import pytest

from app.application.services.atim_adaptive_routing_service import ATIMAdaptiveRoutingService


@pytest.fixture
def adaptive_router():
    return ATIMAdaptiveRoutingService()


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.mark.asyncio
async def test_01_adaptive_routing_clean_flow(adaptive_router, mock_db):
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    route_res, explanation = await adaptive_router.route_adaptive_request(
        db=mock_db,
        prompt="Pay $150 to cloud vendor",
        task_type="PAYMENT",
        tenant_id=tenant_id,
        agent_id=agent_id,
    )

    assert route_res.selected_model == "openai/gpt-4o"
    assert route_res.provider == "openai"
    assert route_res.fallback_used is False
    assert explanation.tenant_id == tenant_id
    assert explanation.selected_model == "openai/gpt-4o"


@pytest.mark.asyncio
async def test_02_adaptive_routing_cost_budget_fallback(adaptive_router, mock_db):
    tenant_id = uuid.uuid4()

    # Exhaust tenant daily budget
    await adaptive_router.cost_service.record_spend(mock_db, tenant_id, Decimal("49.990000"))

    route_res, explanation = await adaptive_router.route_adaptive_request(
        db=mock_db,
        prompt="Lookup recent transactions",
        task_type="TRANSACTION_LOOKUP",
        tenant_id=tenant_id,
    )

    # Expensive model gpt-4o ($0.001500) breaches daily quota $50.00 ($49.991500 > $50.00).
    # Router falls back to gpt-4o-mini ($0.000300).
    assert route_res.fallback_used is True
    assert route_res.selected_model == "openai/gpt-4o-mini"
    assert explanation.fallback_chain == ["openai/gpt-4o-mini", "rule_engine"]
