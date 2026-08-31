"""Security & Tenant Isolation tests for ATIM Telemetry & API (Phase 10 / Group 5)."""

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, status

from app.api.v1.atim import analyze_transaction_intelligence
from app.application.services.atim_observability_service import ATIMObservabilityService
from app.domain.atim.telemetry_models import ATIMAnalyzeRequest, ATIMTelemetryRecord


@pytest.mark.asyncio
async def test_01_cross_tenant_analysis_rejected():
    user_tenant = uuid.uuid4()
    other_tenant = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_user = MagicMock()
    mock_user.tenant_id = user_tenant

    mock_db = AsyncMock()
    facade_service = MagicMock()

    # Request attempting analysis on other_tenant
    req = ATIMAnalyzeRequest(
        prompt="Transfer $500 to vendor",
        tenant_id=other_tenant,
        agent_id=agent_id,
    )

    with pytest.raises(HTTPException) as exc_info:
        await analyze_transaction_intelligence(req, mock_user, mock_db, facade_service)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Cross-tenant" in exc_info.value.detail


@pytest.mark.asyncio
async def test_02_tenant_telemetry_query_strictly_isolated():
    tenant1 = uuid.uuid4()
    tenant2 = uuid.uuid4()

    observability = ATIMObservabilityService()

    # Mock DB query returning data ONLY for tenant1
    row_t1 = MagicMock(
        tenant_id=tenant1,
        is_security_blocked=False,
        fallback_used=False,
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        estimated_cost_usd=Decimal("0.001500"),
        latency_ms=45.0,
        provider="openai",
        selected_model="openai/gpt-4o",
    )

    mock_db = AsyncMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = [row_t1]

    agg_t1 = await observability.get_tenant_telemetry_aggregate(mock_db, tenant1)
    assert agg_t1.tenant_id == tenant1
    assert agg_t1.total_requests == 1

    # Mock DB returning empty for tenant2
    mock_db.execute.return_value.scalars.return_value.all.return_value = []
    agg_t2 = await observability.get_tenant_telemetry_aggregate(mock_db, tenant2)
    assert agg_t2.tenant_id == tenant2
    assert agg_t2.total_requests == 0
    assert agg_t2.total_cost_usd == Decimal("0.000000")
