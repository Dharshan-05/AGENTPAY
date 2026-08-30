"""Unit and Security Tests for Agent Risk Profile Engine (Phase 208)."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.application.services.agent_risk_profile_service import AgentRiskProfileService
from app.schemas.agent_risk_profile import RiskFactor


@pytest.fixture
def service() -> AgentRiskProfileService:
    return AgentRiskProfileService()


def test_01_build_low_risk_profile(service: AgentRiskProfileService) -> None:
    """1. Test building low risk profile for high trust score."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    res = service.build_risk_profile(
        tenant_id=tenant_id,
        agent_id=agent_id,
        trust_score=Decimal("0.90"),
    )

    assert res.risk_level == "LOW"
    assert len(res.risk_factors) == 0


def test_02_build_critical_risk_profile(service: AgentRiskProfileService) -> None:
    """2. Test CRITICAL severity risk factor promotes risk level to CRITICAL."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    factor = RiskFactor(
        code="AMOUNT_MISMATCH",
        severity="CRITICAL",
        source="INTENT",
    )

    res = service.build_risk_profile(
        tenant_id=tenant_id,
        agent_id=agent_id,
        trust_score=Decimal("0.80"),
        risk_factors=[factor],
    )

    assert res.risk_level == "CRITICAL"
