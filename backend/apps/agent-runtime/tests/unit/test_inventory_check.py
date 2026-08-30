"""Unit and Security Tests for Inventory Check Subsystem (Phase 176)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.inventory_check_service import InventoryCheckService
from app.domain.exceptions.agent_exceptions import ProductValidationError
from app.infrastructure.database.models.inventory import Inventory
from app.infrastructure.database.models.product import Product


@pytest.fixture
def service() -> InventoryCheckService:
    service = InventoryCheckService()
    service.repository.get_by_id = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_invalid_quantity_rejected(service: InventoryCheckService) -> None:
    """1. Test zero or negative requested quantity raises ProductValidationError."""
    tenant_id = uuid.uuid4()
    product_id = uuid.uuid4()
    mock_db = MagicMock()

    with pytest.raises(ProductValidationError):
        await service.check_inventory(
            mock_db, tenant_id, product_id, requested_quantity=Decimal("0.000")
        )

    with pytest.raises(ProductValidationError):
        await service.check_inventory(
            mock_db, tenant_id, product_id, requested_quantity=Decimal("-5.000")
        )


@pytest.mark.asyncio
async def test_02_inventory_check_available_and_unknown(
    service: InventoryCheckService,
) -> None:
    """2. Test available stock check and unstocked unknown status handling."""
    tenant_id = uuid.uuid4()
    product_id = uuid.uuid4()

    product = Product(
        id=product_id,
        tenant_id=tenant_id,
        merchant_id=uuid.uuid4(),
        name="Smartphone",
        sku="PHONE-01",
        price=Decimal("699.99"),
        status="active",
    )
    service.repository.get_by_id.return_value = product  # type: ignore[attr-defined]

    inventory_record = Inventory(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        merchant_id=product.merchant_id,
        product_id=product_id,
        quantity=Decimal("10.000"),
        available_quantity=Decimal("10.000"),
        status="active",
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = inventory_record

    res = await service.check_inventory(
        mock_db, tenant_id, product_id, requested_quantity=Decimal("2.000")
    )
    assert res.is_available is True
    assert res.inventory_status == "AVAILABLE"
    assert res.available_quantity == Decimal("10.000")

    # Unstocked case
    mock_db.execute.return_value.scalars.return_value.first.return_value = None
    res_unknown = await service.check_inventory(
        mock_db, tenant_id, product_id, requested_quantity=Decimal("1.000")
    )
    assert res_unknown.is_available is False
    assert res_unknown.inventory_status == "UNKNOWN"
