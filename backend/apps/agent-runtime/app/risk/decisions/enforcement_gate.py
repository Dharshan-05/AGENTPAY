"""Decision Enforcement Gate (Phase 285)."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime

from app.schemas.risk_engine import (
    DecisionEnforcementResult,
    EnforcementOutcome,
    FinalRiskDecision,
    FinalRiskDecisionResult,
    RiskEvaluationContext,
)

logger = logging.getLogger("agentpay.risk.decisions.enforcement")


class DecisionEnforcementGate:
    """Production Decision Enforcement Gate (Phase 285).

    The authoritative boundary before transaction execution. Enforces ALLOW/REVIEW/BLOCK semantics
    and verifies cryptographic decision fingerprints, point-in-time freshness, and identity binding.
    """

    def _compute_enforcement_fingerprint(
        self,
        decision_id: str,
        evaluation_id: str,
        tenant_id: str,
        agent_id: str,
        transaction_id: str,
        enforcement_outcome: str,
        execution_permitted: bool,
        reason_code: str,
    ) -> str:
        """Compute SHA-256 fingerprint for enforcement outcome."""
        payload = {
            "decision_id": decision_id,
            "evaluation_id": evaluation_id,
            "tenant_id": tenant_id,
            "agent_id": agent_id,
            "transaction_id": transaction_id,
            "enforcement_outcome": enforcement_outcome,
            "execution_permitted": execution_permitted,
            "reason_code": reason_code,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def enforce_decision(
        self,
        decision_result: FinalRiskDecisionResult,
        execution_context: RiskEvaluationContext,
        max_decision_age_seconds: float = 300.0,
    ) -> DecisionEnforcementResult:
        """Enforce authoritative final risk decision at execution boundary (Phase 285)."""
        logger.info(
            "Enforcing final risk decision %s for tx=%s (tenant=%s, agent=%s)",
            decision_result.decision_id,
            execution_context.transaction_id,
            execution_context.tenant_id,
            execution_context.agent_id,
        )

        # 1. Identity Binding Defense-in-Depth
        if decision_result.tenant_id != execution_context.tenant_id:
            logger.error("Enforcement failed: tenant mismatch!")
            return self._build_denied_result(
                decision_result, execution_context, "IDENTITY_TENANT_MISMATCH"
            )

        if decision_result.agent_id != execution_context.agent_id:
            logger.error("Enforcement failed: agent mismatch!")
            return self._build_denied_result(
                decision_result, execution_context, "IDENTITY_AGENT_MISMATCH"
            )

        if decision_result.transaction_id != execution_context.transaction_id:
            logger.error("Enforcement failed: transaction mismatch!")
            return self._build_denied_result(
                decision_result, execution_context, "IDENTITY_TRANSACTION_MISMATCH"
            )

        # 2. Point-in-Time Freshness & Stale Decision Check
        now = datetime.now(UTC)
        age = (now - decision_result.created_at).total_seconds()
        if age < 0 or age > max_decision_age_seconds:
            logger.error("Enforcement failed: stale or future decision (age=%.2fs)", age)
            return self._build_denied_result(
                decision_result, execution_context, "STALE_OR_FUTURE_DECISION"
            )

        # 3. Decision Fingerprint Re-Verification (Tamper Detection)
        recomputed_fp = self._recompute_decision_fingerprint(decision_result)
        if recomputed_fp != decision_result.decision_fingerprint:
            logger.error("Enforcement failed: decision fingerprint tampering detected!")
            return self._build_denied_result(
                decision_result, execution_context, "FINGERPRINT_TAMPERING_DETECTED"
            )

        # 4. Enforce Authoritative Final Decision Semantics
        if decision_result.decision == FinalRiskDecision.ALLOW:
            # ALLOW -> PERMITTED ONLY IF all policy and security conditions passed
            if decision_result.policy_precedence.upper() == "DENY":
                return self._build_denied_result(
                    decision_result, execution_context, "POLICY_DENY_ENFORCED"
                )

            enf_fp = self._compute_enforcement_fingerprint(
                decision_id=str(decision_result.decision_id),
                evaluation_id=str(decision_result.evaluation_id),
                tenant_id=str(execution_context.tenant_id),
                agent_id=str(execution_context.agent_id),
                transaction_id=execution_context.transaction_id,
                enforcement_outcome=EnforcementOutcome.PERMITTED.value,
                execution_permitted=True,
                reason_code="EXECUTION_PERMITTED_ALLOW",
            )
            return DecisionEnforcementResult(
                decision_id=decision_result.decision_id,
                evaluation_id=decision_result.evaluation_id,
                tenant_id=execution_context.tenant_id,
                agent_id=execution_context.agent_id,
                transaction_id=execution_context.transaction_id,
                enforcement_outcome=EnforcementOutcome.PERMITTED,
                execution_permitted=True,
                execution_suspended=False,
                approval_required=False,
                authorization_denied=False,
                reason_code="EXECUTION_PERMITTED_ALLOW",
                enforcement_fingerprint=enf_fp,
            )

        elif decision_result.decision == FinalRiskDecision.REVIEW:
            # REVIEW -> SUSPENDED (Execution prohibited without human approval)
            enf_fp = self._compute_enforcement_fingerprint(
                decision_id=str(decision_result.decision_id),
                evaluation_id=str(decision_result.evaluation_id),
                tenant_id=str(execution_context.tenant_id),
                agent_id=str(execution_context.agent_id),
                transaction_id=execution_context.transaction_id,
                enforcement_outcome=EnforcementOutcome.SUSPENDED.value,
                execution_permitted=False,
                reason_code=f"EXECUTION_SUSPENDED_{decision_result.decision_reason}",
            )
            return DecisionEnforcementResult(
                decision_id=decision_result.decision_id,
                evaluation_id=decision_result.evaluation_id,
                tenant_id=execution_context.tenant_id,
                agent_id=execution_context.agent_id,
                transaction_id=execution_context.transaction_id,
                enforcement_outcome=EnforcementOutcome.SUSPENDED,
                execution_permitted=False,
                execution_suspended=True,
                approval_required=True,
                authorization_denied=False,
                reason_code=f"EXECUTION_SUSPENDED_{decision_result.decision_reason}",
                enforcement_fingerprint=enf_fp,
            )

        else:
            # BLOCK or unknown -> DENIED
            return self._build_denied_result(
                decision_result,
                execution_context,
                f"AUTHORIZATION_DENIED_{decision_result.decision_reason}",  # noqa: E501
            )

    def _build_denied_result(
        self,
        decision_result: FinalRiskDecisionResult,
        execution_context: RiskEvaluationContext,
        reason_code: str,
    ) -> DecisionEnforcementResult:
        enf_fp = self._compute_enforcement_fingerprint(
            decision_id=str(decision_result.decision_id),
            evaluation_id=str(decision_result.evaluation_id),
            tenant_id=str(execution_context.tenant_id),
            agent_id=str(execution_context.agent_id),
            transaction_id=execution_context.transaction_id,
            enforcement_outcome=EnforcementOutcome.DENIED.value,
            execution_permitted=False,
            reason_code=reason_code,
        )
        return DecisionEnforcementResult(
            decision_id=decision_result.decision_id,
            evaluation_id=decision_result.evaluation_id,
            tenant_id=execution_context.tenant_id,
            agent_id=execution_context.agent_id,
            transaction_id=execution_context.transaction_id,
            enforcement_outcome=EnforcementOutcome.DENIED,
            execution_permitted=False,
            execution_suspended=False,
            approval_required=False,
            authorization_denied=True,
            reason_code=reason_code,
            enforcement_fingerprint=enf_fp,
        )

    def _recompute_decision_fingerprint(self, decision_result: FinalRiskDecisionResult) -> str:
        payload = {
            "evaluation_id": str(decision_result.evaluation_id),
            "tenant_id": str(decision_result.tenant_id),
            "agent_id": str(decision_result.agent_id),
            "transaction_id": decision_result.transaction_id,
            "prediction_timestamp": decision_result.prediction_timestamp.isoformat(),
            "decision": decision_result.decision.value,
            "decision_reason": decision_result.decision_reason,
            "composite_risk_score": decision_result.composite_risk_score,
            "risk_band": decision_result.risk_band.value,
            "policy_precedence": decision_result.policy_precedence,
            "calculation_fingerprint": decision_result.calculation_fingerprint,
            "source_fingerprints": sorted(decision_result.source_fingerprints),
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
