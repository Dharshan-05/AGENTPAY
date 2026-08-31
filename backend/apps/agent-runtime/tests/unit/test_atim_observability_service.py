"""Unit tests for ATIM Observability & Telemetry Service (Phase 10 / Group 5)."""

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.atim_observability_service import ATIMObservabilityService
from app.domain.atim.telemetry_models import ATIMTelemetryRecord


@pytest.fixture
def observability_service():
    return ATIMObservabilityService()


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_01_record_telemetry_success(observability_service, mock_db):
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    record = ATIMTelemetryRecord(
        tenant_id=tenant_id,
        agent_id=agent_id,
        prompt_text="Pay $50 to Merchant",
        action="payment",
        amount=Decimal("50.00"),
        currency="USD",
        selected_model="openai/gpt-4o",
        provider="openai",
        latency_ms=120.5,
        prompt_tokens=100,
        completion_tokens=30,
        total_tokens=130,
        estimated_cost_usd=Decimal("0.001300"),
    )

    result = await observability_service.record_telemetry(mock_db, record)

    assert result.tenant_id == tenant_id
    assert result.agent_id == agent_id
    assert result.selected_model == "openai/gpt-4o"
    assert result.total_tokens == 130
    assert mock_db.add.called


@pytest.mark.asyncio
async def test_02_get_tenant_telemetry_aggregate_empty(observability_service, mock_db):
    tenant_id = uuid.uuid4()
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    agg = await observability_service.get_tenant_telemetry_aggregate(mock_db, tenant_id)

    assert agg.tenant_id == tenant_id
    assert agg.total_requests == 0
    assert agg.security_blocked_requests == 0
    assert agg.total_tokens == 0
    assert agg.total_cost_usd == Decimal("0.000000")
    assert agg.latency_distribution.avg_ms == 0.0


@pytest.mark.asyncio
async def test_03_get_tenant_telemetry_aggregate_populated(observability_service, mock_db):
    tenant_id = uuid.uuid4()

    # Create mock telemetry rows
    row1 = MagicMock(
        is_security_blocked=False,
        fallback_used=False,
        prompt_tokens=100,
        completion_tokens=20,
        total_tokens=120,
        estimated_cost_usd=Decimal("0.001000"),
        latency_ms=100.0,
        provider="openai",
        selected_model="openai/gpt-4o",
    )
    row2 = MagicMock(
        is_security_blocked=True,
        fallback_used=True,
        prompt_tokens=80,
        completion_tokens=0,
        total_tokens=80,
        estimated_cost_usd=Decimal("0.000500"),
        latency_ms=200.0,
        provider="anthropic",
        selected_model="anthropic/claude-3-5-sonnet-20241022",
    )

    mock_db.execute.return_value.scalars.return_value.all.return_value = [row1, row2]

    agg = await observability_service.get_tenant_telemetry_aggregate(mock_db, tenant_id)

    assert agg.tenant_id == tenant_id
    assert agg.total_requests == 2
    assert agg.security_blocked_requests == 1
    assert agg.security_block_rate == 0.5
    assert agg.fallback_requests == 1
    assert agg.total_tokens == 200
    assert agg.total_cost_usd == Decimal("0.001500")
    assert agg.latency_distribution.avg_ms == 150.0
    assert len(agg.provider_breakdown) == 2
