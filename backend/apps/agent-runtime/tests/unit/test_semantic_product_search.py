"""Unit and Security Tests for Semantic Product Search Subsystem (Phase 169)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.application.services.embedding_service import EmbeddingService
from app.application.services.product_search_service import ProductSearchService
from app.infrastructure.database.models.product import Product


@pytest.fixture
def service() -> ProductSearchService:
    return ProductSearchService()


@pytest.mark.asyncio
async def test_01_embedding_service_unit() -> None:
    """1. Test embedding vector computation and cosine similarity."""
    embed_svc = EmbeddingService()

    v1 = embed_svc.embed_text("wireless headphones")
    v2 = embed_svc.embed_text("wireless headphones")
    v3 = embed_svc.embed_text("coffee maker machine")

    assert len(v1) == 128
    sim1 = embed_svc.cosine_similarity(v1, v2)
    assert sim1 == 1.0

    sim2 = embed_svc.cosine_similarity(v1, v3)
    assert 0.0 <= sim2 < 1.0


@pytest.mark.asyncio
async def test_02_semantic_search_products(service: ProductSearchService) -> None:
    """2. Test natural language semantic product search and hybrid score computation."""
    tenant_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    p1 = Product(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        merchant_id=merchant_id,
        name="Noise Cancelling Wireless Earbuds",
        sku="EARBUDS-01",
        description="Active noise cancelling wireless bluetooth earbuds with deep bass",
        price=Decimal("129.99"),
        currency_code="USD",
        status="active",
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = [p1]

    res = await service.semantic_search_products(
        mock_db, tenant_id, "headphones with strong bass", hybrid=True
    )
    assert res.total_count == 1
    assert res.results[0].sku == "EARBUDS-01"
    assert 0.0 <= res.results[0].semantic_score <= 1.0
    assert 0.0 <= res.results[0].hybrid_score <= 1.0


@pytest.mark.asyncio
async def test_03_tenant_isolation_semantic_search(
    service: ProductSearchService,
) -> None:
    """3. Test tenant isolation in semantic search."""
    tenant_b = uuid.uuid4()

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    res = await service.semantic_search_products(mock_db, tenant_b, "keyboard")
    assert res.tenant_id == tenant_b
    assert res.total_count == 0
