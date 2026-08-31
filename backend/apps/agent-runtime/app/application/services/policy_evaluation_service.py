"""Policy Evaluation Engine Application Service for AGENTPAY (Phases 187–205)."""

from __future__ import annotations

import inspect
import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_identity_verification_service import (
    AgentIdentityVerificationService,
)
from app.application.services.behaviour_baseline_service import BehaviourBaselineService
from app.application.services.behaviour_deviation_service import BehaviourDeviationService
from app.application.services.category_behaviour_analysis_service import (
    CategoryBehaviourAnalysisService,
)
from app.application.services.category_restriction_service import CategoryRestrictionService
from app.application.services.daily_spending_limit_service import DailySpendingLimitService
from app.application.services.intent_matching_service import IntentMatchingService
from app.application.services.intent_mismatch_detection_service import (
    IntentMismatchDetectionService,
)
from app.application.services.intent_verification_service import IntentVerificationService
from app.application.services.merchant_behaviour_analysis_service import (
    MerchantBehaviourAnalysisService,
)
from app.application.services.merchant_restriction_service import MerchantRestrictionService
from app.application.services.policy_conflict_resolution_service import (
    PolicyConflictResolutionService,
)
from app.application.services.policy_priority_service import PolicyPriorityService
from app.application.services.policy_rule_engine import PolicyRuleEngine
from app.application.services.spending_limit_service import SpendingLimitService
from app.application.services.time_based_policy_service import TimeBasedPolicyService
from app.application.services.transaction_threshold_service import TransactionThresholdService
from app.application.services.velocity_detection_service import VelocityDetectionService
from app.infrastructure.database.models.policy_rule import PolicyRule
from app.infrastructure.database.models.security_policy import SecurityPolicy
from app.schemas.behaviour_deviation import BehaviourDeviationRequest
from app.schemas.category_behaviour_analysis import CategoryBehaviourAnalysisRequest
from app.schemas.category_restrictions import CategoryRestrictionEvaluationRequest
from app.schemas.intent_matching import IntentMatchRequest
from app.schemas.intent_mismatch import IntentMismatchDetectionRequest
from app.schemas.intent_verification import DeclaredIntent, IntentVerificationRequest
from app.schemas.merchant_behaviour_analysis import MerchantBehaviourAnalysisRequest
from app.schemas.merchant_restrictions import MerchantRestrictionEvaluationRequest
from app.schemas.policy_conflict_resolution import PolicyCandidate
from app.schemas.policy_evaluation import (
    PolicyEvaluationContext,
    PolicyEvaluationResult,
)
from app.schemas.policy_rules import PolicyRuleContext, PolicyRuleResult
from app.schemas.spending_limits import SpendingLimitEvaluationRequest
from app.schemas.time_based_policies import TimeBasedPolicyEvaluationRequest
from app.schemas.transaction_thresholds import TransactionThresholdEvaluationRequest
from app.schemas.velocity_detection import VelocityDetectionRequest

logger = logging.getLogger("agentguard.security.policy_evaluation_engine")


