"""Unit & Security tests for Phase 144 — Intent Normalization."""

import uuid
from decimal import Decimal

from app.application.services.intent_normalization_service import IntentNormalizationService
from app.schemas.agents import ExtractedEntities, StructuredIntent


def test_intent_normalization_determinism() -> None:
    """Test identical input always produces identical normalized output."""
    service = IntentNormalizationService()

    intent = StructuredIntent(
        intent_id=uuid.uuid4(),
        action=" MAKE PAYMENT ",
        target=" MERCHANT ",
        entities=ExtractedEntities(
            amount=Decimal("500.25"), currency=" usd ", merchant=" acme_store "
        ),
        confidence=Decimal("0.9500"),
        source="rule_based_provider",
    )

    norm1 = service.normalize_intent(intent, intent_category="PAYMENT")
    norm2 = service.normalize_intent(intent, intent_category="PAYMENT")

    assert norm1.model_dump() == norm2.model_dump()
    assert norm1.action == "payment"
    assert norm1.entities.currency == "USD"
    assert norm1.entities.merchant == "acme_store"
    assert norm1.entities.amount == Decimal("500.25")


def test_intent_normalization_preserves_decimal_precision() -> None:
    """Test Decimal monetary amounts preserve exact precision without float conversion."""
    service = IntentNormalizationService()

    intent = StructuredIntent(
        intent_id=uuid.uuid4(),
        action="payment",
        entities=ExtractedEntities(amount=Decimal("1234567.89"), currency="INR"),
        confidence=Decimal("0.9000"),
        source="rule_based",
    )

    norm = service.normalize_intent(intent, intent_category="PAYMENT")
    assert isinstance(norm.entities.amount, Decimal)
    assert norm.entities.amount == Decimal("1234567.89")


def test_intent_normalization_does_not_invent_missing_fields() -> None:
    """Test normalization does not guess or invent missing amount or currency."""
    service = IntentNormalizationService()

    intent = StructuredIntent(
        intent_id=uuid.uuid4(),
        action="balance",
        entities=ExtractedEntities(),
        confidence=Decimal("0.9000"),
        source="rule_based",
    )

    norm = service.normalize_intent(intent, intent_category="BALANCE_QUERY")
    assert norm.action == "balance_query"
    assert norm.entities.amount is None
    assert norm.entities.currency is None
    assert norm.entities.merchant is None
