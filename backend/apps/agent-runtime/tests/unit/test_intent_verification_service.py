"""Unit and Security Tests for Intent Verification Engine (Phase 197)."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.application.services.intent_verification_service import IntentVerificationService
from app.schemas.intent_verification import DeclaredIntent, IntentVerificationRequest


@pytest.fixture
def service() -> IntentVerificationService:
    return IntentVerificationService()


def test_01_valid_intent_verification_passes(
    service: IntentVerificationService,
) -> None:
    """1. Test declared intent matching requested operation returns VERIFIED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    intent = DeclaredIntent(
        action="payment",
        amount=Decimal("500.00"),
        currency="USD",
    )

    req = IntentVerificationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        declared_intent=intent,
        requested_action="pay",
        requested_amount=Decimal("300.00"),
        requested_currency="USD",
    )

    res = service.verify_intent(req)
    assert res.verified is True
    assert res.decision == "VERIFIED"
    assert res.reason_code == "INTENT_VERIFIED"
    assert res.confidence_score == Decimal("1.00")


def test_02_missing_declared_intent_fails_closed(
    service: IntentVerificationService,
) -> None:
    """2. Test missing declared intent fails closed with INSUFFICIENT."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = IntentVerificationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        declared_intent=None,
        requested_action="pay",
    )

    res = service.verify_intent(req)
    assert res.verified is False
    assert res.decision == "INSUFFICIENT"
    assert res.reason_code == "INTENT_MISSING"


def test_03_action_mismatch_denied(service: IntentVerificationService) -> None:
    """3. Test action mismatch returns MISMATCH."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    intent = DeclaredIntent(action="refund")

    req = IntentVerificationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        declared_intent=intent,
        requested_action="payment",
    )

    res = service.verify_intent(req)
    assert res.verified is False
    assert res.decision == "MISMATCH"
    assert res.reason_code == "ACTION_MISMATCH"


def test_04_amount_exceeding_declared_intent_mismatch(
    service: IntentVerificationService,
) -> None:
    """4. Test requested amount exceeding declared max intent returns AMOUNT_MISMATCH."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    intent = DeclaredIntent(action="payment", amount=Decimal("100.00"))

    req = IntentVerificationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        declared_intent=intent,
        requested_action="pay",
        requested_amount=Decimal("150.00"),
    )

    res = service.verify_intent(req)
    assert res.verified is False
    assert res.reason_code == "AMOUNT_MISMATCH"
