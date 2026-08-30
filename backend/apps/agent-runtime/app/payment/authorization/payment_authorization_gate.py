"""Payment Authorization Gate (Phase 285)."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid

from app.risk.decisions.enforcement_gate import DecisionEnforcementGate
from app.schemas.payment_authorization import (
    PaymentAuthorizationOutcome,
    PaymentAuthorizationRequest,
    PaymentAuthorizationResult,
)
from app.schemas.risk_engine import (
    EnforcementOutcome,
    FinalRiskDecisionResult,
    RiskEvaluationContext,
)

logger = logging.getLogger("agentpay.payment.authorization.gate")


class PaymentAuthorizationGate:
    """Production Payment Authorization Gate (Phase 285).

    Establishes a hardened authorization boundary between authoritative risk decisions
    and future payment execution. Consumes authoritative FinalRiskDecisionResult without
    recalculating risk, scores, thresholds, weights, or policies.
    """

    def __init__(self, enforcement_gate: DecisionEnforcementGate | None = None) -> None:
        self.enforcement_gate = enforcement_gate or DecisionEnforcementGate()

    def _compute_authorization_fingerprint(
        self,
        authorization_id: str,
        decision_id: str,
        evaluation_id: str,
        tenant_id: str,
        agent_id: str,
        transaction_id: str,
        payment_reference: str | None,
        outcome: str,
        execution_permitted: bool,
        reason_code: str,
        decision_fingerprint: str,
    ) -> str:
        """Compute canonical SHA-256 fingerprint for payment authorization outcome."""
        payload = {
            "authorization_id": authorization_id,
            "decision_id": decision_id,
            "evaluation_id": evaluation_id,
            "tenant_id": tenant_id,
            "agent_id": agent_id,
            "transaction_id": transaction_id,
            "payment_reference": payment_reference or "",
            "outcome": outcome,
            "execution_permitted": execution_permitted,
            "reason_code": reason_code,
            "decision_fingerprint": decision_fingerprint,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def authorize_payment(
        self,
        decision_result: FinalRiskDecisionResult,
        request: PaymentAuthorizationRequest,
        max_decision_age_seconds: float = 300.0,
    ) -> PaymentAuthorizationResult:
        """Enforce payment authorization boundary against authoritative decision (Phase 285)."""
        logger.info(
            "Evaluating payment authorization gate for decision %s (tx=%s, tenant=%s, agent=%s)",
            decision_result.decision_id,
            request.transaction_id,
            request.tenant_id,
            request.agent_id,
        )

        # 1. Construct RiskEvaluationContext from PaymentAuthorizationRequest
        exec_ctx = RiskEvaluationContext(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            prediction_timestamp=request.authorization_timestamp,
            source_context=request.context_metadata,
        )

        # 2. Strict Identity Binding Check
        if decision_result.tenant_id != request.tenant_id:
            logger.error("Payment authorization failed: tenant mismatch!")
            return self._build_denied_result(decision_result, request, "IDENTITY_TENANT_MISMATCH")

        if decision_result.agent_id != request.agent_id:
            logger.error("Payment authorization failed: agent mismatch!")
            return self._build_denied_result(decision_result, request, "IDENTITY_AGENT_MISMATCH")

        if decision_result.transaction_id != request.transaction_id:
            logger.error("Payment authorization failed: transaction mismatch!")
            return self._build_denied_result(
                decision_result, request, "IDENTITY_TRANSACTION_MISMATCH"
            )

        # 3. Delegate to DecisionEnforcementGate for decision enforcement
        enf_res = self.enforcement_gate.enforce_decision(
            decision_result=decision_result,
            execution_context=exec_ctx,
            max_decision_age_seconds=max_decision_age_seconds,
        )

        # 4. Map Enforcement Outcome to Payment Authorization Outcome
        if enf_res.enforcement_outcome == EnforcementOutcome.PERMITTED:
            outcome = PaymentAuthorizationOutcome.PERMITTED
            permitted = True
            suspended = False
            approval = False
            denied = False
            reason_code = "PAYMENT_AUTHORIZATION_PERMITTED"
        elif enf_res.enforcement_outcome == EnforcementOutcome.SUSPENDED:
            outcome = PaymentAuthorizationOutcome.SUSPENDED
            permitted = False
            suspended = True
            approval = True
            denied = False
            reason_code = f"PAYMENT_AUTHORIZATION_SUSPENDED_{decision_result.decision_reason}"
        else:
            outcome = PaymentAuthorizationOutcome.DENIED
            permitted = False
            suspended = False
            approval = False
            denied = True
            reason_code = f"PAYMENT_AUTHORIZATION_DENIED_{enf_res.reason_code}"

        auth_id = str(uuid.uuid4())
        auth_fp = self._compute_authorization_fingerprint(
            authorization_id=auth_id,
            decision_id=str(decision_result.decision_id),
            evaluation_id=str(decision_result.evaluation_id),
            tenant_id=str(request.tenant_id),
            agent_id=str(request.agent_id),
            transaction_id=request.transaction_id,
            payment_reference=request.payment_reference,
            outcome=outcome.value,
            execution_permitted=permitted,
            reason_code=reason_code,
            decision_fingerprint=decision_result.decision_fingerprint,
        )

        return PaymentAuthorizationResult(
            authorization_id=uuid.UUID(auth_id),
            decision_id=decision_result.decision_id,
            evaluation_id=decision_result.evaluation_id,
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            payment_reference=request.payment_reference,
            outcome=outcome,
            execution_permitted=permitted,
            execution_suspended=suspended,
            approval_required=approval,
            authorization_denied=denied,
            reason_code=reason_code,
            decision_reason=decision_result.decision_reason,
            decision_fingerprint=decision_result.decision_fingerprint,
            authorization_fingerprint=auth_fp,
        )

    def _build_denied_result(
        self,
        decision_result: FinalRiskDecisionResult,
        request: PaymentAuthorizationRequest,
        reason_code: str,
    ) -> PaymentAuthorizationResult:
        auth_id = str(uuid.uuid4())
        auth_fp = self._compute_authorization_fingerprint(
            authorization_id=auth_id,
            decision_id=str(decision_result.decision_id),
            evaluation_id=str(decision_result.evaluation_id),
            tenant_id=str(request.tenant_id),
            agent_id=str(request.agent_id),
            transaction_id=request.transaction_id,
            payment_reference=request.payment_reference,
            outcome=PaymentAuthorizationOutcome.DENIED.value,
            execution_permitted=False,
            reason_code=reason_code,
            decision_fingerprint=decision_result.decision_fingerprint,
        )

        return PaymentAuthorizationResult(
            authorization_id=uuid.UUID(auth_id),
            decision_id=decision_result.decision_id,
            evaluation_id=decision_result.evaluation_id,
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            payment_reference=request.payment_reference,
            outcome=PaymentAuthorizationOutcome.DENIED,
            execution_permitted=False,
            execution_suspended=False,
            approval_required=False,
            authorization_denied=True,
            reason_code=reason_code,
            decision_reason=decision_result.decision_reason,
            decision_fingerprint=decision_result.decision_fingerprint,
            authorization_fingerprint=auth_fp,
        )
