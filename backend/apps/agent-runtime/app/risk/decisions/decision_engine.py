"""Centralized Final Risk Decision Engine (Phases 278-280)."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime
from typing import Any

from app.risk.decisions.allow_decision import AllowDecisionEngine
from app.risk.decisions.block_decision import BlockDecisionEngine
from app.risk.decisions.review_decision import ReviewDecisionEngine
from app.schemas.risk_engine import (
    FinalRiskDecision,
    FinalRiskDecisionResult,
    HardSecurityEvaluationResult,
    RiskEvaluationContext,
    RiskScoreCalculationResult,
    RiskThresholdEvaluationResult,
)

logger = logging.getLogger("agentpay.risk.decisions.engine")


class FinalRiskDecisionEngine:
    """Production Centralized Final Risk Decision Engine (Phases 278-280)."""

    def __init__(
        self,
        allow_engine: AllowDecisionEngine | None = None,
        review_engine: ReviewDecisionEngine | None = None,
        block_engine: BlockDecisionEngine | None = None,
    ) -> None:
        self.allow_engine = allow_engine or AllowDecisionEngine()
        self.review_engine = review_engine or ReviewDecisionEngine()
        self.block_engine = block_engine or BlockDecisionEngine()

    def _compute_decision_fingerprint(
        self,
        evaluation_id: Any,
        tenant_id: Any,
        agent_id: Any,
        transaction_id: str,
        prediction_timestamp: datetime,
        decision: str,
        decision_reason: str,
        composite_risk_score: float,
        risk_band: str,
        policy_precedence: str,
        calculation_fingerprint: str,
        source_fingerprints: list[str],
    ) -> str:
        """Compute byte-identical SHA-256 fingerprint for final decision outcome."""
        payload = {
            "evaluation_id": str(evaluation_id),
            "tenant_id": str(tenant_id),
            "agent_id": str(agent_id),
            "transaction_id": transaction_id,
            "prediction_timestamp": prediction_timestamp.isoformat(),
            "decision": decision,
            "decision_reason": decision_reason,
            "composite_risk_score": composite_risk_score,
            "risk_band": risk_band,
            "policy_precedence": policy_precedence,
            "calculation_fingerprint": calculation_fingerprint,
            "source_fingerprints": sorted(source_fingerprints),
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def evaluate_final_decision(
        self,
        context: RiskEvaluationContext,
        calc_result: RiskScoreCalculationResult,
        threshold_result: RiskThresholdEvaluationResult,
        security_result: HardSecurityEvaluationResult,
    ) -> FinalRiskDecisionResult:
        """Evaluate authoritative final risk decision (ALLOW, REVIEW, BLOCK) (Phases 278-280)."""  # noqa: E501
        logger.info(
            "Evaluating final risk decision for evaluation %s (tx=%s, tenant=%s)",
            context.evaluation_id,
            context.transaction_id,
            context.tenant_id,
        )

        # 1. Identity & Temporal Defense-in-Depth Validation
        if (
            calc_result.tenant_id != context.tenant_id
            or threshold_result.tenant_id != context.tenant_id
            or security_result.tenant_id != context.tenant_id
        ):
            raise ValueError(
                f"Tenant ID mismatch across decision components! Context tenant '{context.tenant_id}'"  # noqa: E501
            )

        if (
            calc_result.agent_id != context.agent_id
            or threshold_result.agent_id != context.agent_id
            or security_result.agent_id != context.agent_id
        ):
            raise ValueError(
                f"Agent ID mismatch across decision components! Context agent '{context.agent_id}'"  # noqa: E501
            )

        if (
            calc_result.transaction_id != context.transaction_id
            or threshold_result.transaction_id != context.transaction_id
            or security_result.transaction_id != context.transaction_id
        ):
            raise ValueError(
                f"Transaction ID mismatch across decision components! Context tx '{context.transaction_id}'"  # noqa: E501
            )

        # 2. Evaluate Individual Decision Engines
        is_block, block_reasons = self.block_engine.evaluate_block(
            context, calc_result, threshold_result, security_result
        )

        is_review, review_reasons = self.review_engine.evaluate_review(
            context, calc_result, threshold_result, security_result
        )

        is_allow, allow_reasons = self.allow_engine.evaluate_allow(
            context, calc_result, threshold_result, security_result
        )

        # 3. Deterministic Precedence Resolution
        # PRIORITY 1: BLOCK
        if is_block:
            final_dec = FinalRiskDecision.BLOCK
            primary_reason = block_reasons[0] if block_reasons else "BLOCK_SECURITY_RESTRICTION"
        # PRIORITY 2: REVIEW
        elif is_review:
            final_dec = FinalRiskDecision.REVIEW
            primary_reason = review_reasons[0] if review_reasons else "REVIEW_SECURITY_INTERVENTION"
        # PRIORITY 3: ALLOW
        elif is_allow:
            final_dec = FinalRiskDecision.ALLOW
            primary_reason = allow_reasons[0] if allow_reasons else "LOW_RISK_ALLOW_CLEAN"
        # PRIORITY 4: Fail-Closed Fallback (If not cleanly ALLOW, default to REVIEW!)
        else:
            final_dec = FinalRiskDecision.REVIEW
            primary_reason = "FAIL_CLOSED_SAFETY_REVIEW"

        # Extract metadata
        triggered_rule_ids = [r.rule_id for r in security_result.triggered_rules]
        sec_status = (
            "PASSED"
            if not security_result.has_triggered_rules
            else f"TRIGGERED_{security_result.max_triggered_severity.value if security_result.max_triggered_severity else 'RULES'}"  # noqa: E501
        )
        is_cold_start = any("cold_start" in s for s in calc_result.excluded_signal_types)

        # 4. Compute SHA-256 Decision Fingerprint
        decision_fp = self._compute_decision_fingerprint(
            evaluation_id=context.evaluation_id,
            tenant_id=context.tenant_id,
            agent_id=context.agent_id,
            transaction_id=context.transaction_id,
            prediction_timestamp=context.prediction_timestamp,
            decision=final_dec.value,
            decision_reason=primary_reason,
            composite_risk_score=calc_result.composite_risk_score,
            risk_band=threshold_result.matched_threshold_band.value,
            policy_precedence=calc_result.policy_precedence,
            calculation_fingerprint=calc_result.calculation_fingerprint,
            source_fingerprints=calc_result.source_fingerprints,
        )

        return FinalRiskDecisionResult(
            evaluation_id=context.evaluation_id,
            tenant_id=context.tenant_id,
            agent_id=context.agent_id,
            transaction_id=context.transaction_id,
            prediction_timestamp=context.prediction_timestamp,
            decision=final_dec,
            decision_reason=primary_reason,
            composite_risk_score=calc_result.composite_risk_score,
            risk_band=threshold_result.matched_threshold_band,
            policy_precedence=calc_result.policy_precedence,
            hard_security_status=sec_status,
            triggered_rule_ids=triggered_rule_ids,
            review_reasons=review_reasons,
            block_reasons=block_reasons,
            available_signal_types=calc_result.available_signal_types,
            unavailable_signal_types=calc_result.unavailable_signal_types,
            cold_start=is_cold_start,
            policy_authoritative=True,
            threshold_configuration_version=threshold_result.configuration_version,
            threshold_configuration_hash=threshold_result.configuration_hash,
            weight_configuration_version=calc_result.weight_configuration_version,
            weight_configuration_hash=calc_result.weight_configuration_hash,
            source_fingerprints=calc_result.source_fingerprints,
            calculation_fingerprint=calc_result.calculation_fingerprint,
            decision_fingerprint=decision_fp,
        )
