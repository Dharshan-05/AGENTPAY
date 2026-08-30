"""Unit and Security Tests for AgentGuard Integration Gateway (Phase 215)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.application.services.agentguard_integration_service import (
    AgentGuardIntegrationService,
)
from app.schemas.agentguard_decision import (
    AgentGuardDecisionRequest,
    AgentGuardDecisionResult,
)


@pytest.fixture
def service() -> AgentGuardIntegrationService:
    mock_decision = AsyncMock()
    return AgentGuardIntegrationService(decision_service=mock_decision)


@pytest.mark.asyncio
async def test_01_evaluate_agent_request_delegates_to_decision_engine(
    service: AgentGuardIntegrationService,
) -> None:
    """1. Test evaluating agent request through integration gateway."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    now = pytest.importorskip("datetime").datetime.now(pytest.importorskip("datetime").timezone.utc)

    expected_res = AgentGuardDecisionResult(
        agent_id=agent_id,
        tenant_id=tenant_id,
        decision="ALLOW",
        risk_level="LOW",
        trust_score=Decimal("1.00"),
        behaviour_risk_score=Decimal("0.00"),
        velocity_risk_score=Decimal("0.00"),
        intent_risk_score=Decimal("0.00"),
        can_proceed=True,
        requires_approval=False,
        reason_codes=["POLICY_ALLOWED"],
        risk_factors=[],
        evaluated_at=now,
    )

    service.decision_service.evaluate_agentguard_decision.return_value = expected_res  # type: ignore[attr-defined]  # noqa: E501

    req = AgentGuardDecisionRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        amount=Decimal("50.00"),
    )

    mock_db = AsyncMock()
    res = await service.evaluate_agent_request(mock_db, req)
    assert res.decision == "ALLOW"
    assert res.can_proceed is True
