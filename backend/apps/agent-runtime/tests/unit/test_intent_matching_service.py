"""Unit and Security Tests for Intent Matching Engine (Phase 198)."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.application.services.intent_matching_service import IntentMatchingService
from app.schemas.intent_matching import IntentMatchRequest
from app.schemas.intent_verification import DeclaredIntent


@pytest.fixture
def service() -> IntentMatchingService:
    return IntentMatchingService()


def test_01_exact_intent_match(service: IntentMatchingService) -> None:
    """1. Test all signals matching returns EXACT_MATCH and score 1.00."""
    merchant_id = str(uuid.uuid4())
    intent = DeclaredIntent(
        action="payment",
        amount=Decimal("100.00"),
        currency="USD",
        merchant_slug=merchant_id,
        category="electronics",
    )

    req = IntentMatchRequest(
        declared_intent=intent,
        requested_action="pay",
        requested_amount=Decimal("50.00"),
        requested_currency="USD",
        requested_merchant_id=merchant_id,
        requested_category="electronics",
    )

    res = service.match_intent(req)
    assert res.overall_match == "EXACT_MATCH"
    assert res.match_score == Decimal("1.00")
    assert len(res.signals) == 5


def test_02_financial_mismatch_caps_score_at_zero(
    service: IntentMatchingService,
) -> None:
    """2. Test financial mismatch (currency) caps match_score at 0.00 and status MISMATCH."""
    intent = DeclaredIntent(
        action="payment",
        amount=Decimal("100.00"),
        currency="USD",
    )

    req = IntentMatchRequest(
        declared_intent=intent,
        requested_action="pay",
        requested_amount=Decimal("50.00"),
        requested_currency="EUR",
    )

    res = service.match_intent(req)
    assert res.overall_match == "MISMATCH"
    assert res.match_score == Decimal("0.00")
