"""Unit tests for LLMIntentExtractorProvider with fallback to RuleBasedIntentExtractorProvider."""

from __future__ import annotations

from unittest.mock import AsyncMock
from decimal import Decimal
import uuid
import pytest

from app.application.services.llm_intent_extractor_provider import LLMIntentExtractorProvider
from app.application.services.intent_extraction_service import RuleBasedIntentExtractorProvider
from app.infrastructure.llm.exceptions import LLMProviderError
from app.infrastructure.llm.router import LLMRouter
from app.infrastructure.llm.schemas import StructuredLLMResponse
from app.schemas.atim import ATIMProposedIntent


@pytest.mark.asyncio
async def test_llm_intent_extractor_success():
    """Test successful intent extraction via LLM provider."""
    mock_router = AsyncMock(spec=LLMRouter)
    mock_intent = ATIMProposedIntent(
        intent_id=uuid.uuid4(),
        action="PAYMENT",
        amount=Decimal("65000.00"),
        currency="INR",
        merchant="amazon",
    )
    mock_router.generate_structured.return_value = StructuredLLMResponse[ATIMProposedIntent](
        correlation_id=uuid.uuid4(),
        provider="mock_openai",
        model="gpt-4o-mini",
        data=mock_intent,
        raw_content="{}",
        latency_ms=20.0,
    )

    provider = LLMIntentExtractorProvider(router=mock_router)
    res = await provider.extract("Pay ₹65,000 to merchant amazon", {})

    assert res.action == "PAYMENT"
    assert res.entities.amount == Decimal("65000.00")
    assert res.entities.currency == "INR"
    assert res.entities.merchant == "amazon"


@pytest.mark.asyncio
async def test_llm_intent_extractor_fallback_on_llm_failure():
    """Test automatic fallback to RuleBasedIntentExtractorProvider when LLM fails."""
    mock_router = AsyncMock(spec=LLMRouter)
    mock_router.generate_structured.side_effect = LLMProviderError("All providers down")

    fallback_provider = RuleBasedIntentExtractorProvider()
    provider = LLMIntentExtractorProvider(router=mock_router, fallback_provider=fallback_provider)

    # Simple prompt that rule-based engine can parse
    res = await provider.extract("Pay $150 to merchant cloud_services", {})

    assert res.action.upper() == "PAYMENT"
    assert res.entities.amount == Decimal("150")
    assert res.entities.currency == "USD"
    assert res.entities.merchant == "cloud_services"

