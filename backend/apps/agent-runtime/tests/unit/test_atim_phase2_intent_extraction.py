"""Unit tests for ATIM Phase 2: Intelligent Intent & Constraint Extraction."""

from __future__ import annotations

from decimal import Decimal
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.services.atim_constraint_engine import ATIMConstraintEngine
from app.application.services.llm_intent_extractor_provider import LLMIntentExtractorProvider
from app.schemas.atim import ATIMConstraint, ATIMProposedIntent


def test_simple_payment_extraction_and_normalization():
    """Test standard payment intent extraction and currency/amount normalization."""
    engine = ATIMConstraintEngine()
    raw = ATIMProposedIntent(
        intent_id=uuid.uuid4(),
        action="PAYMENT",
        amount=Decimal("65000.00"),
        currency="INR",
        merchant="Amazon",
    )
    norm = engine.normalize_intent(raw)
    assert norm.amount == Decimal("65000.00")
    assert norm.currency == "INR"
    assert norm.merchant == "amazon"
    assert norm.confidence_level == "HIGH_CONFIDENCE"
    assert norm.is_ambiguous is False


def test_product_and_brand_extraction_with_price_constraint():
    """Test extraction of product, brand, and max_price constraint (e.g. Logitech keyboard < ₹5000)."""
    engine = ATIMConstraintEngine()
    raw = ATIMProposedIntent(
        intent_id=uuid.uuid4(),
        action="PRODUCT_SEARCH",
        product="Logitech keyboard",
        brand="Logitech",
        amount=Decimal("5000.00"),
        currency="INR",
        constraints=[
            ATIMConstraint(name="max_price", operator="lte", value=5000.0),
            ATIMConstraint(name="min_rating", operator="gte", value=4.5),
        ],
    )
    norm = engine.normalize_intent(raw)
    assert norm.brand == "Logitech"
    assert norm.product == "Logitech keyboard"
    assert len(norm.constraints) == 2
    c_map = {c.name: c for c in norm.constraints}
    assert c_map["max_price"].value == 5000.0
    assert c_map["max_price"].is_security_authoritative is True
    assert c_map["min_rating"].value == 4.5


def test_quantity_extraction():
    """Test extraction of quantity constraint (e.g., 'three laptops')."""
    engine = ATIMConstraintEngine()
    raw = ATIMProposedIntent(
        intent_id=uuid.uuid4(),
        action="PRODUCT_SEARCH",
        product="laptop",
        quantity=3,
        constraints=[ATIMConstraint(name="quantity", operator="eq", value=3)],
    )
    norm = engine.normalize_intent(raw)
    assert norm.quantity == 3
    assert norm.constraints[0].value == 3


def test_negation_and_exclusions_extraction():
    """Test negation handling (e.g. 'Do not buy refurbished products', 'Don't use Amazon')."""
    raw = ATIMProposedIntent(
        intent_id=uuid.uuid4(),
        action="PRODUCT_SEARCH",
        product="laptop",
        negations=["refurbished", "amazon"],
    )
    assert "refurbished" in raw.negations
    assert "amazon" in raw.negations


def test_temporal_language_extraction():
    """Test temporal phrase extraction (e.g., 'yesterday', 'this month')."""
    raw = ATIMProposedIntent(
        intent_id=uuid.uuid4(),
        action="REFUND",
        amount=Decimal("150.00"),
        temporal_constraint="yesterday",
    )
    assert raw.temporal_constraint == "yesterday"


def test_conditional_purchase_and_multi_intent_extraction():
    """Test multi-intent decomposition (SEARCH + FILTER + COMPARE + PURCHASE)."""
    raw = ATIMProposedIntent(
        intent_id=uuid.uuid4(),
        action="PRODUCT_SEARCH",
        product="keyboard",
        sub_intents=["SEARCH", "FILTER", "CONDITION", "PURCHASE"],
        conditions=["final_price_includes_shipping"],
        optimization="MIN_PRICE",
    )
    engine = ATIMConstraintEngine()
    norm = engine.normalize_intent(raw)
    assert norm.optimization == "MIN_PRICE"
    assert "PURCHASE" in norm.sub_intents
    assert "final_price_includes_shipping" in norm.conditions


def test_ambiguous_request_handling_vague_target():
    """Test vague prompt 'Buy me something good' triggers ambiguity fail-closed."""
    engine = ATIMConstraintEngine()
    raw = ATIMProposedIntent(
        intent_id=uuid.uuid4(),
        action="PAYMENT",
        target="something good",
        amount=None,
        merchant=None,
    )
    norm = engine.normalize_intent(raw)
    assert norm.is_ambiguous is True
    assert norm.confidence_level == "AMBIGUOUS"
    assert norm.confidence <= Decimal("0.40")
    assert "amount" in norm.missing_fields


def test_ambiguous_request_missing_amount_and_merchant():
    """Test request missing mandatory financial fields is marked ambiguous."""
    engine = ATIMConstraintEngine()
    raw = ATIMProposedIntent(
        intent_id=uuid.uuid4(),
        action="PAYMENT",
        amount=None,
        merchant=None,
    )
    norm = engine.normalize_intent(raw)
    assert norm.is_ambiguous is True
    assert norm.confidence_level == "AMBIGUOUS"


@pytest.mark.asyncio
async def test_llm_extractor_fallback_on_malformed_llm_output():
    """Test that provider failure or invalid output triggers fallback to rule engine."""
    mock_router = MagicMock()
    mock_router.generate_structured = AsyncMock(side_effect=Exception("LLM Timeout or Invalid JSON"))

    provider = LLMIntentExtractorProvider(router=mock_router)
    res = await provider.extract("Pay $150 to merchant cloud_services", {})

    assert res.action.upper() == "PAYMENT"
    assert res.entities.amount == Decimal("150")
    assert res.entities.currency == "USD"
    assert res.source == "rule_based_provider"
