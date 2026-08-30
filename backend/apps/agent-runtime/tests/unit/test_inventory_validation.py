"""Unit and Security Tests for Inventory Validation Subsystem (Phase 177)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.inventory_validation_service import InventoryValidationService
from app.domain.exceptions.agent_exceptions import ProductValidationError
from app.schemas.inventory import InventoryCheckResult, InventoryValidationItem


@pytest.fixture
def service() -> InventoryValidationService:
    service = InventoryValidationService()
    service.check_service.check_inventory = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_bulk_validation_limit_exceeded(
    service: InventoryValidationService,
) -> None:
    """1. Test bulk validation list exceeding maximum 50 items raises ProductValidationError."""  # noqa: E501
    tenant_id = uuid.uuid4()
    mock_db = MagicMock()

    items = [
        InventoryValidationItem(product_id=uuid.uuid4(), requested_quantity=Decimal("1.000"))
        for _ in range(51)
    ]

    with pytest.raises(ProductValidationError):
        await service.validate_inventory(mock_db, tenant_id, items)


@pytest.mark.asyncio
async def test_02_advisory_validation_result(
    service: InventoryValidationService,
) -> None:
    """2. Test advisory read-only inventory validation results."""
    tenant_id = uuid.uuid4()
    p1_id = uuid.uuid4()

    item = InventoryValidationItem(product_id=p1_id, requested_quantity=Decimal("2.000"))

    service.check_service.check_inventory.return_value = InventoryCheckResult(  # type: ignore[attr-defined]  # noqa: E501
        product_id=p1_id,
        requested_quantity=Decimal("2.000"),
        available_quantity=Decimal("5.000"),
        is_available=True,
        inventory_status="AVAILABLE",
    )

    mock_db = MagicMock()
    res = await service.validate_inventory(mock_db, tenant_id, [item])
    assert res.all_valid is True
    assert len(res.results) == 1
    assert res.results[0].reason == "VALID"
