"""Product Personalization Domain Application Service for AGENTPAY (Phase 175)."""

from __future__ import annotations

import inspect
import logging
import uuid
from typing import Any

from sqlalchemy import select

from app.application.services.agent_memory_service import AgentMemoryService
from app.application.services.product_ranking_service import ProductRankingService
from app.infrastructure.database.models.agent_memory import AgentMemory
from app.infrastructure.database.repositories.product_repository import ProductRepository
from app.schemas.product_personalization import (
    PersonalizedProductItem,
    PersonalizedRecommendationResponse,
)

logger = logging.getLogger("agentpay.product.personalization.service")

_LIMIT_DEFAULT = 10
_LIMIT_MAX = 100
_MAX_PERSONALIZATION_BOOST = 0.20


class PersonalizationService:
    """Production service for memory-driven product ranking boost and cold-start support (Phase 175)."""  # noqa: E501

    def __init__(
        self,
        repository: ProductRepository | None = None,
        ranking_service: ProductRankingService | None = None,
        memory_service: AgentMemoryService | None = None,
    ) -> None:
        self.repository = repository or ProductRepository()
        self.ranking_service = ranking_service or ProductRankingService()
        self.memory_service = memory_service or AgentMemoryService()

    async def get_personalized_recommendations(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        *,
        user_id: uuid.UUID | None = None,
        agent_id: uuid.UUID | None = None,
        query: str = "catalog products",
        limit: int = _LIMIT_DEFAULT,
    ) -> PersonalizedRecommendationResponse:
        """Personalize product recommendations using agent memory preference signals (Phase 175)."""
        fetch_limit = min(max(1, limit), _LIMIT_MAX)

        # 1. Obtain base ranked products
        base_resp = await self.ranking_service.rank_products(
            db, tenant_id, query, limit=fetch_limit * 2
        )

        # 2. Extract tenant-scoped memory preference signals for agent (if available)
        preference_keywords: list[str] = []
        if agent_id:
            m_stmt = select(AgentMemory).where(
                AgentMemory.tenant_id == tenant_id,
                AgentMemory.agent_id == agent_id,
                AgentMemory.deleted_at.is_(None),
            )
            res = db.execute(m_stmt)
            if inspect.isawaitable(res):
                res = await res
            memories = list(res.scalars().all())

            for m in memories:
                val_str = str(m.value or {}).lower()
                key_str = m.key.lower()
                for token in (key_str + " " + val_str).split():
                    if len(token) > 3 and token.isalnum():
                        preference_keywords.append(token)

        personalization_applied = len(preference_keywords) > 0
        personalized_items: list[PersonalizedProductItem] = []

        for item in base_resp.results:
            text_corpus = f"{item.name} {item.description or ''} {item.sku}".lower()
            matched_signals: list[str] = []

            for kw in preference_keywords:
                if kw in text_corpus and kw not in matched_signals:
                    matched_signals.append(kw)

            # Bounded boost score calculation
            if matched_signals:
                boost = min(_MAX_PERSONALIZATION_BOOST, round(0.05 * len(matched_signals), 4))
            else:
                boost = 0.0

            final_score = round(min(1.0, item.ranking_score + boost), 4)

            personalized_items.append(
                PersonalizedProductItem(
                    product_id=item.product_id,
                    merchant_id=item.merchant_id,
                    sku=item.sku,
                    name=item.name,
                    description=item.description,
                    price=item.price,
                    currency_code=item.currency_code,
                    status=item.status,
                    base_rank_score=item.ranking_score,
                    personalization_boost=boost,
                    final_score=final_score,
                    personalization_signals=matched_signals[:5],
                )
            )

        # Sort descending by final_score, then product_id ASC
        personalized_items.sort(key=lambda x: (-x.final_score, str(x.product_id)))

        if len(personalized_items) > fetch_limit:
            personalized_items = personalized_items[:fetch_limit]

        return PersonalizedRecommendationResponse(
            tenant_id=tenant_id,
            user_id=user_id,
            agent_id=agent_id,
            personalization_applied=personalization_applied,
            total_count=len(personalized_items),
            results=personalized_items,
        )
