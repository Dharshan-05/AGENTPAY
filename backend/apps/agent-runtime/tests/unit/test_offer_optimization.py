"""Unit and Security Tests for Offer Optimization Subsystem (Phase 179)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.offer_optimization_service import OfferOptimizationService
from app.domain.exceptions.agent_exceptions import ProductValidationError
from app.schemas.offers import OfferItem, OfferListResponse


@pytest.fixture
def service() -> OfferOptimizationService:
    service = OfferOptimizationService()
    service.offer_service.get_product_offers = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_invalid_quantity_rejected(
    service: OfferOptimizationService,
) -> None:
    """1. Test non-positive quantity raises ProductValidationError."""
    tenant_id = uuid.uuid4()
    product_id = uuid.uuid4()
    mock_db = MagicMock()

    with pytest.raises(ProductValidationError):
        await service.optimize_offer(mock_db, tenant_id, product_id, quantity=Decimal("0.000"))


@pytest.mark.asyncio
async def test_02_best_offer_selection_and_tie_breaking(
    service: OfferOptimizationService,
) -> None:
    """2. Test selection of offer producing greatest savings with deterministic tie-breaking."""  # noqa: E501
    tenant_id = uuid.uuid4()
    product_id = uuid.uuid4()
    merchant_id = uuid.uuid4()
    o1_id = uuid.uuid4()
    o2_id = uuid.uuid4()

    o1 = OfferItem(
        offer_id=o1_id,
        tenant_id=tenant_id,
        merchant_id=merchant_id,
        product_id=product_id,
        name="Offer 1 ($10 off)",
        slug="offer-1",
        status="active",
        original_price=Decimal("100.00"),
        discounted_price=Decimal("90.00"),
        discount_amount=Decimal("10.00"),
        currency_code="USD",
    )

    o2 = OfferItem(
        offer_id=o2_id,
        tenant_id=tenant_id,
        merchant_id=merchant_id,
        product_id=product_id,
        name="Offer 2 ($25 off)",
        slug="offer-2",
        status="active",
        original_price=Decimal("100.00"),
        discounted_price=Decimal("75.00"),
        discount_amount=Decimal("25.00"),
        currency_code="USD",
    )

    service.offer_service.get_product_offers.return_value = OfferListResponse(  # type: ignore[attr-defined]  # noqa: E501
        tenant_id=tenant_id,
        product_id=product_id,
        total_count=2,
        offers=[o1, o2],
    )

    mock_db = MagicMock()
    res = await service.optimize_offer(mock_db, tenant_id, product_id, quantity=Decimal("1.000"))
    assert res.has_applicable_offer is True
    assert res.optimized_offer is not None
    assert res.optimized_offer.offer_id == o2_id
    assert res.optimized_offer.discount_amount == Decimal("25.0000")
