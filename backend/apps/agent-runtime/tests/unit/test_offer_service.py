"""Unit and Security Tests for Commercial Offer Service (Phase 178)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.offer_service import OfferService
from app.infrastructure.database.models.offer import Offer
from app.infrastructure.database.models.product import Product


@pytest.fixture
def service() -> OfferService:
    service = OfferService()
    service.repository.get_by_id = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_active_offer_evaluation_success(service: OfferService) -> None:
    """1. Test evaluation of an active, valid commercial offer with Decimal discount math."""  # noqa: E501
    tenant_id = uuid.uuid4()
    merchant_id = uuid.uuid4()
    product_id = uuid.uuid4()

    product = Product(
        id=product_id,
        tenant_id=tenant_id,
        merchant_id=merchant_id,
        name="Smart Watch",
        sku="WATCH-01",
        price=Decimal("299.99"),
        currency_code="USD",
        status="active",
    )
    service.repository.get_by_id.return_value = product  # type: ignore[attr-defined]

    now = datetime.now(UTC)
    offer = Offer(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        merchant_id=merchant_id,
        product_id=product_id,
        name="Summer Promo Deal",
        slug="summer-promo-deal",
        price=Decimal("249.99"),
        currency_code="USD",
        status="active",
        starts_at=now - timedelta(days=1),
        ends_at=now + timedelta(days=30),
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = [offer]

    res = await service.get_product_offers(mock_db, tenant_id, product_id)
    assert res.total_count == 1
    assert res.offers[0].discounted_price == Decimal("249.99")
    assert res.offers[0].discount_amount == Decimal("50.00")
    assert res.offers[0].currency_code == "USD"


@pytest.mark.asyncio
async def test_02_currency_mismatch_offer_ignored(service: OfferService) -> None:
    """2. Test offer with currency mismatch is safely ignored."""
    tenant_id = uuid.uuid4()
    product_id = uuid.uuid4()

    product = Product(
        id=product_id,
        tenant_id=tenant_id,
        merchant_id=uuid.uuid4(),
        name="Monitor",
        sku="MON-01",
        price=Decimal("199.99"),
        currency_code="USD",
        status="active",
    )
    service.repository.get_by_id.return_value = product  # type: ignore[attr-defined]

    offer = Offer(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        merchant_id=product.merchant_id,
        product_id=product_id,
        name="EUR Promo",
        slug="eur-promo",
        price=Decimal("150.00"),
        currency_code="EUR",  # Currency mismatch (EUR vs USD)
        status="active",
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = [offer]

    res = await service.get_product_offers(mock_db, tenant_id, product_id)
    assert res.total_count == 0