class PolicyEvaluationService:
    """Production policy evaluation engine orchestrating security policies & engines (Phases 187–205)."""  # noqa: E501

    def __init__(
        self,
        identity_service: AgentIdentityVerificationService | None = None,
        rule_engine: PolicyRuleEngine | None = None,
        spending_service: SpendingLimitService | None = None,
        daily_spending_service: DailySpendingLimitService | None = None,
        threshold_service: TransactionThresholdService | None = None,
        category_service: CategoryRestrictionService | None = None,
        merchant_service: MerchantRestrictionService | None = None,
        time_service: TimeBasedPolicyService | None = None,
        priority_service: PolicyPriorityService | None = None,
        conflict_service: PolicyConflictResolutionService | None = None,
        intent_verification_service: IntentVerificationService | None = None,
        intent_matching_service: IntentMatchingService | None = None,
        intent_mismatch_service: IntentMismatchDetectionService | None = None,
        baseline_service: BehaviourBaselineService | None = None,
        deviation_service: BehaviourDeviationService | None = None,
        velocity_service: VelocityDetectionService | None = None,
        merchant_behaviour_service: MerchantBehaviourAnalysisService | None = None,
        category_behaviour_service: CategoryBehaviourAnalysisService | None = None,
    ) -> None:
        self.identity_service = identity_service or AgentIdentityVerificationService()
        self.rule_engine = rule_engine or PolicyRuleEngine()
        self.spending_service = spending_service or SpendingLimitService()
        self.daily_spending_service = daily_spending_service or DailySpendingLimitService()
        self.threshold_service = threshold_service or TransactionThresholdService()
        self.category_service = category_service or CategoryRestrictionService()
        self.merchant_service = merchant_service or MerchantRestrictionService()
        self.time_service = time_service or TimeBasedPolicyService()
        self.priority_service = priority_service or PolicyPriorityService()
        self.conflict_service = conflict_service or PolicyConflictResolutionService()
        self.intent_verification_service = (
            intent_verification_service or IntentVerificationService()
        )
        self.intent_matching_service = intent_matching_service or IntentMatchingService()
        self.intent_mismatch_service = intent_mismatch_service or IntentMismatchDetectionService()
        self.baseline_service = baseline_service or BehaviourBaselineService()
        self.deviation_service = deviation_service or BehaviourDeviationService()
        self.velocity_service = velocity_service or VelocityDetectionService()
        self.merchant_behaviour_service = (
            merchant_behaviour_service or MerchantBehaviourAnalysisService()
        )
        self.category_behaviour_service = (
            category_behaviour_service or CategoryBehaviourAnalysisService()
        )

    async def evaluate_policies(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        context: PolicyEvaluationContext,
    ) -> PolicyEvaluationResult:
        """Evaluate applicable policies for an agent context deterministically (Phases 187–205)."""  # noqa: E501
        now = datetime.now(UTC)

        # 1. Identity Verification Step
        id_res = await self.identity_service.verify_agent_identity(
            db, tenant_id=tenant_id, agent_id=agent_id, principal_id=context.principal_id
        )
        if not id_res.verified:
            logger.info("Policy evaluation DENIED for agent %s: identity not verified", agent_id)
            return PolicyEvaluationResult(
                agent_id=agent_id,
                tenant_id=tenant_id,
                decision="DENIED",
                evaluated_policy_ids=[],
                matched_policy_ids=[],
                denied_policy_ids=[],
                reason_codes=["IDENTITY_NOT_VERIFIED"],
                decision_reason=f"Identity verification failed: {id_res.verification_reason}",
                highest_priority=0,
                evaluated_at=now,
            )

        # 2. Intent Subsystem Evaluation Pipeline (Phases 197–199)
        declared_intent_raw = (context.metadata or {}).get("declared_intent")
        if declared_intent_raw and isinstance(declared_intent_raw, dict):
            declared_obj = DeclaredIntent(**declared_intent_raw)
            # Phase 197: Verify Intent
            intent_req = IntentVerificationRequest(
                tenant_id=tenant_id,
                agent_id=agent_id,
                principal_id=context.principal_id,
                declared_intent=declared_obj,
                requested_action=context.requested_action or "payment",
                requested_amount=context.amount,
                requested_currency=context.currency,
                requested_merchant_id=context.merchant_id,
                requested_category=context.category,
            )
            intent_v_res = self.intent_verification_service.verify_intent(intent_req)

            # Phase 198: Match Intent Signals
            match_req = IntentMatchRequest(
                declared_intent=declared_obj,
                requested_action=context.requested_action or "payment",
                requested_amount=context.amount,
                requested_currency=context.currency,
                requested_merchant_id=str(context.merchant_id) if context.merchant_id else None,
                requested_category=context.category,
            )
            match_res = self.intent_matching_service.match_intent(match_req)

            # Phase 199: Mismatch Detection
            mismatch_req = IntentMismatchDetectionRequest(
                tenant_id=tenant_id,
                agent_id=agent_id,
                match_result=match_res,
            )
            mismatch_res = self.intent_mismatch_service.detect_mismatches(mismatch_req)

            if not mismatch_res.can_proceed or not intent_v_res.verified:
                return PolicyEvaluationResult(
                    agent_id=agent_id,
                    tenant_id=tenant_id,
                    decision="DENIED",
                    evaluated_policy_ids=[],
                    matched_policy_ids=[],
                    denied_policy_ids=[],
                    reason_codes=mismatch_res.reason_codes or [intent_v_res.reason_code],
                    decision_reason=f"Intent evaluation failed: {mismatch_res.explanation}",
                    highest_priority=0,
                    evaluated_at=now,
                )

        # 3. Behaviour Subsystem Intelligence (Phases 200–205)
        # Phase 201 & 202: Baseline & Deviation
        baseline = await self.baseline_service.compute_baseline(db, tenant_id, agent_id)
        dev_req = BehaviourDeviationRequest(
            tenant_id=tenant_id,
            agent_id=agent_id,
            amount=context.amount,
            currency=context.currency,
            merchant_id=context.merchant_id,
            category=context.category,
            baseline=baseline,
        )
        dev_res = self.deviation_service.evaluate_deviation(dev_req)

        # Phase 203: Velocity Detection
        vel_req = VelocityDetectionRequest(
            tenant_id=tenant_id,
            agent_id=agent_id,
            window_minutes=60,
        )
        vel_res = await self.velocity_service.detect_velocity(db, vel_req)

        # Phase 204: Merchant Behaviour Analysis
        merchant_b_reason_codes: list[str] = []
        if context.merchant_id:
            m_b_req = MerchantBehaviourAnalysisRequest(
                tenant_id=tenant_id,
                agent_id=agent_id,
                merchant_id=context.merchant_id,
                amount=context.amount,
                currency=context.currency,
            )
            m_b_res = await self.merchant_behaviour_service.analyze_merchant_behaviour(db, m_b_req)
            merchant_b_reason_codes = m_b_res.reason_codes

        # Phase 205: Category Behaviour Analysis
        category_b_reason_codes: list[str] = []
        if context.category:
            c_b_req = CategoryBehaviourAnalysisRequest(
                tenant_id=tenant_id,
                agent_id=agent_id,
                category=context.category,
                amount=context.amount,
                currency=context.currency,
            )
            c_b_res = await self.category_behaviour_service.analyze_category_behaviour(db, c_b_req)
            category_b_reason_codes = c_b_res.reason_codes

        # Combine advisory reason codes from Behaviour Intelligence
        advisory_reason_codes = list(
            dict.fromkeys(
                (dev_res.reason_codes or [])
                + (vel_res.reason_codes or [])
                + merchant_b_reason_codes
                + category_b_reason_codes
            )
        )

        # 4. Resolve Active Security Policies in Tenant Scope
        stmt = (
            select(SecurityPolicy)
            .where(
                SecurityPolicy.tenant_id == tenant_id,
                SecurityPolicy.status == "active",
                SecurityPolicy.deleted_at.is_(None),
                or_(SecurityPolicy.starts_at.is_(None), SecurityPolicy.starts_at <= now),
                or_(SecurityPolicy.ends_at.is_(None), SecurityPolicy.ends_at >= now),
            )
            .order_by(SecurityPolicy.priority.desc(), SecurityPolicy.id.asc())
        )

        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res

        raw_policies: list[SecurityPolicy] = []
        if hasattr(res, "scalars") and callable(getattr(res, "scalars", None)):

            try:
                sc = res.scalars()
                if inspect.isawaitable(sc):
                    sc = await sc
                if hasattr(sc, "all") and callable(getattr(sc, "all", None)):
                    all_p = sc.all()
                    if inspect.isawaitable(all_p):
                        all_p = await all_p
                    if isinstance(all_p, (list, tuple, set)):
                        raw_policies = list(all_p)
            except Exception:
                raw_policies = []


        if not raw_policies:
            logger.info("No active policies found for tenant %s", tenant_id)
            return PolicyEvaluationResult(
                agent_id=agent_id,
                tenant_id=tenant_id,
                decision="NO_APPLICABLE_POLICY",
                evaluated_policy_ids=[],
                matched_policy_ids=[],
                denied_policy_ids=[],
                reason_codes=advisory_reason_codes + ["NO_APPLICABLE_POLICY"],
                decision_reason="No active policies found for tenant scope.",
                highest_priority=0,
                evaluated_at=now,
            )

        # 5. Phase 196: Deterministic Priority Sorting
        sorted_policies: list[SecurityPolicy] = self.priority_service.sort_policies_by_priority(
            raw_policies
        )

        # 6. Phase 194: Time-Based Eligibility Filtering
        eligible_policies: list[SecurityPolicy] = []
        for p in sorted_policies:
            cfg = p.configuration or {}
            time_req = TimeBasedPolicyEvaluationRequest(
                tenant_id=tenant_id,
                agent_id=agent_id,
                evaluation_time=now,
                starts_at=p.starts_at,
                ends_at=p.ends_at,
                time_window_start=cfg.get("time_window_start"),
                time_window_end=cfg.get("time_window_end"),
                allowed_days=cfg.get("allowed_days", []),
                timezone=cfg.get("timezone", "UTC"),
            )
            time_res = self.time_service.evaluate_time_eligibility(time_req)
            if time_res.is_eligible:
                eligible_policies.append(p)

        if not eligible_policies:
            return PolicyEvaluationResult(
                agent_id=agent_id,
                tenant_id=tenant_id,
                decision="NO_APPLICABLE_POLICY",
                evaluated_policy_ids=[p.id for p in sorted_policies],
                matched_policy_ids=[],
                denied_policy_ids=[],
                reason_codes=advisory_reason_codes + ["OUTSIDE_EFFECTIVE_TIME_WINDOW"],
                decision_reason="All active policies are currently outside their effective time windows.",  # noqa: E501
                highest_priority=0,
                evaluated_at=now,
            )

        # 7. Policy & Engine Evaluation Loop (Building Candidates for Phase 195 Conflict Resolution)
        evaluated_ids: list[uuid.UUID] = []
        matched_ids: list[uuid.UUID] = []
        denied_ids: list[uuid.UUID] = []
        reason_codes: list[str] = list(advisory_reason_codes)
        candidates: list[PolicyCandidate] = []
        highest_priority = eligible_policies[0].priority if eligible_policies else 0

        # Inject Behaviour Deviation/Velocity advisory signal candidate if critical/high
        if vel_res.severity in ("CRITICAL", "HIGH") or (
            dev_res.has_deviation and dev_res.severity in ("CRITICAL", "HIGH")
        ):
            candidates.append(
                PolicyCandidate(
                    policy_id=eligible_policies[0].id,
                    decision="REQUIRE_APPROVAL",
                    priority=highest_priority,
                    specificity=1,
                    reason_code="BEHAVIOURAL_RISK_HIGH",
                )
            )

        rule_ctx = PolicyRuleContext(
            tenant_id=tenant_id,
            agent_id=agent_id,
            principal_id=context.principal_id,
            transaction_id=context.transaction_id,
            merchant_id=context.merchant_id,
            category=context.category,
            amount=context.amount,
            currency=context.currency,
            timestamp=now,
            requested_action=context.requested_action,
            tool_name=context.tool_name,
            metadata=context.metadata,
        )

        for p in eligible_policies:
            evaluated_ids.append(p.id)
            matched_ids.append(p.id)
            config = p.configuration or {}
            specificity = 3 if context.merchant_id else (2 if context.category else 1)

            if p.enforcement_mode == "block":
                denied_ids.append(p.id)
                reason_codes.append(f"BLOCKED_BY_POLICY_{p.slug.upper()}")
                candidates.append(
                    PolicyCandidate(
                        policy_id=p.id,
                        decision="DENIED",
                        priority=p.priority,
                        specificity=specificity,
                        reason_code=f"BLOCKED_BY_POLICY_{p.slug.upper()}",
                    )
                )
            elif p.enforcement_mode == "warn":
                reason_codes.append(f"APPROVAL_REQUIRED_BY_{p.slug.upper()}")
                candidates.append(
                    PolicyCandidate(
                        policy_id=p.id,
                        decision="REQUIRE_APPROVAL",
                        priority=p.priority,
                        specificity=specificity,
                        reason_code=f"APPROVAL_REQUIRED_BY_{p.slug.upper()}",
                    )
                )

            # 7a. Transaction Threshold Engine Evaluation (Phase 191)
            if context.amount is not None:
                min_amt = (
                    Decimal(str(config.get("minimum_transaction_amount")))
                    if config.get("minimum_transaction_amount") is not None
                    else None
                )
                max_amt = (
                    Decimal(str(config.get("maximum_transaction_amount")))
                    if config.get("maximum_transaction_amount") is not None
                    else (
                        Decimal(str(config.get("max_transaction_amount")))
                        if config.get("max_transaction_amount") is not None
                        else None
                    )
                )
                app_amt = (
                    Decimal(str(config.get("approval_threshold")))
                    if config.get("approval_threshold") is not None
                    else None
                )

                if min_amt is not None or max_amt is not None or app_amt is not None:
                    thresh_req = TransactionThresholdEvaluationRequest(
                        tenant_id=tenant_id,
                        agent_id=agent_id,
                        amount=context.amount,
                        currency=context.currency,
                        minimum_amount=min_amt,
                        maximum_amount=max_amt,
                        approval_threshold=app_amt,
                        threshold_currency=config.get("currency", "USD"),
                        enforcement_mode=p.enforcement_mode,
                    )
                    thresh_res = self.threshold_service.evaluate_threshold(thresh_req)
                    reason_codes.append(thresh_res.reason_code)
                    if thresh_res.decision == "DENIED":
                        denied_ids.append(p.id)
                        candidates.append(
                            PolicyCandidate(
                                policy_id=p.id,
                                decision="DENIED",
                                priority=p.priority,
                                specificity=specificity,
                                reason_code=thresh_res.reason_code,
                            )
                        )
                    elif thresh_res.decision == "REQUIRE_APPROVAL":
                        candidates.append(
                            PolicyCandidate(
                                policy_id=p.id,
                                decision="REQUIRE_APPROVAL",
                                priority=p.priority,
                                specificity=specificity,
                                reason_code=thresh_res.reason_code,
                            )
                        )

            # 7b. Single & Daily Spending Limit Engines (Phases 189 & 190)
            if context.amount is not None and config:
                max_spending = config.get("max_transaction_amount")
                if max_spending is not None:
                    limit_req = SpendingLimitEvaluationRequest(
                        tenant_id=tenant_id,
                        agent_id=agent_id,
                        amount=context.amount,
                        currency=context.currency,
                        configured_limit=Decimal(str(max_spending)),
                        limit_currency=config.get("currency", "USD"),
                        enforcement_mode=p.enforcement_mode,
                    )
                    sl_res = self.spending_service.evaluate_spending_limit(limit_req)
                    reason_codes.append(sl_res.reason_code)
                    if sl_res.decision in ("LIMIT_EXCEEDED", "INVALID_CURRENCY", "INVALID_AMOUNT"):
                        denied_ids.append(p.id)
                        candidates.append(
                            PolicyCandidate(
                                policy_id=p.id,
                                decision="DENIED",
                                priority=p.priority,
                                specificity=specificity,
                                reason_code=sl_res.reason_code,
                            )
                        )
                    elif sl_res.decision == "REQUIRES_APPROVAL":
                        candidates.append(
                            PolicyCandidate(
                                policy_id=p.id,
                                decision="REQUIRE_APPROVAL",
                                priority=p.priority,
                                specificity=specificity,
                                reason_code=sl_res.reason_code,
                            )
                        )

                daily_limit_raw = config.get("daily_spending_limit")
                if daily_limit_raw is not None:
                    daily_limit = Decimal(str(daily_limit_raw))
                    daily_res = await self.daily_spending_service.evaluate_daily_spending_limit(
                        db,
                        tenant_id=tenant_id,
                        agent_id=agent_id,
                        amount=context.amount,
                        configured_daily_limit=daily_limit,
                        currency=context.currency,
                        limit_currency=config.get("currency", "USD"),
                        enforcement_mode=p.enforcement_mode,
                    )
                    reason_codes.append(daily_res.reason_code)
                    if daily_res.decision in (
                        "LIMIT_EXCEEDED",
                        "INVALID_CURRENCY",
                        "INVALID_AMOUNT",
                    ):
                        denied_ids.append(p.id)
                        candidates.append(
                            PolicyCandidate(
                                policy_id=p.id,
                                decision="DENIED",
                                priority=p.priority,
                                specificity=specificity,
                                reason_code=daily_res.reason_code,
                            )
                        )
                    elif daily_res.decision == "REQUIRES_APPROVAL":
                        candidates.append(
                            PolicyCandidate(
                                policy_id=p.id,
                                decision="REQUIRE_APPROVAL",
                                priority=p.priority,
                                specificity=specificity,
                                reason_code=daily_res.reason_code,
                            )
                        )

            # 7c. Category Restriction Engine Evaluation (Phase 192)
            allowed_cats = config.get("allowed_categories", [])
            blocked_cats = config.get("blocked_categories", [])
            if allowed_cats or blocked_cats:
                cat_req = CategoryRestrictionEvaluationRequest(
                    tenant_id=tenant_id,
                    agent_id=agent_id,
                    category=context.category,
                    allowed_categories=allowed_cats,
                    blocked_categories=blocked_cats,
                )
                cat_res = self.category_service.evaluate_category_restriction(cat_req)
                reason_codes.append(cat_res.reason_code)
                if cat_res.decision == "DENIED":
                    denied_ids.append(p.id)
                    candidates.append(
                        PolicyCandidate(
                            policy_id=p.id,
                            decision="DENIED",
                            priority=p.priority,
                            specificity=specificity,
                            reason_code=cat_res.reason_code,
                        )
                    )
                elif cat_res.decision == "REQUIRE_APPROVAL":
                    candidates.append(
                        PolicyCandidate(
                            policy_id=p.id,
                            decision="REQUIRE_APPROVAL",
                            priority=p.priority,
                            specificity=specificity,
                            reason_code=cat_res.reason_code,
                        )
                    )

            # 7d. Merchant Restriction Engine Evaluation (Phase 193)
            allowed_merch = config.get("allowed_merchants", [])
            blocked_merch = config.get("blocked_merchants", [])
            if allowed_merch or blocked_merch or context.merchant_id:
                merch_req = MerchantRestrictionEvaluationRequest(
                    tenant_id=tenant_id,
                    agent_id=agent_id,
                    merchant_id=context.merchant_id,
                    allowed_merchants=allowed_merch,
                    blocked_merchants=blocked_merch,
                )
                merch_res = await self.merchant_service.evaluate_merchant_restriction(db, merch_req)
                reason_codes.append(merch_res.reason_code)
                if merch_res.decision == "DENIED":
                    denied_ids.append(p.id)
                    candidates.append(
                        PolicyCandidate(
                            policy_id=p.id,
                            decision="DENIED",
                            priority=p.priority,
                            specificity=specificity,
                            reason_code=merch_res.reason_code,
                        )
                    )
                elif merch_res.decision == "REQUIRE_APPROVAL":
                    candidates.append(
                        PolicyCandidate(
                            policy_id=p.id,
                            decision="REQUIRE_APPROVAL",
                            priority=p.priority,
                            specificity=specificity,
                            reason_code=merch_res.reason_code,
                        )
                    )

            # 7e. Evaluate PolicyRules associated with policy (Phase 188)
            rule_stmt = (
                select(PolicyRule)
                .where(
                    PolicyRule.security_policy_id == p.id,
                    PolicyRule.tenant_id == tenant_id,
                    PolicyRule.status == "active",
                    PolicyRule.deleted_at.is_(None),
                )
                .order_by(PolicyRule.priority.desc(), PolicyRule.id.asc())
            )
            r_res = db.execute(rule_stmt)
            if inspect.isawaitable(r_res):
                r_res = await r_res

            p_rules: list[PolicyRule] = []
            if hasattr(r_res, "scalars") and callable(getattr(r_res, "scalars", None)):
                try:
                    sc_r = r_res.scalars()
                    if inspect.isawaitable(sc_r):
                        sc_r = await sc_r
                    if hasattr(sc_r, "all") and callable(getattr(sc_r, "all", None)):
                        all_r = sc_r.all()
                        if inspect.isawaitable(all_r):
                            all_r = await all_r
                        if isinstance(all_r, (list, tuple, set)):
                            p_rules = list(all_r)
                except Exception:
                    p_rules = []


            for r in p_rules:
                if hasattr(r, "operator"):
                    r_eval: PolicyRuleResult = self.rule_engine.evaluate_rule(r, rule_ctx)
                    reason_codes.append(r_eval.reason_code)
                    if r_eval.outcome == "DENY":
                        denied_ids.append(p.id)
                        candidates.append(
                            PolicyCandidate(
                                policy_id=p.id,
                                rule_id=r.id,
                                decision="DENIED",
                                priority=p.priority,
                                specificity=specificity,
                                reason_code=r_eval.reason_code,
                            )
                        )
                    elif r_eval.outcome == "REQUIRE_APPROVAL":
                        candidates.append(
                            PolicyCandidate(
                                policy_id=p.id,
                                rule_id=r.id,
                                decision="REQUIRE_APPROVAL",
                                priority=p.priority,
                                specificity=specificity,
                                reason_code=r_eval.reason_code,
                            )
                        )

            # If no restrictions failed for this policy, record explicit ALLOW candidate
            if not any(c.policy_id == p.id and c.decision != "ALLOW" for c in candidates):
                candidates.append(
                    PolicyCandidate(
                        policy_id=p.id,
                        decision="ALLOW",
                        priority=p.priority,
                        specificity=specificity,
                        reason_code="POLICY_ALLOWED",
                    )
                )

        # 8. Phase 195: Policy Conflict Resolution Engine Call
        conflict_res = self.conflict_service.resolve_conflicts(candidates)
        reason_codes.append(conflict_res.decision)

        return PolicyEvaluationResult(
            agent_id=agent_id,
            tenant_id=tenant_id,
            decision=conflict_res.decision,
            evaluated_policy_ids=list(dict.fromkeys(evaluated_ids)),
            matched_policy_ids=list(dict.fromkeys(matched_ids)),
            denied_policy_ids=list(dict.fromkeys(denied_ids)),
            reason_codes=list(dict.fromkeys(reason_codes)),
            decision_reason=conflict_res.resolution_reason,
            highest_priority=highest_priority,
            evaluated_at=now,
        )
