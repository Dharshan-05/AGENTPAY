"""Product Search & Semantic Search Application Service for AGENTPAY (Phase 168 & 169)."""

from __future__ import annotations

import inspect
import logging
import uuid
from typing import Any

from sqlalchemy import select

from app.application.services.embedding_service import EmbeddingService
from app.domain.exceptions.agent_exceptions import ProductValidationError
from app.infrastructure.database.models.product import Product
from app.infrastructure.database.repositories.product_repository import ProductRepository
from app.schemas.product_search import (
    ProductSearchResponse,
    ProductSearchResult,
    SemanticProductSearchResponse,
    SemanticProductSearchResult,
)

logger = logging.getLogger("agentpay.product.search.service")

_LIMIT_DEFAULT = 20
_LIMIT_MAX = 100
_QUERY_MIN_LEN = 1
_QUERY_MAX_LEN = 255


class ProductSearchService:
    """Production service orchestrating keyword text search and semantic vector search (Phase 168 & 169)."""  # noqa: E501

    def __init__(
        self,
        repository: ProductRepository | None = None,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self.repository = repository or ProductRepository()
        self.embedding_service = embedding_service or EmbeddingService()

    async def search_products(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        query: str,
        *,
        merchant_id: uuid.UUID | None = None,
        limit: int = _LIMIT_DEFAULT,
    ) -> ProductSearchResponse:
        """Perform deterministic keyword search over product name, SKU, and description (Phase 168)."""  # noqa: E501
        clean_q = self._validate_query(query)
        q_lower = clean_q.lower()
        terms = q_lower.split()

        fetch_limit = min(max(1, limit), _LIMIT_MAX)

        # 1. Fetch active, non-deleted tenant products from repository
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
        all_products = list(res.scalars().all())

        matched_results: list[ProductSearchResult] = []

        for p in all_products:
            p_sku = p.sku.lower()
            p_name = p.name.lower()
            p_desc = (p.description or "").lower()

            rel_score = 0.0
            match_category = ""

            if p_sku == q_lower:
                rel_score = 1.0
                match_category = "EXACT_SKU"
            elif p_name == q_lower:
                rel_score = 0.9
                match_category = "EXACT_NAME"
            elif q_lower in p_name:
                rel_score = 0.75
                match_category = "NAME_MATCH"
            elif any(t in p_name for t in terms):
                rel_score = 0.6
                match_category = "NAME_SUBSTRING"
            elif q_lower in p_desc or any(t in p_desc for t in terms):
                rel_score = 0.4
                match_category = "DESCRIPTION_MATCH"

            if rel_score > 0.0:
                matched_results.append(
                    ProductSearchResult(
                        product_id=p.id,
                        tenant_id=p.tenant_id,
                        merchant_id=p.merchant_id,
                        sku=p.sku,
                        name=p.name,
                        description=p.description,
                        price=p.price,
                        currency_code=getattr(p, "currency_code", None) or "USD",
                        status=p.status,
                        relevance_score=round(rel_score, 4),
                        match_type=match_category,
                    )
                )

        # Sort descending by relevance score
        matched_results.sort(key=lambda x: x.relevance_score, reverse=True)

        has_more = len(matched_results) > fetch_limit
        if has_more:
            matched_results = matched_results[:fetch_limit]

        return ProductSearchResponse(
            query=clean_q,
            tenant_id=tenant_id,
            total_count=len(matched_results),
            has_more=has_more,
            results=matched_results,
        )

    async def semantic_search_products(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        query: str,
        *,
        merchant_id: uuid.UUID | None = None,
        limit: int = _LIMIT_DEFAULT,
        hybrid: bool = True,
        keyword_weight: float = 0.5,
        semantic_weight: float = 0.5,
    ) -> SemanticProductSearchResponse:
        """Perform semantic vector search using embedding cosine similarity and hybrid scoring (Phase 169)."""  # noqa: E501
        clean_q = self._validate_query(query)
        query_vec = self.embedding_service.embed_text(clean_q)

        fetch_limit = min(max(1, limit), _LIMIT_MAX)

        # 1. Fetch active, non-deleted tenant products
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
        all_products = list(res.scalars().all())

        results: list[SemanticProductSearchResult] = []

        # Also obtain keyword scores for hybrid combination
        kw_res = await self.search_products(
            db, tenant_id, clean_q, merchant_id=merchant_id, limit=len(all_products)
        )  # noqa: E501
        kw_map = {r.product_id: r.relevance_score for r in kw_res.results}

        for p in all_products:
            prod_vec = self.embedding_service.embed_product(p.name, p.sku, p.description)
            sem_score = self.embedding_service.cosine_similarity(query_vec, prod_vec)
            kw_score = kw_map.get(p.id, 0.0)

            if hybrid:
                h_score = (keyword_weight * kw_score) + (semantic_weight * sem_score)
            else:
                h_score = sem_score

            h_score = round(min(1.0, max(0.0, h_score)), 4)

            # Include item if semantic score or keyword score is non-zero
            if sem_score > 0.0 or kw_score > 0.0:
                results.append(
                    SemanticProductSearchResult(
                        product_id=p.id,
                        tenant_id=p.tenant_id,
                        merchant_id=p.merchant_id,
                        sku=p.sku,
                        name=p.name,
                        description=p.description,
                        price=p.price,
                        currency_code=getattr(p, "currency_code", None) or "USD",
                        status=p.status,
                        semantic_score=round(sem_score, 4),
                        keyword_score=round(kw_score, 4),
                        hybrid_score=h_score,
                    )
                )

        # Sort descending by hybrid_score
        results.sort(key=lambda x: x.hybrid_score, reverse=True)

        if len(results) > fetch_limit:
            results = results[:fetch_limit]

        return SemanticProductSearchResponse(
            query=clean_q,
            tenant_id=tenant_id,
            hybrid_enabled=hybrid,
            total_count=len(results),
            results=results,
        )

    def _validate_query(self, query: str) -> str:
        """Validate and clean search query string."""
        if not query or not query.strip():
            raise ProductValidationError("Search query cannot be empty.")
        clean = query.strip()
        if len(clean) > _QUERY_MAX_LEN:
            raise ProductValidationError(
                f"Search query exceeds maximum length of {_QUERY_MAX_LEN} characters."
            )
        return clean
