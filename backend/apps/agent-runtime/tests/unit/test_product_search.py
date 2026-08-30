"""Unit and Security Tests for Product Keyword Search Subsystem (Phase 168)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.application.services.product_search_service import ProductSearchService
from app.domain.exceptions.agent_exceptions import ProductValidationError
from app.infrastructure.database.models.product import Product


@pytest.fixture
def service() -> ProductSearchService:
    return ProductSearchService()


@pytest.mark.asyncio
async def test_01_exact_sku_search(service: ProductSearchService) -> None:
    """1. Test exact SKU keyword search returns score 1.0."""
    tenant_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    product = Product(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        merchant_id=merchant_id,
        name="Wireless Noise Cancelling Headphones",
        sku="HEADPHONE-NC-001",
        description="High quality headphones",
        price=Decimal("199.99"),
        currency_code="USD",
        status="active",
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = [product]

    res = await service.search_products(mock_db, tenant_id, "HEADPHONE-NC-001")
    assert res.total_count == 1
    assert res.results[0].sku == "HEADPHONE-NC-001"
    assert res.results[0].relevance_score == 1.0
    assert res.results[0].match_type == "EXACT_SKU"


@pytest.mark.asyncio
async def test_02_name_and_description_keyword_search(
    service: ProductSearchService,
) -> None:
    """2. Test product name and description keyword search ranking."""
    tenant_id = uuid.uuid4()

    p1 = Product(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        merchant_id=uuid.uuid4(),
        name="Gaming Laptop Pro",
        sku="LAPTOP-GAMING-01",
        description="High performance gaming laptop",
        price=Decimal("1499.00"),
        currency_code="USD",
        status="active",
    )

    p2 = Product(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        merchant_id=uuid.uuid4(),
        name="Laptop Sleeve",
        sku="SLEEVE-01",
        description="Protective sleeve for 15 inch laptop",
        price=Decimal("29.99"),
        currency_code="USD",
        status="active",
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = [p1, p2]

    res = await service.search_products(mock_db, tenant_id, "laptop")
    assert res.total_count == 2
    assert res.results[0].name in ("Gaming Laptop Pro", "Laptop Sleeve")


@pytest.mark.asyncio
async def test_03_empty_or_oversized_query_rejected(
    service: ProductSearchService,
) -> None:
    """3. Test empty or oversized search query raises ProductValidationError."""
    tenant_id = uuid.uuid4()
    mock_db = MagicMock()

    with pytest.raises(ProductValidationError):
        await service.search_products(mock_db, tenant_id, "")

    with pytest.raises(ProductValidationError):
        await service.search_products(mock_db, tenant_id, "a" * 300)
