"""Product Ranking Domain Application Service for AGENTPAY (Phase 173)."""

from __future__ import annotations

import inspect
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select

from app.application.services.embedding_service import EmbeddingService
from app.application.services.product_search_service import ProductSearchService
from app.domain.exceptions.agent_exceptions import ProductValidationError
from app.infrastructure.database.models.product import Product
from app.infrastructure.database.repositories.product_repository import ProductRepository
from app.schemas.product_ranking import ProductRankingResponse, RankedProductItem

logger = logging.getLogger("agentpay.product.ranking.service")

_LIMIT_DEFAULT = 20
_LIMIT_MAX = 100

# Transparent scoring weights (sum to 1.0)
SEMANTIC_WEIGHT = 0.40
KEYWORD_WEIGHT = 0.35
BUSINESS_WEIGHT = 0.15
FRESHNESS_WEIGHT = 0.10


class ProductRankingService:
    """Production service for transparent, multi-signal explainable product ranking (Phase 173)."""

    def __init__(
        self,
        repository: ProductRepository | None = None,
        search_service: ProductSearchService | None = None,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self.repository = repository or ProductRepository()
        self.search_service = search_service or ProductSearchService()
        self.embedding_service = embedding_service or EmbeddingService()

    async def rank_products(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        query: str,
        *,
        merchant_id: uuid.UUID | None = None,
        limit: int = _LIMIT_DEFAULT,
    ) -> ProductRankingResponse:
        """Rank candidate products using multi-signal scoring model (Phase 173)."""
        if not query or not query.strip():
            raise ProductValidationError("Ranking query string cannot be empty.")

        clean_q = query.strip()
        fetch_limit = min(max(1, limit), _LIMIT_MAX)

        # 1. Fetch active candidate products from repository
        stmt = select(Product).where(
            Product.tenant_id == tenant_id,
            Product.status == "active",
            Product.deleted_at.is_(None),
        )
        if merchant_id:
            stmt = stmt.where(Product.merchant_id == merchant_id)

        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res
        candidates = list(res.scalars().all())

        if not candidates:
            return ProductRankingResponse(
                query=clean_q,
                tenant_id=tenant_id,
                total_count=0,
                results=[],
            )

        # 2. Obtain keyword scores
        kw_resp = await self.search_service.search_products(
            db, tenant_id, clean_q, merchant_id=merchant_id, limit=len(candidates)
        )
        kw_map = {
            item.product_id: (item.relevance_score, item.match_type) for item in kw_resp.results
        }  # noqa: E501

        # 3. Compute vector query embedding
        query_vec = self.embedding_service.embed_text(clean_q)
        now = datetime.now(UTC)

        ranked_items: list[RankedProductItem] = []

        for p in candidates:
            # Signal 1: Semantic Vector Similarity
            prod_vec = self.embedding_service.embed_product(p.name, p.sku, p.description)
            sem_score = self.embedding_service.cosine_similarity(query_vec, prod_vec)

            # Signal 2: Keyword Relevance
            kw_tuple = kw_map.get(p.id, (0.0, "NO_MATCH"))
            kw_score, match_type = kw_tuple

            # Signal 3: Business Quality Score
            biz_score = 1.0 if p.status == "active" else 0.5

            # Signal 4: Freshness Decay Score (1-year linear decay)
            age_days = (
                (now - p.created_at.replace(tzinfo=UTC)).total_seconds() / 86400.0
                if p.created_at
                else 0.0
            )
            freshness_score = round(max(0.0, 1.0 - (age_days / 365.0)), 4)

            # Weighted combination
            composite = (
                (SEMANTIC_WEIGHT * sem_score)
                + (KEYWORD_WEIGHT * kw_score)
                + (BUSINESS_WEIGHT * biz_score)
                + (FRESHNESS_WEIGHT * freshness_score)
            )
            final_rank_score = round(min(1.0, max(0.0, composite)), 4)

            # Build explainable reasons list
            reasons: list[str] = []
            if kw_score >= 0.9:
                reasons.append(f"Exact match ({match_type})")
            elif kw_score >= 0.5:
                reasons.append(f"Keyword match ({match_type})")

            if sem_score >= 0.7:
                reasons.append("Strong semantic concept similarity")
            elif sem_score >= 0.4:
                reasons.append("Moderate semantic concept similarity")

            if freshness_score >= 0.8:
                reasons.append("Recently added product")

            if not reasons:
                reasons.append("Standard catalog rank")

            ranked_items.append(
                RankedProductItem(
                    product_id=p.id,
                    tenant_id=p.tenant_id,
                    merchant_id=p.merchant_id,
                    sku=p.sku,
                    name=p.name,
                    description=p.description,
                    price=p.price,
                    currency_code=getattr(p, "currency_code", None) or "USD",
                    status=p.status,
                    ranking_score=final_rank_score,
                    semantic_score=round(sem_score, 4),
                    keyword_score=round(kw_score, 4),
                    business_score=round(biz_score, 4),
                    freshness_score=round(freshness_score, 4),
                    ranking_reasons=reasons,
                )
            )

        # Deterministic tie-breaking: ranking_score DESC, product_id ASC
        ranked_items.sort(key=lambda x: (-x.ranking_score, str(x.product_id)))

        if len(ranked_items) > fetch_limit:
            ranked_items = ranked_items[:fetch_limit]

        return ProductRankingResponse(
            query=clean_q,
            tenant_id=tenant_id,
            total_count=len(ranked_items),
            results=ranked_items,
        )
