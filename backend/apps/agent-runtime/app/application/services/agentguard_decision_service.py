"""AgentGuard Decision Application Service for AGENTPAY (Phase 214)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_risk_profile_service import AgentRiskProfileService
from app.application.services.behaviour_risk_service import BehaviourRiskService
from app.application.services.intent_risk_service import IntentRiskService
from app.application.services.policy_evaluation_service import PolicyEvaluationService
from app.application.services.trust_score_calculation_service import (
    TrustScoreCalculationService,
)
from app.application.services.velocity_risk_service import VelocityRiskService
from app.schemas.agentguard_decision import (
    AgentGuardDecisionRequest,
    AgentGuardDecisionResult,
)
from app.schemas.behaviour_risk import BehaviourRiskRequest
from app.schemas.intent_risk import IntentRiskRequest
from app.schemas.policy_evaluation import PolicyEvaluationContext
from app.schemas.trust_score_calculation import TrustScoreCalculationRequest
from app.schemas.velocity_risk import VelocityRiskRequest

logger = logging.getLogger("agentguard.security.decision_engine")


class AgentGuardDecisionService:
    """Production AgentGuard Unified Security Decision Engine (Phase 214)."""

    def __init__(
        self,
        behaviour_risk_service: BehaviourRiskService | None = None,
        velocity_risk_service: VelocityRiskService | None = None,
        intent_risk_service: IntentRiskService | None = None,
        trust_calc_service: TrustScoreCalculationService | None = None,
        risk_profile_service: AgentRiskProfileService | None = None,
        policy_evaluation_service: PolicyEvaluationService | None = None,
    ) -> None:
        self.behaviour_risk_service = behaviour_risk_service or BehaviourRiskService()
        self.velocity_risk_service = velocity_risk_service or VelocityRiskService()
        self.intent_risk_service = intent_risk_service or IntentRiskService()
        self.trust_calc_service = trust_calc_service or TrustScoreCalculationService()
        self.risk_profile_service = risk_profile_service or AgentRiskProfileService()
        self.policy_evaluation_service = policy_evaluation_service or PolicyEvaluationService()

    async def evaluate_agentguard_decision(
        self,
        db: AsyncSession | Any,
        request: AgentGuardDecisionRequest,
    ) -> AgentGuardDecisionResult:
        """Evaluate unified AGENTGUARD security decision (Phase 214)."""
        now = datetime.now(UTC)
        evaluation_id = uuid.uuid4()

        # 1. Intent Risk Engine (Phase 213)
        intent_req = IntentRiskRequest(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            declared_intent=request.metadata.get("declared_intent"),
            requested_action=request.requested_action,
            requested_amount=request.amount,
            requested_currency=request.currency,
            requested_merchant_id=str(request.merchant_id) if request.merchant_id else None,
            requested_category=request.category,
        )
        intent_res = self.intent_risk_service.calculate_intent_risk(intent_req)

        # Fail-closed on critical intent mismatch
        if not intent_res.can_proceed:
            return AgentGuardDecisionResult(
                agent_id=request.agent_id,
                tenant_id=request.tenant_id,
                decision="DENIED",
                risk_level="CRITICAL",
                risk_score=Decimal("1.00"),
                trust_score=Decimal("0.00"),
                confidence=Decimal("1.00"),
                behaviour_risk_score=Decimal("0.00"),
                velocity_risk_score=Decimal("0.00"),
                intent_risk_score=intent_res.intent_risk_score,
                can_proceed=False,
                requires_approval=False,
                reason_codes=[rf.code for rf in intent_res.risk_factors]
                or ["INTENT_CRITICAL_MISMATCH"],  # noqa: E501
                blocking_factors=["INTENT_CRITICAL_MISMATCH"],
                risk_factors=intent_res.risk_factors,
                evaluation_id=evaluation_id,
                decision_version="2.0",
                evaluated_at=now,
            )

        # 2. Behaviour Risk Engine (Phase 211)
        beh_req = BehaviourRiskRequest(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            amount=request.amount,
            currency=request.currency,
            merchant_id=request.merchant_id,
            category=request.category,
        )
        beh_res = await self.behaviour_risk_service.calculate_behaviour_risk(db, beh_req)

        # 3. Velocity Risk Engine (Phase 212)
        vel_req = VelocityRiskRequest(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            window_minutes=60,
        )
        vel_res = await self.velocity_risk_service.calculate_velocity_risk(db, vel_req)

        # 4. Trust Score Calculation (Phase 207)
        trust_req = TrustScoreCalculationRequest(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            behaviour_risk_score=beh_res.behaviour_risk_score,
            intent_risk_score=intent_res.intent_risk_score,
            velocity_risk_score=vel_res.velocity_risk_score,
            violation_count=0,
            baseline_available=beh_res.severity != "COLD_START",
        )
        trust_res = self.trust_calc_service.calculate_trust_score(trust_req)

        # 5. Risk Profile Aggregation (Phase 208)
        combined_factors = beh_res.risk_factors + vel_res.risk_factors + intent_res.risk_factors
        profile = self.risk_profile_service.build_risk_profile(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            trust_score=trust_res.trust_score,
            risk_factors=combined_factors,
            is_cold_start=beh_res.severity == "COLD_START",
        )

        # 6. Authoritative Policy Evaluation (Phases 187-205)
        policy_ctx = PolicyEvaluationContext(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            principal_id=request.principal_id,
            transaction_id=request.transaction_id,
            merchant_id=request.merchant_id,
            category=request.category,
            amount=request.amount,
            currency=request.currency,
            requested_action=request.requested_action,
            metadata=request.metadata,
        )
        policy_res = await self.policy_evaluation_service.evaluate_policies(
            db, request.tenant_id, request.agent_id, policy_ctx
        )

        blocking_factors: list[str] = []
        # Enforce strict decision precedence:
        # DENY > CRITICAL FAILURE > REQUIRE_APPROVAL > ALLOW
        if policy_res.decision == "DENIED":
            final_decision = "DENIED"
            can_proceed = False
            requires_approval = False
            blocking_factors = [
                rc
                for rc in policy_res.reason_codes
                if "DENIED" in rc or "BLOCKED" in rc or "LIMIT_EXCEEDED" in rc
            ] or ["POLICY_DENIED"]  # noqa: E501
        elif profile.risk_level == "CRITICAL":
            final_decision = "DENIED"
            can_proceed = False
            requires_approval = False
            blocking_factors = ["CRITICAL_RISK_LEVEL"]
        elif policy_res.decision == "REQUIRE_APPROVAL" or profile.risk_level in (
            "HIGH",
            "ELEVATED",
        ):
            final_decision = "REQUIRE_APPROVAL"
            can_proceed = False
            requires_approval = True
        else:
            final_decision = policy_res.decision
            can_proceed = True
            requires_approval = False

        all_reason_codes = list(
            dict.fromkeys(policy_res.reason_codes + [f.code for f in combined_factors])
        )

        return AgentGuardDecisionResult(
            agent_id=request.agent_id,
            tenant_id=request.tenant_id,
            decision=final_decision,
            risk_level=profile.risk_level,
            risk_score=profile.risk_score,
            trust_score=trust_res.trust_score,
            confidence=trust_res.confidence,
            behaviour_risk_score=beh_res.behaviour_risk_score,
            velocity_risk_score=vel_res.velocity_risk_score,
            intent_risk_score=intent_res.intent_risk_score,
            can_proceed=can_proceed,
            requires_approval=requires_approval,
            reason_codes=all_reason_codes,
            blocking_factors=blocking_factors,
            risk_factors=combined_factors,
            evaluation_id=evaluation_id,
            decision_version="2.0",
            evaluated_at=now,
        )
