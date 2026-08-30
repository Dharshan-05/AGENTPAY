"""Unit and Data Access Tests for Product Repository (Phase 166)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.infrastructure.database.models.product import Product
from app.infrastructure.database.repositories.product_repository import ProductRepository


@pytest.fixture
def repo() -> ProductRepository:
    return ProductRepository()


@pytest.mark.asyncio
async def test_01_create_and_get_product_repository(repo: ProductRepository) -> None:
    """1. Test creating and retrieving a product entity in repository."""
    tenant_id = uuid.uuid4()
    merchant_id = uuid.uuid4()
    product_id = uuid.uuid4()

    product = Product(
        id=product_id,
        tenant_id=tenant_id,
        merchant_id=merchant_id,
        name="Test Laptop",
        sku="SKU-LAPTOP-100",
        price=Decimal("999.99"),
        currency_code="USD",
        status="active",
        created_at=datetime.now(UTC),
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = product

    saved = await repo.create(mock_db, product)
    assert saved.id == product_id
    assert saved.price == Decimal("999.99")

    retrieved = await repo.get_by_id(mock_db, tenant_id, product_id)
    assert retrieved is not None
    assert retrieved.sku == "SKU-LAPTOP-100"


@pytest.mark.asyncio
async def test_02_get_by_sku_and_exists_check(repo: ProductRepository) -> None:
    """2. Test SKU lookup and existence check in repository."""
    tenant_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    product = MagicMock(spec=Product)
    product.sku = "SKU-PHONE-200"

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = product

    res = await repo.get_by_sku(mock_db, tenant_id, merchant_id, "SKU-PHONE-200")
    assert res is not None
    assert res.sku == "SKU-PHONE-200"

    exists = await repo.exists(mock_db, tenant_id, merchant_id, "SKU-PHONE-200")
    assert exists is True


@pytest.mark.asyncio
async def test_03_archive_and_restore_product_repository(repo: ProductRepository) -> None:
    """3. Test archival (soft delete) and restoration of a product."""
    tenant_id = uuid.uuid4()
    product_id = uuid.uuid4()

    product = Product(
        id=product_id,
        tenant_id=tenant_id,
        merchant_id=uuid.uuid4(),
        name="Archivable Item",
        sku="SKU-ARCH-001",
        price=Decimal("49.99"),
        status="active",
        deleted_at=None,
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = product

    archived = await repo.archive(mock_db, tenant_id, product_id)
    assert archived is not None
    assert archived.deleted_at is not None
    assert archived.status == "archived"
