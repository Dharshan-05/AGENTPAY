"""Recommendation Engine Domain Application Service for AGENTPAY (Phase 174)."""

from __future__ import annotations

import inspect
import logging
import uuid
from typing import Any

from sqlalchemy import select

from app.application.services.embedding_service import EmbeddingService
from app.application.services.product_ranking_service import ProductRankingService
from app.domain.exceptions.agent_exceptions import (
    ProductNotFoundError,
)
from app.infrastructure.database.models.product import Product
from app.infrastructure.database.repositories.product_repository import ProductRepository
from app.schemas.product_recommendations import RecommendationItem, RecommendationResponse

logger = logging.getLogger("agentpay.product.recommendation.service")

_LIMIT_DEFAULT = 10
_LIMIT_MAX = 100


class RecommendationService:
    """Production service orchestrating bounded, deduplicated product recommendations (Phase 174)."""  # noqa: E501

    def __init__(
        self,
        repository: ProductRepository | None = None,
        ranking_service: ProductRankingService | None = None,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self.repository = repository or ProductRepository()
        self.ranking_service = ranking_service or ProductRankingService()
        self.embedding_service = embedding_service or EmbeddingService()

    async def get_recommendations(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        *,
        recommendation_type: str = "similar_products",
        target_product_id: uuid.UUID | None = None,
        query: str | None = None,
        limit: int = _LIMIT_DEFAULT,
    ) -> RecommendationResponse:
        """Generate deduplicated, bounded product recommendations (Phase 174)."""
        fetch_limit = min(max(1, limit), _LIMIT_MAX)
        rec_type = recommendation_type.strip().lower()

        target_product: Product | None = None
        if target_product_id:
            target_product = await self.repository.get_by_id(
                db, tenant_id, target_product_id, include_deleted=False
            )
            if not target_product or target_product.status != "active":
                raise ProductNotFoundError(f"Target product '{target_product_id}' not found.")

        # 1. Fetch candidate active tenant products from repository
        stmt = select(Product).where(
            Product.tenant_id == tenant_id,
            Product.status == "active",
            Product.deleted_at.is_(None),
        )
        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res
        raw_candidates = list(res.scalars().all())

        # 2. Candidate Deduplication & Self-Product Exclusion
        seen_ids: set[uuid.UUID] = set()
        candidates: list[Product] = []

        for p in raw_candidates:
            if target_product_id and p.id == target_product_id:
                continue  # Self-exclusion
            if p.id in seen_ids:
                continue  # Deduplication
            seen_ids.add(p.id)
            candidates.append(p)

        if not candidates:
            return RecommendationResponse(
                tenant_id=tenant_id,
                recommendation_type=rec_type,
                target_product_id=target_product_id,
                total_count=0,
                results=[],
            )

        # 3. Vector similarity scoring against target product or query text
        if target_product:
            target_vec = self.embedding_service.embed_product(
                target_product.name, target_product.sku, target_product.description
            )
            reason_template = f"High similarity to {target_product.name}"
        elif query and query.strip():
            target_vec = self.embedding_service.embed_text(query.strip())
            reason_template = f"Conceptually relevant to search query '{query.strip()}'"
        else:
            # Fallback catalog vector
            target_vec = self.embedding_service.embed_text("catalog featured products")
            reason_template = "Recommended featured product"

        results: list[RecommendationItem] = []

        for p in candidates:
            prod_vec = self.embedding_service.embed_product(p.name, p.sku, p.description)
            score = self.embedding_service.cosine_similarity(target_vec, prod_vec)

            results.append(
                RecommendationItem(
                    product_id=p.id,
                    merchant_id=p.merchant_id,
                    sku=p.sku,
                    name=p.name,
                    description=p.description,
                    price=p.price,
                    currency_code=getattr(p, "currency_code", None) or "USD",
                    status=p.status,
                    recommendation_score=round(score, 4),
                    recommendation_type=rec_type,
                    recommendation_reason=reason_template,
                )
            )

        # Sort descending by recommendation_score, then product_id ASC
        results.sort(key=lambda x: (-x.recommendation_score, str(x.product_id)))

        if len(results) > fetch_limit:
            results = results[:fetch_limit]

        return RecommendationResponse(
            tenant_id=tenant_id,
            recommendation_type=rec_type,
            target_product_id=target_product_id,
            total_count=len(results),
            results=results,
        )
