"""Agent Risk Profile Application Service for AGENTPAY (Phase 208)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal

from app.schemas.agent_risk_profile import AgentRiskProfile, RiskFactor

logger = logging.getLogger("agentguard.security.agent_risk_profile")


class AgentRiskProfileService:
    """Production Agent Risk Profile Aggregation Service (Phase 208)."""

    def build_risk_profile(
        self,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        trust_score: Decimal,
        risk_factors: list[RiskFactor] | None = None,
        is_cold_start: bool = False,
    ) -> AgentRiskProfile:
        """Construct structured AgentRiskProfile with distinct risk_score != trust_score (Phase 208)."""  # noqa: E501
        now = datetime.now(UTC)
        factors = risk_factors or []

        # Distinct risk_score calculation: base risk complement + factor severity boosts
        base_risk = round(Decimal("1.00") - trust_score, 2)
        factor_boost = Decimal("0.00")
        if any(f.severity == "CRITICAL" for f in factors):
            factor_boost += Decimal("0.40")
        elif any(f.severity == "HIGH" for f in factors):
            factor_boost += Decimal("0.25")
        elif any(f.severity == "MEDIUM" for f in factors):
            factor_boost += Decimal("0.10")

        risk_score = min(Decimal("1.00"), base_risk + factor_boost)

        if is_cold_start:
            risk_level = "COLD_START"
            recommended_action = "ALLOW"
        elif any(f.severity == "CRITICAL" for f in factors) or risk_score >= Decimal("0.80"):
            risk_level = "CRITICAL"
            recommended_action = "DENY"
        elif any(f.severity == "HIGH" for f in factors) or risk_score >= Decimal("0.55"):
            risk_level = "HIGH"
            recommended_action = "REQUIRE_APPROVAL"
        elif any(f.severity == "MEDIUM" for f in factors) or risk_score >= Decimal("0.35"):
            risk_level = "ELEVATED"
            recommended_action = "REQUIRE_APPROVAL"
        elif risk_score >= Decimal("0.20"):
            risk_level = "NORMAL"
            recommended_action = "ALLOW"
        else:
            risk_level = "LOW"
            recommended_action = "ALLOW"

        reasons = [f"{f.source}: {f.code} ({f.severity})" for f in factors]
        if not reasons:
            reasons = [f"Risk profile evaluated at {risk_level} level."]

        return AgentRiskProfile(
            agent_id=agent_id,
            tenant_id=tenant_id,
            risk_score=risk_score,
            trust_score=trust_score,
            risk_level=risk_level,
            risk_factors=factors,
            recommended_action=recommended_action,
            explainable_reasons=reasons,
            evaluated_at=now,
        )
