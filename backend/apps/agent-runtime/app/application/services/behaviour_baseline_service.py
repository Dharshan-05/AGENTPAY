"""Behaviour Baseline Application Service for AGENTPAY (Phase 201)."""

from __future__ import annotations

import logging
import uuid
from collections import Counter
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.behaviour_tracking_service import BehaviourTrackingService
from app.schemas.behaviour_baseline import AmountStatistics, BehaviourBaseline
from app.schemas.behaviour_tracking import BehaviourTrackingQueryRequest

logger = logging.getLogger("agentguard.security.behaviour_baseline")


class BehaviourBaselineService:
    """Production Behaviour Baseline Engine (Phase 201 - Read/Compute Only)."""

    def __init__(self, tracking_service: BehaviourTrackingService | None = None) -> None:
        self.tracking_service = tracking_service or BehaviourTrackingService()

    async def compute_baseline(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        min_observations: int = 5,
    ) -> BehaviourBaseline:
        """Compute deterministic behaviour baseline from authoritative event data (Phase 201)."""
        now = datetime.now(UTC)

        query_req = BehaviourTrackingQueryRequest(
            tenant_id=tenant_id,
            agent_id=agent_id,
            limit=100,
        )
        query_res = await self.tracking_service.get_agent_events(db, query_req)
        events = query_res.events

        obs_count = len(events)
        if obs_count < min_observations:
            return BehaviourBaseline(
                agent_id=agent_id,
                tenant_id=tenant_id,
                baseline_available=False,
                state="COLD_START",
                observation_count=obs_count,
                successful_count=sum(1 for e in events if e.outcome == "SUCCESS"),
                failed_count=sum(1 for e in events if e.outcome == "FAILED"),
                amount_stats=None,
                frequent_merchants=[],
                frequent_categories=[],
                frequent_currencies=[],
                generated_at=now,
            )

        amounts = [e.amount for e in events if e.amount is not None]
        success_count = sum(1 for e in events if e.outcome == "SUCCESS")
        failed_count = obs_count - success_count

        if amounts:
            total_amt = sum(amounts, Decimal("0.00"))
            avg_amt = round(total_amt / Decimal(str(len(amounts))), 2)
            min_amt = min(amounts)
            max_amt = max(amounts)
            amt_stats = AmountStatistics(
                total_amount=total_amt,
                average_amount=avg_amt,
                min_amount=min_amt,
                max_amount=max_amt,
            )
        else:
            amt_stats = None

        merchant_counts = Counter([str(e.merchant_id).lower() for e in events if e.merchant_id])
        category_counts = Counter([e.category.lower() for e in events if e.category])
        currency_counts = Counter([e.currency.upper() for e in events if e.currency])

        top_merchants = [m for m, _ in merchant_counts.most_common(5)]
        top_categories = [c for c, _ in category_counts.most_common(5)]
        top_currencies = [curr for curr, _ in currency_counts.most_common(3)]

        return BehaviourBaseline(
            agent_id=agent_id,
            tenant_id=tenant_id,
            baseline_available=True,
            state="ESTABLISHED",
            observation_count=obs_count,
            successful_count=success_count,
            failed_count=failed_count,
            amount_stats=amt_stats,
            frequent_merchants=top_merchants,
            frequent_categories=top_categories,
            frequent_currencies=top_currencies,
            generated_at=now,
        )
