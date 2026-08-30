"""Approval Policy Engine Subsystem (Phase 301)."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from decimal import Decimal

from app.schemas.payment import SupportedCurrency
from app.schemas.payment_approval import (
    ApprovalDecisionRecord,
    ApprovalPolicy,
    ApprovalRequest,
    ApprovalStatus,
)
from app.schemas.risk_engine import FinalRiskDecision, FinalRiskDecisionResult

logger = logging.getLogger("agentpay.payment.approval")


class ApprovalPolicyEngineError(Exception):
    """Domain exception raised when approval policy evaluation fails."""

    def __init__(self, message: str, error_code: str = "APPROVAL_POLICY_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ApprovalPolicyEngine:
    """Production Approval Policy Engine (Phase 301).

    Primary responsibility: Deterministically derive human-in-the-loop approval requirements.
    - Low Risk / Low Value -> NOT_REQUIRED.
    - High Risk / High Value / Review Decision -> PENDING.
    - CRITICAL INVARIANT: Agent CANNOT set approval_status = APPROVED!
    - Execution Gate: Payment execution CANNOT proceed while approval_status == PENDING.
    """

    def __init__(self, policy: ApprovalPolicy | None = None) -> None:
        self.policy = policy or ApprovalPolicy()

    def evaluate_approval_requirement(
        self,
        decision_result: FinalRiskDecisionResult,
        amount: Decimal,
        currency: SupportedCurrency,
        order_id: str | None = None,
        payment_id: str | None = None,
        operation: str = "payment",
    ) -> ApprovalRequest:
        """Evaluate approval requirement for a payment request (Phase 301)."""
        logger.info(
            "ApprovalPolicyEngine evaluating requirement for tx=%s (score=%s, amount=%s %s)",
            decision_result.transaction_id,
            decision_result.composite_risk_score,
            amount,
            currency.value,
        )

        # 1. Deterministic Policy Evaluation
        requires_approval = False
        reason = "LOW_RISK_LOW_VALUE"

        if decision_result.decision == FinalRiskDecision.REVIEW:
            requires_approval = True
            reason = "RISK_DECISION_REVIEW_REQUIRED"
        elif (
            self.policy.require_approval_for_high_risk
            and decision_result.composite_risk_score > self.policy.auto_approval_risk_cutoff
        ):
            requires_approval = True
            reason = "HIGH_RISK_SCORE_THRESHOLD_EXCEEDED"
        elif amount > self.policy.high_value_threshold:
            requires_approval = True
            reason = "HIGH_VALUE_THRESHOLD_EXCEEDED"

        initial_status = (
            ApprovalStatus.PENDING if requires_approval else ApprovalStatus.NOT_REQUIRED
        )

        # 2. Compute Approval Fingerprint
        approval_id = uuid.uuid4()
        fingerprint = self.calculate_approval_fingerprint(
            approval_id=approval_id,
            tenant_id=decision_result.tenant_id,
            agent_id=decision_result.agent_id,
            transaction_id=decision_result.transaction_id,
            order_id=order_id,
            payment_id=payment_id,
            status=initial_status,
            risk_score=decision_result.composite_risk_score,
            amount=amount,
            currency=currency,
            policy_version=self.policy.policy_version,
        )

        # 3. Create Approval Request Contract (Fails closed if status == APPROVED!)
        req = ApprovalRequest(
            approval_id=approval_id,
            tenant_id=decision_result.tenant_id,
            agent_id=decision_result.agent_id,
            transaction_id=decision_result.transaction_id,
            order_id=order_id,
            payment_id=payment_id,
            approval_status=initial_status,
            risk_score=decision_result.composite_risk_score,
            amount=amount,
            currency=currency,
            approval_fingerprint=fingerprint,
        )

        logger.info(
            "Approval evaluation outcome for tx=%s: status=%s (reason=%s)",
            decision_result.transaction_id,
            initial_status.value,
            reason,
        )
        return req

    def is_execution_permitted(
        self,
        request: ApprovalRequest,
        decision_record: ApprovalDecisionRecord | None = None,
    ) -> bool:
        """Check if payment execution is permitted given current approval status (Phase 301).

        - Returns True if status == NOT_REQUIRED or APPROVED (from valid human reviewer).
        - Returns False if status == PENDING, REJECTED, EXPIRED, or CANCELLED.
        """
        if request.approval_status == ApprovalStatus.NOT_REQUIRED:
            return True

        if decision_record is not None:
            if (
                decision_record.approval_id == request.approval_id
                and decision_record.decision_status == ApprovalStatus.APPROVED
            ):
                return True

        logger.warning(
            "Payment execution BLOCKED by Approval Engine for tx=%s (status=%s)",
            request.transaction_id,
            request.approval_status.value,
        )
        return False

    def calculate_approval_fingerprint(
        self,
        approval_id: uuid.UUID,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        transaction_id: str,
        status: ApprovalStatus,
        risk_score: float,
        amount: Decimal,
        currency: SupportedCurrency,
        policy_version: str,
        order_id: str | None = None,
        payment_id: str | None = None,
    ) -> str:
        """Calculate deterministic SHA-256 fingerprint over canonical approval metadata."""
        canonical = {
            "approval_id": str(approval_id),
            "tenant_id": str(tenant_id),
            "agent_id": str(agent_id),
            "transaction_id": transaction_id,
            "order_id": order_id or "",
            "payment_id": payment_id or "",
            "approval_status": status.value,
            "risk_score": risk_score,
            "amount": str(amount),
            "currency": currency.value,
            "policy_version": policy_version,
        }
        encoded = json.dumps(canonical, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
