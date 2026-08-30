"""Unit and Security Tests for Intent Risk Engine (Phase 213)."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.application.services.intent_risk_service import IntentRiskService
from app.schemas.intent_risk import IntentRiskRequest


@pytest.fixture
def service() -> IntentRiskService:
    return IntentRiskService()


def test_01_no_declared_intent_returns_zero_risk(
    service: IntentRiskService,
) -> None:
    """1. Test request without declared intent returns zero risk and can_proceed = True."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = IntentRiskRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        declared_intent=None,
    )

    res = service.calculate_intent_risk(req)
    assert res.intent_risk_score == Decimal("0.00")
    assert res.can_proceed is True


def test_02_critical_intent_mismatch_fails_closed(
    service: IntentRiskService,
) -> None:
    """2. Test currency mismatch produces CRITICAL severity and can_proceed = False."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    declared = {"action": "payment", "amount": "100.00", "currency": "USD"}
    req = IntentRiskRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        declared_intent=declared,
        requested_action="payment",
        requested_amount=Decimal("100.00"),
        requested_currency="EUR",
    )

    res = service.calculate_intent_risk(req)
    assert res.can_proceed is False
    assert res.severity == "CRITICAL"
