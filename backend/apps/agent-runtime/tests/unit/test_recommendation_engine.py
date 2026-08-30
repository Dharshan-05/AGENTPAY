"""Unit and Security Tests for Recommendation Engine Subsystem (Phase 174)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.recommendation_service import RecommendationService
from app.infrastructure.database.models.product import Product


@pytest.fixture
def service() -> RecommendationService:
    service = RecommendationService()
    service.repository.get_by_id = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_recommendation_self_exclusion_and_deduplication(
    service: RecommendationService,
) -> None:
    """1. Test self-product exclusion and candidate deduplication in recommendations."""
    tenant_id = uuid.uuid4()
    target_id = uuid.uuid4()
    p_other_id = uuid.uuid4()

    target_prod = Product(
        id=target_id,
        tenant_id=tenant_id,
        merchant_id=uuid.uuid4(),
        name="Mechanical Keyboard",
        sku="KB-01",
        description="RGB Mechanical Keyboard",
        price=Decimal("129.99"),
        status="active",
    )
    other_prod = Product(
        id=p_other_id,
        tenant_id=tenant_id,
        merchant_id=uuid.uuid4(),
        name="Gaming Mouse",
        sku="MOUSE-01",
        description="High DPI Gaming Mouse",
        price=Decimal("59.99"),
        status="active",
    )

    service.repository.get_by_id.return_value = target_prod  # type: ignore[attr-defined]

    mock_db = MagicMock()
    # Mock DB returns both target_prod and other_prod
    mock_db.execute.return_value.scalars.return_value.all.return_value = [
        target_prod,
        other_prod,
        other_prod,  # Duplicate in candidate stream
    ]

    res = await service.get_recommendations(
        mock_db, tenant_id, target_product_id=target_id, limit=5
    )
    assert res.total_count == 1
    assert res.results[0].product_id == p_other_id
    assert res.results[0].product_id != target_id
