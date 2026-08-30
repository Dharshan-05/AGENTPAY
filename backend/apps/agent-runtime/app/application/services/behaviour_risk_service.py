"""Behaviour Risk Application Service for AGENTPAY (Phase 211)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.behaviour_baseline_service import BehaviourBaselineService
from app.application.services.behaviour_deviation_service import BehaviourDeviationService
from app.schemas.agent_risk_profile import RiskFactor
from app.schemas.behaviour_deviation import BehaviourDeviationRequest
from app.schemas.behaviour_risk import BehaviourRiskRequest, BehaviourRiskResult

logger = logging.getLogger("agentguard.security.behaviour_risk")


class BehaviourRiskService:
    """Production Behaviour Risk Engine (Phase 211 - Read/Advisory Only)."""

    def __init__(
        self,
        baseline_service: BehaviourBaselineService | None = None,
        deviation_service: BehaviourDeviationService | None = None,
    ) -> None:
        self.baseline_service = baseline_service or BehaviourBaselineService()
        self.deviation_service = deviation_service or BehaviourDeviationService()

    async def calculate_behaviour_risk(
        self,
        db: AsyncSession | Any,
        request: BehaviourRiskRequest,
    ) -> BehaviourRiskResult:
        """Calculate normalized behaviour risk score for an agent action (Phase 211)."""
        now = datetime.now(UTC)

        baseline = await self.baseline_service.compute_baseline(
            db, tenant_id=request.tenant_id, agent_id=request.agent_id
        )
        if not baseline.baseline_available:
            return BehaviourRiskResult(
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                behaviour_risk_score=Decimal("0.00"),
                severity="COLD_START",
                risk_factors=[
                    RiskFactor(
                        code="INSUFFICIENT_HISTORY",
                        severity="LOW",
                        source="BEHAVIOUR",
                        confidence=Decimal("0.00"),
                    )
                ],
                confidence=Decimal("0.00"),
                explanation="Insufficient historical data available for behaviour evaluation.",
                evaluated_at=now,
            )

        dev_req = BehaviourDeviationRequest(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            amount=request.amount,
            currency=request.currency,
            merchant_id=request.merchant_id,
            category=request.category,
            baseline=baseline,
        )
        dev_res = self.deviation_service.evaluate_deviation(dev_req)

        risk_factors = [
            RiskFactor(
                code=rc, severity=dev_res.severity, source="BEHAVIOUR", confidence=Decimal("1.00")
            )
            for rc in dev_res.reason_codes
        ]

        return BehaviourRiskResult(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            behaviour_risk_score=dev_res.deviation_score,
            severity=dev_res.severity,
            risk_factors=risk_factors,
            confidence=Decimal("1.00"),
            explanation=dev_res.explanation,
            evaluated_at=now,
        )
