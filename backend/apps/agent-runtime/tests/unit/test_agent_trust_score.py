"""Unit and Security Tests for Agent Trust Score Foundation (Phase 206)."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.application.services.agent_trust_score_service import AgentTrustScoreService


@pytest.fixture
def service() -> AgentTrustScoreService:
    return AgentTrustScoreService()


def test_01_create_trust_score_normal(service: AgentTrustScoreService) -> None:
    """1. Test creating a normal trust score."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    res = service.create_trust_score(
        tenant_id=tenant_id,
        agent_id=agent_id,
        trust_score=Decimal("0.75"),
    )

    assert res.trust_score == Decimal("0.75")
    assert res.trust_state == "NORMAL"


def test_02_trust_score_clamping(service: AgentTrustScoreService) -> None:
    """2. Test trust score clamping to range [0.00, 1.00]."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    res_high = service.create_trust_score(tenant_id, agent_id, Decimal("1.50"))
    assert res_high.trust_score == Decimal("1.00")
    assert res_high.trust_state == "TRUSTED"

    res_low = service.create_trust_score(tenant_id, agent_id, Decimal("-0.50"))
    assert res_low.trust_score == Decimal("0.00")
    assert res_low.trust_state == "UNTRUSTED"
