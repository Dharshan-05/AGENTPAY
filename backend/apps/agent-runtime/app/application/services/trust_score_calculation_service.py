"""Trust Score Calculation Application Service for AGENTPAY (Phase 207)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal

from app.application.services.agent_trust_score_service import AgentTrustScoreService
from app.schemas.agent_trust_score import TrustDimension
from app.schemas.trust_score_calculation import (
    TrustScoreCalculationRequest,
    TrustScoreCalculationResult,
)

logger = logging.getLogger("agentguard.security.trust_score_calculation")


class TrustScoreCalculationService:
    """Production Trust Score Calculation Engine (Phase 207)."""

    def __init__(self, trust_score_service: AgentTrustScoreService | None = None) -> None:
        self.trust_score_service = trust_score_service or AgentTrustScoreService()

    def calculate_trust_score(
        self,
        request: TrustScoreCalculationRequest,
    ) -> TrustScoreCalculationResult:
        """Calculate deterministic agent trust score from input risk signals (Phase 207)."""
        now = datetime.now(UTC)

        if not request.baseline_available:
            cold_dimensions = [
                TrustDimension(
                    dimension_name="HISTORICAL_BASELINE",
                    score=Decimal("0.50"),
                    weight=Decimal("1.00"),
                    confidence=Decimal("0.00"),
                    explanation="No historical baseline observations available.",
                    source="BEHAVIOUR_BASELINE",
                )
            ]
            ts = self.trust_score_service.create_trust_score(
                request.tenant_id,
                request.agent_id,
                Decimal("0.50"),
                dimensions=cold_dimensions,
                confidence=Decimal("0.20"),
            )
            return TrustScoreCalculationResult(
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                trust_score=Decimal("0.50"),
                confidence=Decimal("0.20"),
                trust_state="COLD_START",
                dimensions=cold_dimensions,
                deductions={"COLD_START_NEUTRAL": Decimal("0.50")},
                explanation="Cold-start agent assigned neutral initial trust score with zero baseline confidence.",  # noqa: E501
                calculation_version="2.0",
                evaluated_at=now,
            )

        base_score = Decimal("1.00")
        deductions: dict[str, Decimal] = {}
        dimensions: list[TrustDimension] = []

        # 1. Behaviour dimension (Weight 0.30)
        beh_score = round(Decimal("1.00") - request.behaviour_risk_score, 2)
        beh_ded = round(request.behaviour_risk_score * Decimal("0.30"), 2)
        if beh_ded > Decimal("0.00"):
            deductions["BEHAVIOUR_RISK"] = beh_ded
        dimensions.append(
            TrustDimension(
                dimension_name="BEHAVIOUR_STABILITY",
                score=beh_score,
                weight=Decimal("0.30"),
                confidence=Decimal("1.00"),
                explanation=f"Behaviour stability score: {beh_score}",
                source="BEHAVIOUR_ENGINE",
            )
        )

        # 2. Intent dimension (Weight 0.35)
        int_score = round(Decimal("1.00") - request.intent_risk_score, 2)
        int_ded = round(request.intent_risk_score * Decimal("0.35"), 2)
        if int_ded > Decimal("0.00"):
            deductions["INTENT_RISK"] = int_ded
        dimensions.append(
            TrustDimension(
                dimension_name="INTENT_CONSISTENCY",
                score=int_score,
                weight=Decimal("0.35"),
                confidence=Decimal("1.00"),
                explanation=f"Intent consistency score: {int_score}",
                source="INTENT_ENGINE",
            )
        )

        # 3. Velocity dimension (Weight 0.20)
        vel_score = round(Decimal("1.00") - request.velocity_risk_score, 2)
        vel_ded = round(request.velocity_risk_score * Decimal("0.20"), 2)
        if vel_ded > Decimal("0.00"):
            deductions["VELOCITY_RISK"] = vel_ded
        dimensions.append(
            TrustDimension(
                dimension_name="VELOCITY_STABILITY",
                score=vel_score,
                weight=Decimal("0.20"),
                confidence=Decimal("1.00"),
                explanation=f"Velocity stability score: {vel_score}",
                source="VELOCITY_ENGINE",
            )
        )

        # 4. Violation dimension (Weight 0.15 max)
        viol_ded = min(Decimal(str(request.violation_count)) * Decimal("0.05"), Decimal("0.15"))
        viol_score = round(Decimal("1.00") - viol_ded, 2)
        if viol_ded > Decimal("0.00"):
            deductions["VIOLATIONS"] = viol_ded
        dimensions.append(
            TrustDimension(
                dimension_name="POLICY_COMPLIANCE",
                score=viol_score,
                weight=Decimal("0.15"),
                confidence=Decimal("1.00"),
                explanation=f"Policy compliance score based on {request.violation_count} violations.",  # noqa: E501
                source="VIOLATION_TRACKING",
            )
        )

        total_deduction = sum(deductions.values(), Decimal("0.00"))
        final_score = max(Decimal("0.00"), base_score - total_deduction)

        ts = self.trust_score_service.create_trust_score(
            request.tenant_id,
            request.agent_id,
            final_score,
            dimensions=dimensions,
            confidence=Decimal("1.00"),
        )

        return TrustScoreCalculationResult(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            trust_score=ts.trust_score,
            confidence=ts.confidence,
            trust_state=ts.trust_state,
            dimensions=dimensions,
            deductions=deductions,
            explanation=f"Calculated trust score: {ts.trust_score} ({ts.trust_state}).",
            calculation_version="2.0",
            evaluated_at=now,
        )
