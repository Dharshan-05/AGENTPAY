"""Unit and Security Tests for Commerce Validation Subsystem (Phase 182)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.commerce_validation_service import CommerceValidationService
from app.infrastructure.database.models.product import Product
from app.infrastructure.database.models.purchase_intent import PurchaseIntent
from app.infrastructure.database.models.purchase_plan import PurchasePlan
from app.schemas.inventory import InventoryValidationResponse
from app.schemas.offer_optimization import OfferOptimizationResponse


@pytest.fixture
def service() -> CommerceValidationService:
    service = CommerceValidationService()
    service.repository.get_by_id = AsyncMock()  # type: ignore[method-assign]
    service.inventory_service.validate_inventory = AsyncMock()  # type: ignore[method-assign]
    service.offer_opt_service.optimize_offer = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_commerce_validation_success(
    service: CommerceValidationService,
) -> None:
    """1. Test successful authoritative commerce validation pipeline."""
    tenant_id = uuid.uuid4()
    req_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    p1_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    intent = PurchaseIntent(
        id=req_id,
        tenant_id=tenant_id,
        merchant_id=merchant_id,
        agent_id=uuid.uuid4(),
        product_id=p1_id,
        intent_reference="req_val_01",
        status="pending",
        quantity=Decimal("1.000"),
        unit_price=Decimal("100.00"),
        total_amount=Decimal("100.00"),
        currency_code="USD",
        intent_metadata={"purchase_plan_id": str(plan_id)},
    )

    plan = PurchasePlan(
        id=plan_id,
        tenant_id=tenant_id,
        purchase_intent_id=req_id,
        merchant_id=merchant_id,
        agent_id=intent.agent_id,
        product_id=p1_id,
        plan_reference="plan_val_01",
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
                    "sku": "ITEM-01",
                    "name": "Widget",
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
        name="Widget",
        sku="ITEM-01",
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

    def execute_side_effect(stmt: MagicMock) -> MagicMock:
        mock_scalars = MagicMock()
        stmt_str = str(stmt)
        if "purchase_intents" in stmt_str:
            mock_scalars.first.return_value = intent
        else:
            mock_scalars.first.return_value = plan
        mock_res = MagicMock()
        mock_res.scalars.return_value = mock_scalars
        return mock_res

    mock_db.execute.side_effect = execute_side_effect

    res = await service.validate_commerce_request(mock_db, tenant_id, req_id)
    assert res.valid is True
    assert res.purchase_request_id == req_id
    assert res.total == Decimal("100.00")
    assert len(res.validation_errors) == 0
