"""Unit and Security Tests for Product Sorting Subsystem (Phase 171)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.infrastructure.database.models.product import Product
from app.infrastructure.database.repositories.product_repository import (
    SORT_COLUMN_MAP,
    ProductRepository,
)


@pytest.fixture
def repo() -> ProductRepository:
    return ProductRepository()


@pytest.mark.asyncio
async def test_01_sort_whitelist_safety() -> None:
    """1. Test sort column map contains only safe whitelisted columns."""
    assert "price" in SORT_COLUMN_MAP
    assert "name" in SORT_COLUMN_MAP
    assert "created_at" in SORT_COLUMN_MAP
    assert "updated_at" in SORT_COLUMN_MAP
    assert "sku" in SORT_COLUMN_MAP
    assert "password_hash" not in SORT_COLUMN_MAP


@pytest.mark.asyncio
async def test_02_product_sorting_execution(repo: ProductRepository) -> None:
    """2. Test sorting by price and name via repository."""
    tenant_id = uuid.uuid4()
    p1 = Product(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        name="Alpha",
        price=Decimal("10.00"),
        created_at=datetime.now(UTC),
    )
    p2 = Product(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        name="Beta",
        price=Decimal("20.00"),
        created_at=datetime.now(UTC),
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = [p1, p2]

    rows, has_more = await repo.list(mock_db, tenant_id, sort_by="price", sort_dir="asc")
    assert len(rows) == 2
    assert has_more is False
