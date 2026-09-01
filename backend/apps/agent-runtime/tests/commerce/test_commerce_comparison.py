"""Unit Tests for Product Comparison Engine (Buildathon Track 01)."""

from decimal import Decimal
import pytest

from app.commerce.providers.online_search_provider import OnlineProductSearchProvider
from app.commerce.services.product_comparison_service import ProductComparisonService


@pytest.mark.asyncio
async def test_product_comparison_matrix_generation():
    """Verify multi-factor product comparison across Price, Specs, Value, and Risk."""
    provider = OnlineProductSearchProvider()
    service = ProductComparisonService()

    products = await provider.search_products("laptop", max_price=Decimal("50000.00"), limit=3)
    assert len(products) >= 2

    matrix = service.compare_products(products=products, user_purpose="CODING", budget=Decimal("50000.00"))

    assert matrix.best_overall_id is not None
    assert matrix.best_value_id is not None
    assert matrix.best_performance_id is not None
    assert matrix.lowest_risk_id is not None
    assert len(matrix.scores) == len(products)
    assert "Evaluated" in matrix.comparison_summary or "Compared" in matrix.comparison_summary

    for score in matrix.scores:
        assert 0.0 <= score.overall_score <= 100.0
        assert 0.0 <= score.value_score <= 100.0
        assert 0.0 <= score.performance_score <= 100.0
