"""Unit tests for ATIMConstraintEngine."""

from __future__ import annotations

from decimal import Decimal
import uuid

from app.application.services.atim_constraint_engine import ATIMConstraintEngine
from app.schemas.atim import ATIMConstraint, ATIMProposedIntent


def test_atim_constraint_engine_currency_and_amount_normalization():
    """Test normalizing currency code, decimal amount, and merchant slug."""
    engine = ATIMConstraintEngine()
    raw = ATIMProposedIntent(
        intent_id=uuid.uuid4(),
        action="PAYMENT",
        amount=Decimal("65000.555"),
        currency="inr",
        merchant=" Amazon.in! ",
        category="ELECTRONICS",
        constraints=[
            ATIMConstraint(name="max_price", operator="lte", value="65000.00"),
            ATIMConstraint(name="min_rating", operator="gte", value="4.5"),
        ],
    )

    norm = engine.normalize_intent(raw)

    assert norm.currency == "INR"
    assert norm.amount == Decimal("65000.56")
    assert norm.merchant == "amazonin"
    assert norm.category == "electronics"
    assert len(norm.constraints) == 2
    assert norm.constraints[0].is_security_authoritative is True
    assert norm.constraints[1].is_security_authoritative is False


def test_atim_constraint_engine_rejects_negative_amount():
    """Test constraint engine resets negative monetary amount to None."""
    engine = ATIMConstraintEngine()
    raw = ATIMProposedIntent(
        intent_id=uuid.uuid4(),
        action="PAYMENT",
        amount=Decimal("-500.00"),
        currency="USD",
    )

    norm = engine.normalize_intent(raw)

    assert norm.amount is None
