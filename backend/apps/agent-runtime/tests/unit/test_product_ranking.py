"""Unit and Security Tests for Product Ranking Subsystem (Phase 173)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.application.services.product_ranking_service import ProductRankingService
from app.domain.exceptions.agent_exceptions import ProductValidationError
from app.infrastructure.database.models.product import Product


@pytest.fixture
def service() -> ProductRankingService:
    return ProductRankingService()


@pytest.mark.asyncio
async def test_01_empty_query_rejected(service: ProductRankingService) -> None:
    """1. Test empty ranking query raises ProductValidationError."""
    tenant_id = uuid.uuid4()
    mock_db = MagicMock()

    with pytest.raises(ProductValidationError):
        await service.rank_products(mock_db, tenant_id, "")


@pytest.mark.asyncio
async def test_02_rank_products_execution(service: ProductRankingService) -> None:
    """2. Test multi-signal product ranking computation and explainable reasons."""
    tenant_id = uuid.uuid4()
    p1 = Product(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        merchant_id=uuid.uuid4(),
        name="Noise Cancelling Wireless Earbuds",
        sku="EARBUDS-01",
        description="High quality Bluetooth earbuds with deep bass",
        price=Decimal("99.99"),
        currency_code="USD",
        status="active",
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = [p1]

    res = await service.rank_products(mock_db, tenant_id, "wireless earbuds")
    assert res.total_count == 1
    assert res.results[0].sku == "EARBUDS-01"
    assert 0.0 <= res.results[0].ranking_score <= 1.0
    assert len(res.results[0].ranking_reasons) > 0
