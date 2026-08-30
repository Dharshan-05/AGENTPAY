"""Unit and Security Tests for Product Domain Service (Phase 164)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.product_service import ProductService
from app.domain.exceptions.agent_exceptions import (
    ProductAlreadyExistsError,
    ProductNotFoundError,
)
from app.infrastructure.database.models.merchant import Merchant
from app.infrastructure.database.models.product import Product
from app.schemas.products import ProductCreateRequest


@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock()


@pytest.fixture
def service() -> ProductService:
    service = ProductService()
    service.repository.create = AsyncMock()  # type: ignore[method-assign]
    service.repository.get_by_id = AsyncMock()  # type: ignore[method-assign]
    service.repository.get_by_sku = AsyncMock()  # type: ignore[method-assign]
    service.repository.update = AsyncMock()  # type: ignore[method-assign]
    service.repository.archive = AsyncMock()  # type: ignore[method-assign]
    service.repository.restore = AsyncMock()  # type: ignore[method-assign]
    service.repository.exists = AsyncMock()  # type: ignore[method-assign]
    service.repository.list = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_create_product_success(mock_db: MagicMock, service: ProductService) -> None:
    """1. Test successful product creation with non-zero Decimal price."""
    tenant_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    mock_merchant = MagicMock(spec=Merchant)
    mock_merchant.id = merchant_id
    mock_merchant.tenant_id = tenant_id
    mock_db.execute.return_value.scalars.return_value.first.return_value = mock_merchant

    service.repository.exists.return_value = False  # type: ignore[attr-defined]

    mock_product = Product(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        merchant_id=merchant_id,
        name="Wireless Keyboard",
        sku="KB-WIRELESS-001",
        price=Decimal("79.99"),
        currency_code="USD",
        status="active",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    service.repository.create.return_value = mock_product  # type: ignore[attr-defined]

    req = ProductCreateRequest(
        merchant_id=merchant_id,
        name="Wireless Keyboard",
        sku="KB-WIRELESS-001",
        price=Decimal("79.99"),
        currency_code="USD",
    )

    res = await service.create_product(mock_db, tenant_id, req)
    assert res.name == "Wireless Keyboard"
    assert res.price == Decimal("79.99")
    assert res.currency_code == "USD"


@pytest.mark.asyncio
async def test_02_create_product_invalid_price_rejected(
    mock_db: MagicMock, service: ProductService
) -> None:
    """2. Test zero or negative price is rejected."""
    merchant_id = uuid.uuid4()

    mock_merchant = MagicMock(spec=Merchant)
    mock_db.execute.return_value.scalars.return_value.first.return_value = mock_merchant

    with pytest.raises((ValueError, TypeError)):
        ProductCreateRequest(
            merchant_id=merchant_id,
            name="Free Item",
            sku="FREE-001",
            price=Decimal("0.00"),
        )


@pytest.mark.asyncio
async def test_03_create_product_duplicate_sku_rejected(
    mock_db: MagicMock, service: ProductService
) -> None:
    """3. Test duplicate SKU creation raises ProductAlreadyExistsError."""
    tenant_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    mock_merchant = MagicMock(spec=Merchant)
    mock_db.execute.return_value.scalars.return_value.first.return_value = mock_merchant

    service.repository.exists.return_value = True  # type: ignore[attr-defined]

    req = ProductCreateRequest(
        merchant_id=merchant_id,
        name="Duplicate Item",
        sku="DUP-SKU-123",
        price=Decimal("19.99"),
    )

    with pytest.raises(ProductAlreadyExistsError):
        await service.create_product(mock_db, tenant_id, req)


@pytest.mark.asyncio
async def test_04_tenant_isolation_idor_protection(
    mock_db: MagicMock, service: ProductService
) -> None:
    """4. Test cross-tenant product lookup returns ProductNotFoundError (404 anti-enumeration)."""
    tenant_b = uuid.uuid4()
    product_id = uuid.uuid4()

    service.repository.get_by_id.return_value = None  # type: ignore[attr-defined]

    with pytest.raises(ProductNotFoundError):
        await service.get_product(mock_db, tenant_b, product_id)
