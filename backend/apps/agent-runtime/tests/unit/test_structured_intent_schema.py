"""Unit & Security tests for Phase 142 — Structured Intent Schema."""

import uuid
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.agents import ExtractedEntities, StructuredIntent


def test_structured_intent_financial_precision() -> None:
    """Test monetary values preserve exact Decimal precision without float conversion."""
    entities = ExtractedEntities(
        amount=Decimal("1234.56"),
        currency="INR",
        merchant="acme_corp",
    )

    intent = StructuredIntent(
        intent_id=uuid.uuid4(),
        action="payment",
        target="merchant",
        entities=entities,
        confidence=Decimal("0.98"),
        source="rule_based_provider",
    )

    assert isinstance(intent.entities.amount, Decimal)
    assert intent.entities.amount == Decimal("1234.56")
    assert intent.entities.currency == "INR"


def test_structured_intent_extra_forbid() -> None:
    """Test StructuredIntent schema strictly rejects unexpected extra fields."""
    with pytest.raises(ValidationError):
        StructuredIntent.model_validate(
            {
                "intent_id": str(uuid.uuid4()),
                "action": "payment",
                "confidence": "0.90",
                "source": "rule_based",
                "unauthorized_field": "hacked_value",  # Unexpected extra field
            }
        )


def test_extracted_entities_extra_forbid() -> None:
    """Test ExtractedEntities schema strictly rejects extra fields."""
    with pytest.raises(ValidationError):
        ExtractedEntities.model_validate(
            {
                "amount": "100.00",
                "currency": "USD",
                "tenant_id": str(uuid.uuid4()),  # Security-sensitive injected field
            }
        )
