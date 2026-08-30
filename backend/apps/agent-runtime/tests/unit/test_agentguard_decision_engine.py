"""Unit and Security Tests for AgentGuard Decision Engine (Phase 214)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.agentguard_decision_service import AgentGuardDecisionService
from app.schemas.agentguard_decision import AgentGuardDecisionRequest
from app.schemas.policy_evaluation import PolicyEvaluationResult


@pytest.fixture
def service() -> AgentGuardDecisionService:
    mock_beh: Any = AsyncMock()
    mock_vel: Any = AsyncMock()
    mock_intent: Any = MagicMock()
    mock_policy: Any = AsyncMock()
    return AgentGuardDecisionService(
        behaviour_risk_service=mock_beh,
        velocity_risk_service=mock_vel,
        intent_risk_service=mock_intent,
        policy_evaluation_service=mock_policy,
    )


@pytest.mark.asyncio
async def test_01_policy_deny_is_dominant(
    service: AgentGuardDecisionService,
) -> None:
    """1. Test that policy DENY decision is dominant over all trust/risk signals."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    now = pytest.importorskip("datetime").datetime.now(pytest.importorskip("datetime").timezone.utc)

    intent_mock: Any = service.intent_risk_service
    beh_mock: Any = service.behaviour_risk_service
    vel_mock: Any = service.velocity_risk_service
    pol_mock: Any = service.policy_evaluation_service

    intent_mock.calculate_intent_risk.return_value = pytest.importorskip(
        "app.schemas.intent_risk"
    ).IntentRiskResult(
        tenant_id=tenant_id,
        agent_id=agent_id,
        intent_risk_score=Decimal("0.00"),
        severity="NORMAL",
        risk_factors=[],
        can_proceed=True,
    )

    beh_mock.calculate_behaviour_risk.return_value = pytest.importorskip(
        "app.schemas.behaviour_risk"
    ).BehaviourRiskResult(
        tenant_id=tenant_id,
        agent_id=agent_id,
        behaviour_risk_score=Decimal("0.00"),
        severity="NORMAL",
        risk_factors=[],
        confidence=Decimal("1.00"),
    )

    vel_mock.calculate_velocity_risk.return_value = pytest.importorskip(
        "app.schemas.velocity_risk"
    ).VelocityRiskResult(
        tenant_id=tenant_id,
        agent_id=agent_id,
        velocity_risk_score=Decimal("0.00"),
        severity="NORMAL",
        window_minutes=60,
        risk_factors=[],
    )

    pol_mock.evaluate_policies.return_value = PolicyEvaluationResult(
        agent_id=agent_id,
        tenant_id=tenant_id,
        decision="DENIED",
        evaluated_policy_ids=[],
        matched_policy_ids=[],
        denied_policy_ids=[],
        reason_codes=["BLOCKED_BY_POLICY"],
        decision_reason="Policy denied transaction",
        highest_priority=100,
        evaluated_at=now,
    )

    req = AgentGuardDecisionRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        amount=Decimal("100.00"),
    )

    mock_db = AsyncMock()
    res = await service.evaluate_agentguard_decision(mock_db, req)
    assert res.decision == "DENIED"
    assert res.can_proceed is False
