"""Unit and Security Tests for Product Filtering Subsystem (Phase 170)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.product_service import ProductService
from app.domain.exceptions.agent_exceptions import ProductValidationError


@pytest.fixture
def service() -> ProductService:
    service = ProductService()
    service.repository.list = AsyncMock(return_value=([], False))  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_invalid_price_range_rejected(service: ProductService) -> None:
    """1. Test negative prices or min_price > max_price raise ProductValidationError."""
    tenant_id = uuid.uuid4()
    mock_db = MagicMock()

    with pytest.raises(ProductValidationError):
        await service.list_products(mock_db, tenant_id, min_price=Decimal("-10.00"))

    with pytest.raises(ProductValidationError):
        await service.list_products(mock_db, tenant_id, max_price=Decimal("-5.00"))

    with pytest.raises(ProductValidationError):
        await service.list_products(
            mock_db, tenant_id, min_price=Decimal("100.00"), max_price=Decimal("50.00")
        )


@pytest.mark.asyncio
async def test_02_valid_filtering(service: ProductService) -> None:
    """2. Test valid filter parameter execution."""
    tenant_id = uuid.uuid4()
    merchant_id = uuid.uuid4()
    mock_db = MagicMock()

    res = await service.list_products(
        mock_db,
        tenant_id,
        merchant_id=merchant_id,
        currency="USD",
        min_price=Decimal("10.00"),
        max_price=Decimal("500.00"),
        status="active",
    )
    assert res.total_count == 0
    assert res.has_more is False
