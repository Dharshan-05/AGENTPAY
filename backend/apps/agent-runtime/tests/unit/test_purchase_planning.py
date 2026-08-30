"""Unit and Security Tests for Purchase Planning Subsystem (Phase 180)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.purchase_planning_service import PurchasePlanningService
from app.domain.exceptions.agent_exceptions import ProductValidationError
from app.infrastructure.database.models.product import Product
from app.schemas.inventory import InventoryValidationResponse
from app.schemas.offer_optimization import OfferOptimizationResponse
from app.schemas.purchase_planning import (
    PurchasePlanCreateRequest,
    PurchasePlanItemRequest,
)


@pytest.fixture
def service() -> PurchasePlanningService:
    service = PurchasePlanningService()
    service.repository.get_by_id = AsyncMock()  # type: ignore[method-assign]
    service.inventory_service.validate_inventory = AsyncMock()  # type: ignore[method-assign]
    service.offer_opt_service.optimize_offer = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_duplicate_product_rejected(
    service: PurchasePlanningService,
) -> None:
    """1. Test duplicate product_id in plan items raises ProductValidationError."""
    tenant_id = uuid.uuid4()
    p1_id = uuid.uuid4()
    mock_db = MagicMock()

    req = PurchasePlanCreateRequest(
        items=[
            PurchasePlanItemRequest(product_id=p1_id, quantity=Decimal("1.000")),
            PurchasePlanItemRequest(product_id=p1_id, quantity=Decimal("2.000")),
        ]
    )

    with pytest.raises(ProductValidationError):
        await service.create_purchase_plan(mock_db, tenant_id, req)


@pytest.mark.asyncio
async def test_02_create_purchase_plan_success(
    service: PurchasePlanningService,
) -> None:
    """2. Test creation of purchase plan with pricing and snapshot metadata."""
    tenant_id = uuid.uuid4()
    merchant_id = uuid.uuid4()
    p1_id = uuid.uuid4()

    product = Product(
        id=p1_id,
        tenant_id=tenant_id,
        merchant_id=merchant_id,
        name="Laptop",
        sku="LAP-01",
        price=Decimal("1000.00"),
        currency_code="USD",
        status="active",
    )
    service.repository.get_by_id.return_value = product  # type: ignore[attr-defined]

    service.inventory_service.validate_inventory.return_value = (  # type: ignore[attr-defined]
        InventoryValidationResponse(tenant_id=tenant_id, all_valid=True, results=[])
    )

    service.offer_opt_service.optimize_offer.return_value = OfferOptimizationResponse(  # type: ignore[attr-defined]  # noqa: E501
        tenant_id=tenant_id,
        product_id=p1_id,
        quantity=Decimal("1.000"),
        has_applicable_offer=False,
        optimized_offer=None,
    )

    mock_db = MagicMock()
    # Mock return None for existing plan replay check
    mock_db.execute.return_value.scalars.return_value.first.return_value = None

    req = PurchasePlanCreateRequest(
        items=[PurchasePlanItemRequest(product_id=p1_id, quantity=Decimal("1.000"))]
    )

    res = await service.create_purchase_plan(mock_db, tenant_id, req)
    assert res.total_amount == Decimal("1000.0000")
    assert res.currency_code == "USD"
    assert len(res.items) == 1
    assert res.items[0].product_id == p1_id
