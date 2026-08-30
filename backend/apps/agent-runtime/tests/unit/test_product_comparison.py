"""Unit and Security Tests for Product Comparison Subsystem (Phase 172)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.product_comparison_service import ProductComparisonService
from app.domain.exceptions.agent_exceptions import (
    ProductNotFoundError,
    ProductValidationError,
)
from app.infrastructure.database.models.product import Product


@pytest.fixture
def service() -> ProductComparisonService:
    service = ProductComparisonService()
    service.repository.get_by_id = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_invalid_comparison_requests(
    service: ProductComparisonService,
) -> None:
    """1. Test single product, >5 products, or duplicate product IDs are rejected."""
    tenant_id = uuid.uuid4()
    pid1 = uuid.uuid4()
    mock_db = MagicMock()

    # < 2 products
    with pytest.raises(ProductValidationError):
        await service.compare_products(mock_db, tenant_id, [pid1])

    # > 5 products
    with pytest.raises(ProductValidationError):
        await service.compare_products(mock_db, tenant_id, [uuid.uuid4() for _ in range(6)])

    # Duplicates
    with pytest.raises(ProductValidationError):
        await service.compare_products(mock_db, tenant_id, [pid1, pid1])


@pytest.mark.asyncio
async def test_02_successful_comparison_same_currency(
    service: ProductComparisonService,
) -> None:
    """2. Test comparison of 2 active products in same currency (USD)."""
    tenant_id = uuid.uuid4()
    pid1 = uuid.uuid4()
    pid2 = uuid.uuid4()

    p1 = Product(
        id=pid1,
        tenant_id=tenant_id,
        merchant_id=uuid.uuid4(),
        name="Item A",
        sku="SKU-A",
        price=Decimal("49.99"),
        currency_code="USD",
        status="active",
    )
    p2 = Product(
        id=pid2,
        tenant_id=tenant_id,
        merchant_id=uuid.uuid4(),
        name="Item B",
        sku="SKU-B",
        price=Decimal("99.99"),
        currency_code="USD",
        status="active",
    )

    def get_by_id_side_effect(
        db: MagicMock, t_id: uuid.UUID, p_id: uuid.UUID, include_deleted: bool = False
    ) -> Product | None:  # noqa: E501
        if p_id == pid1:
            return p1
        if p_id == pid2:
            return p2
        return None

    service.repository.get_by_id.side_effect = get_by_id_side_effect  # type: ignore[attr-defined]

    res = await service.compare_products(MagicMock(), tenant_id, [pid1, pid2])
    assert len(res.products) == 2
    assert res.metrics.common_currency == "USD"
    assert res.metrics.lowest_price_product_id == pid1
    assert res.metrics.highest_price_product_id == pid2
    assert res.metrics.price_difference == Decimal("50.00")
    assert res.metrics.price_difference_available is True


@pytest.mark.asyncio
async def test_03_comparison_cross_tenant_or_missing_404(
    service: ProductComparisonService,
) -> None:
    """3. Test missing or cross-tenant product raises 404 anti-enumeration error."""
    tenant_id = uuid.uuid4()
    pid1 = uuid.uuid4()
    pid2 = uuid.uuid4()

    service.repository.get_by_id.return_value = None  # type: ignore[attr-defined]

    with pytest.raises(ProductNotFoundError):
        await service.compare_products(MagicMock(), tenant_id, [pid1, pid2])
