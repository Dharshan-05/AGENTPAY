"""Unit tests for ATIM REST API endpoints (Phase 10 / Group 5)."""

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.api.v1.atim import (
    analyze_transaction_intelligence,
    evaluate_atim_models,
    get_atim_telemetry,
    list_atim_models,
    reset_atim_circuit_breaker,
)
from app.domain.atim.telemetry_models import ATIMAnalyzeRequest
from app.infrastructure.database.models.atim_telemetry import ATIMExecutionTelemetry


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = uuid.uuid4()
    user.tenant_id = uuid.uuid4()
    return user


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_01_analyze_transaction_intelligence_success(mock_user, mock_db):
    tenant_id = mock_user.tenant_id
    agent_id = uuid.uuid4()

    req = ATIMAnalyzeRequest(
        prompt="Transfer $100 to supplier for invoice #1234",
        tenant_id=tenant_id,
        agent_id=agent_id,
        requested_action="payment",
        requested_amount=Decimal("100.00"),
        requested_currency="USD",
    )

    facade_service = MagicMock()
    facade_response = MagicMock(
        request_id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent_id,
        prompt_security_blocked=False,
        selected_model="openai/gpt-4o",
        provider="openai",
        fallback_used=False,
        task_type="INTENT_EXTRACTION",
        complexity="MODERATE",
        risk_level="MEDIUM",
        plan_valid=True,
        final_execution_decision="ALLOW",
        latency_ms=12.5,
        estimated_cost_usd=Decimal("0.001500"),
    )
    facade_service.analyze_transaction_intelligence = AsyncMock(return_value=facade_response)

    res = await analyze_transaction_intelligence(req, mock_user, mock_db, facade_service)

    assert res.tenant_id == tenant_id
    assert res.agent_id == agent_id
    assert res.prompt_security_blocked is False
    assert res.selected_model == "openai/gpt-4o"
    assert res.final_execution_decision == "ALLOW"


@pytest.mark.asyncio
async def test_02_list_atim_models_success(mock_user):
    registry = MagicMock()
    m1 = MagicMock(
        model_id="openai/gpt-4o",
        provider_name="openai",
        context_window=128000,
        security_score=Decimal("0.98"),
        schema_score=Decimal("0.99"),
        status="enabled",
    )
    registry.list_all_models.return_value = [m1]

    circuit_breaker = MagicMock()
    circuit_breaker.get_state.return_value.value = "CLOSED"

    res = await list_atim_models(mock_user, registry, circuit_breaker)

    assert len(res) == 1
    assert res[0]["model_id"] == "openai/gpt-4o"
    assert res[0]["circuit_breaker_state"] == "CLOSED"


@pytest.mark.asyncio
async def test_03_reset_atim_circuit_breaker(mock_user):
    circuit_breaker = MagicMock()
    res = await reset_atim_circuit_breaker("openai", mock_user, circuit_breaker)

    assert res["provider"] == "openai"
    assert res["circuit_breaker_state"] == "CLOSED"
    assert circuit_breaker.reset.called_with("openai")
