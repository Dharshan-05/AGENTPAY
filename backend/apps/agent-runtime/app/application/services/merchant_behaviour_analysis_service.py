"""Merchant Behaviour Analysis Application Service for AGENTPAY (Phase 204)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.behaviour_baseline_service import BehaviourBaselineService
from app.application.services.behaviour_tracking_service import BehaviourTrackingService
from app.schemas.behaviour_tracking import BehaviourTrackingQueryRequest
from app.schemas.merchant_behaviour_analysis import (
    MerchantBehaviourAnalysisRequest,
    MerchantBehaviourAnalysisResult,
)

logger = logging.getLogger("agentguard.security.merchant_behaviour_analysis")


class MerchantBehaviourAnalysisService:
    """Production Merchant Behaviour Analysis Engine (Phase 204 - Read/Analysis Only)."""

    def __init__(
        self,
        baseline_service: BehaviourBaselineService | None = None,
        tracking_service: BehaviourTrackingService | None = None,
    ) -> None:
        self.tracking_service = tracking_service or BehaviourTrackingService()
        self.baseline_service = baseline_service or BehaviourBaselineService(
            tracking_service=self.tracking_service
        )

    async def analyze_merchant_behaviour(
        self,
        db: AsyncSession | Any,
        request: MerchantBehaviourAnalysisRequest,
    ) -> MerchantBehaviourAnalysisResult:
        """Analyze agent purchasing behaviour for a specific merchant (Phase 204)."""
        now = datetime.now(UTC)

        baseline = await self.baseline_service.compute_baseline(
            db, tenant_id=request.tenant_id, agent_id=request.agent_id
        )
        if not baseline.baseline_available:
            return MerchantBehaviourAnalysisResult(
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                merchant_id=request.merchant_id,
                familiarity="INSUFFICIENT_DATA",
                transaction_count=0,
                total_amount=Decimal("0.00"),
                average_amount=Decimal("0.00"),
                merchant_share=Decimal("0.00"),
                severity="COLD_START",
                merchant_score=Decimal("0.00"),
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

        merchant_events = [
            e for e in all_events if e.merchant_id and e.merchant_id == request.merchant_id
        ]
        m_tx_count = len(merchant_events)

        m_amounts = [e.amount for e in merchant_events if e.amount is not None]
        m_total_amt = sum(m_amounts, Decimal("0.00"))
        m_avg_amt = (
            round(m_total_amt / Decimal(str(m_tx_count)), 2) if m_tx_count > 0 else Decimal("0.00")
        )
        m_share = (
            round(Decimal(str(m_tx_count)) / Decimal(str(total_tx)), 4)
            if total_tx > 0
            else Decimal("0.00")
        )

        reason_codes: list[str] = []
        m_str = str(request.merchant_id).lower()

        if m_tx_count == 0:
            familiarity = "FIRST_SEEN"
            severity = "MEDIUM"
            merchant_score = Decimal("0.25")
            reason_codes.append("FIRST_SEEN_MERCHANT")
        elif m_str in baseline.frequent_merchants:
            familiarity = "FAMILIAR"
            severity = "NORMAL"
            merchant_score = Decimal("0.00")
        else:
            familiarity = "UNFAMILIAR"
            severity = "LOW"
            merchant_score = Decimal("0.15")
            reason_codes.append("UNFAMILIAR_MERCHANT")

        if (
            request.amount is not None
            and m_avg_amt > Decimal("0.00")
            and request.amount > m_avg_amt * Decimal("3.00")
        ):
            reason_codes.append("MERCHANT_AMOUNT_SPIKE")
            severity = "HIGH"
            merchant_score = max(merchant_score, Decimal("0.60"))

        return MerchantBehaviourAnalysisResult(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            merchant_id=request.merchant_id,
            familiarity=familiarity,
            transaction_count=m_tx_count,
            total_amount=m_total_amt,
            average_amount=m_avg_amt,
            merchant_share=m_share,
            severity=severity,
            merchant_score=merchant_score,
            reason_codes=reason_codes,
            evaluated_at=now,
        )
