"""Category Behaviour Analysis Application Service for AGENTPAY (Phase 205)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.behaviour_baseline_service import BehaviourBaselineService
from app.application.services.behaviour_tracking_service import BehaviourTrackingService
from app.schemas.behaviour_tracking import BehaviourTrackingQueryRequest
from app.schemas.category_behaviour_analysis import (
    CategoryBehaviourAnalysisRequest,
    CategoryBehaviourAnalysisResult,
)

logger = logging.getLogger("agentguard.security.category_behaviour_analysis")


class CategoryBehaviourAnalysisService:
    """Production Category Behaviour Analysis Engine (Phase 205 - Read/Analysis Only)."""

    def __init__(
        self,
        baseline_service: BehaviourBaselineService | None = None,
        tracking_service: BehaviourTrackingService | None = None,
    ) -> None:
        self.tracking_service = tracking_service or BehaviourTrackingService()
        self.baseline_service = baseline_service or BehaviourBaselineService(
            tracking_service=self.tracking_service
        )

    async def analyze_category_behaviour(
        self,
        db: AsyncSession | Any,
        request: CategoryBehaviourAnalysisRequest,
    ) -> CategoryBehaviourAnalysisResult:
        """Analyze agent purchasing behaviour for a specific product category (Phase 205)."""
        now = datetime.now(UTC)
        norm_cat = request.category.strip().lower()

        baseline = await self.baseline_service.compute_baseline(
            db, tenant_id=request.tenant_id, agent_id=request.agent_id
        )
        if not baseline.baseline_available:
            return CategoryBehaviourAnalysisResult(
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                category=request.category,
                normalized_category=norm_cat,
                familiarity="INSUFFICIENT_DATA",
                transaction_count=0,
                total_amount=Decimal("0.00"),
                average_amount=Decimal("0.00"),
                category_share=Decimal("0.00"),
                severity="COLD_START",
                category_score=Decimal("0.00"),
                reason_codes=["INSUFFICIENT_HISTORY"],
                evaluated_at=now,
            )

        query_req = BehaviourTrackingQueryRequest(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            limit=100,
        )
        query_res = await self.tracking_service.get_agent_events(db, query_req)
        all_events = query_res.events
        total_tx = len(all_events)

        category_events = [
            e
            for e in all_events
            if e.category
            and (
                e.category.strip().lower() == norm_cat
                or e.category.strip().lower().startswith(norm_cat + ".")
                or norm_cat.startswith(e.category.strip().lower() + ".")
            )
        ]
        c_tx_count = len(category_events)

        c_amounts = [e.amount for e in category_events if e.amount is not None]
        c_total_amt = sum(c_amounts, Decimal("0.00"))
        c_avg_amt = (
            round(c_total_amt / Decimal(str(c_tx_count)), 2) if c_tx_count > 0 else Decimal("0.00")
        )
        c_share = (
            round(Decimal(str(c_tx_count)) / Decimal(str(total_tx)), 4)
            if total_tx > 0
            else Decimal("0.00")
        )

        reason_codes: list[str] = []
        is_familiar = any(
            freq_cat == norm_cat
            or freq_cat.startswith(norm_cat + ".")
            or norm_cat.startswith(freq_cat + ".")
            for freq_cat in baseline.frequent_categories
        )

        if c_tx_count == 0:
            familiarity = "FIRST_SEEN"
            severity = "MEDIUM"
            category_score = Decimal("0.25")
            reason_codes.append("FIRST_SEEN_CATEGORY")
        elif is_familiar:
            familiarity = "FAMILIAR"
            severity = "NORMAL"
            category_score = Decimal("0.00")
        else:
            familiarity = "UNFAMILIAR"
            severity = "LOW"
            category_score = Decimal("0.15")
            reason_codes.append("UNFAMILIAR_CATEGORY")

        if (
            request.amount is not None
            and c_avg_amt > Decimal("0.00")
            and request.amount > c_avg_amt * Decimal("3.00")
        ):
            reason_codes.append("CATEGORY_AMOUNT_SPIKE")
            severity = "HIGH"
            category_score = max(category_score, Decimal("0.60"))

        return CategoryBehaviourAnalysisResult(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            category=request.category,
            normalized_category=norm_cat,
            familiarity=familiarity,
            transaction_count=c_tx_count,
            total_amount=c_total_amt,
            average_amount=c_avg_amt,
            category_share=c_share,
            severity=severity,
            category_score=category_score,
            reason_codes=reason_codes,
            evaluated_at=now,
        )
