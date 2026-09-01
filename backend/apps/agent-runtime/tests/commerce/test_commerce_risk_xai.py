"""Unit Tests for FraudGuard Commerce Risk & XAI Explainability (Buildathon Track 01)."""

from decimal import Decimal
import pytest

from app.commerce.providers.online_search_provider import OnlineProductSearchProvider
from app.commerce.services.commerce_risk_service import CommerceRiskService


@pytest.mark.asyncio
async def test_commerce_risk_service_xai_explainability():
    """Verify FraudGuard returns numerical risk score (0-100), risk level, and human-readable XAI signals."""
    provider = OnlineProductSearchProvider()
    risk_service = CommerceRiskService()

    product = await provider.get_product_details("prod_lenovo_ideapad_slim3")
    assert product is not None

    assessment = risk_service.evaluate_commerce_risk(
        product=product,
        requested_amount=Decimal("47990.00"),
    )

    assert 0.0 <= assessment.risk_score <= 100.0
    assert assessment.risk_level in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert assessment.confidence == 0.96
    assert len(assessment.risk_factors) > 0
    assert assessment.is_transaction_allowed is True
