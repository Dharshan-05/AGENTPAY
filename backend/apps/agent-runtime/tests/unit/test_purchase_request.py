"""Unit and Security Tests for Purchase Request Subsystem (Phase 181)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.purchase_request_service import PurchaseRequestService
from app.infrastructure.database.models.product import Product
from app.infrastructure.database.models.purchase_plan import PurchasePlan
from app.schemas.inventory import InventoryValidationResponse
from app.schemas.offer_optimization import OfferOptimizationResponse
from app.schemas.purchase_request import PurchaseRequestCreateRequest


@pytest.fixture
def service() -> PurchaseRequestService:
    service = PurchaseRequestService()
    service.repository.get_by_id = AsyncMock()  # type: ignore[method-assign]
    service.inventory_service.validate_inventory = AsyncMock()  # type: ignore[method-assign]
    service.offer_opt_service.optimize_offer = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_create_purchase_request_ready(
    service: PurchaseRequestService,
) -> None:
    """1. Test purchase request creation for plan under approval threshold."""
    tenant_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    p1_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    plan = PurchasePlan(
        id=plan_id,
        tenant_id=tenant_id,
        purchase_intent_id=uuid.uuid4(),
        merchant_id=merchant_id,
        agent_id=uuid.uuid4(),
        product_id=p1_id,
        plan_reference="plan_test_01",
        status="validated",
        quantity=Decimal("1.000"),
        unit_price=Decimal("100.00"),
        subtotal=Decimal("100.00"),
        total_amount=Decimal("100.00"),
        currency_code="USD",
        plan_metadata={
            "snapshot_items": [
                {
                    "product_id": str(p1_id),
                    "merchant_id": str(merchant_id),
                    "sku": "LAP-01",
                    "name": "Laptop",
                    "unit_price": "100.00",
                    "quantity": "1.000",
                    "discount_amount": "0.00",
                    "line_total": "100.00",
                    "currency_code": "USD",
                }
            ]
        },
    )

    product = Product(
        id=p1_id,
        tenant_id=tenant_id,
        merchant_id=merchant_id,
        name="Laptop",
        sku="LAP-01",
        price=Decimal("100.00"),
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
    mock_db.execute.return_value.scalars.return_value.first.return_value = plan

    req = PurchaseRequestCreateRequest(purchase_plan_id=plan_id)
    res = await service.create_purchase_request(mock_db, tenant_id, req)
    assert res.status == "READY_FOR_EXECUTION"
    assert res.requires_approval is False
    assert res.total_amount == Decimal("100.00")


@pytest.mark.asyncio
async def test_02_create_purchase_request_requires_approval(
    service: PurchaseRequestService,
) -> None:
    """2. Test purchase request creation exceeding $500 threshold requires approval."""
    tenant_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    p1_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    plan = PurchasePlan(
        id=plan_id,
        tenant_id=tenant_id,
        purchase_intent_id=uuid.uuid4(),
        merchant_id=merchant_id,
        agent_id=uuid.uuid4(),
        product_id=p1_id,
        plan_reference="plan_test_02",
        status="validated",
        quantity=Decimal("1.000"),
        unit_price=Decimal("1200.00"),
        subtotal=Decimal("1200.00"),
        total_amount=Decimal("1200.00"),
        currency_code="USD",
        plan_metadata={
            "snapshot_items": [
                {
                    "product_id": str(p1_id),
                    "merchant_id": str(merchant_id),
                    "sku": "LAP-PRO",
                    "name": "Laptop Pro",
                    "unit_price": "1200.00",
                    "quantity": "1.000",
                    "discount_amount": "0.00",
                    "line_total": "1200.00",
                    "currency_code": "USD",
                }
            ]
        },
    )

    product = Product(
        id=p1_id,
        tenant_id=tenant_id,
        merchant_id=merchant_id,
        name="Laptop Pro",
        sku="LAP-PRO",
        price=Decimal("1200.00"),
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
    mock_db.execute.return_value.scalars.return_value.first.return_value = plan

    req = PurchaseRequestCreateRequest(purchase_plan_id=plan_id)
    res = await service.create_purchase_request(mock_db, tenant_id, req)
    assert res.status == "PENDING_APPROVAL"
    assert res.requires_approval is True
    assert res.total_amount == Decimal("1200.00")
