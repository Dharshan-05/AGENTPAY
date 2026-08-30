"""Human Approval Workflow Service for AGENTPAY (Phase 162)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import select

from app.domain.exceptions.agent_exceptions import (
    ApprovalExpiredError,
    HumanApprovalError,
    SelfApprovalForbiddenError,
)
from app.infrastructure.database.models.approval_decision import ApprovalDecision
from app.infrastructure.database.models.approval_request import ApprovalRequest
from app.schemas.human_approval import (
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    ApprovalPolicyEvaluationResponse,
    ApprovalRequestCreate,
    ApprovalRequestResponse,
    ApprovalRiskLevel,
    ApprovalStatus,
)

logger = logging.getLogger(__name__)


class HumanApprovalWorkflowService:
    """Production service for human-in-the-loop approval workflows and self-approval security enforcement (Phase 162)."""  # noqa: E501

    async def evaluate_approval_policy(
        self,
        tenant_id: uuid.UUID,
        action_name: str,
        amount: float,
        currency: str = "USD",
    ) -> ApprovalPolicyEvaluationResponse:
        """Evaluate configurable approval policy based on risk level, amount thresholds, and action type (Phase 162)."""  # noqa: E501
        sensitive_actions = {"refund", "cancel", "override_security", "payout", "transfer"}

        if action_name in sensitive_actions or amount > 500.00:
            risk = ApprovalRiskLevel.HIGH
            req_count = 2
            req_approval = True
            auto_appr = False
            policy_name = "High Risk Multi-Approval Policy"
        elif amount > 50.00:
            risk = ApprovalRiskLevel.MEDIUM
            req_count = 1
            req_approval = True
            auto_appr = False
            policy_name = "Medium Risk Single Approval Policy"
        else:
            risk = ApprovalRiskLevel.LOW
            req_count = 0
            req_approval = False
            auto_appr = True
            policy_name = "Low Risk Auto-Approval Policy"

        return ApprovalPolicyEvaluationResponse(
            requires_approval=req_approval,
            risk_level=risk,
            required_approvals_count=req_count,
            matched_policy_name=policy_name,
            auto_approved=auto_appr,
        )

    async def create_approval_request(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        request: ApprovalRequestCreate,
        requesting_user_id: uuid.UUID | None = None,
    ) -> ApprovalRequestResponse:
        """Create a human approval request record in approval_requests table (Phase 162)."""
        policy_eval = await self.evaluate_approval_policy(
            tenant_id=tenant_id,
            action_name=request.action_name,
            amount=request.amount,
            currency=request.currency,
        )

        approval_id = uuid.uuid4()
        ref_code = f"APP-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(UTC)
        expires_at = now + timedelta(hours=24)

        status_str = ApprovalStatus.PENDING_APPROVAL.value
        if policy_eval.auto_approved:
            status_str = ApprovalStatus.AUTO_APPROVED.value

        appr_obj = ApprovalRequest(
            id=approval_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            requester_id=requesting_user_id,
            approval_reference=ref_code,
            approval_type="agent",
            requested_action=request.action_name,
            requested_amount=Decimal(str(request.amount)),
            currency_code=request.currency,
            risk_score=Decimal("0.85")
            if policy_eval.risk_level == ApprovalRiskLevel.HIGH
            else Decimal("0.30"),  # noqa: E501
            status=status_str.lower(),
            required_approvals=policy_eval.required_approvals_count,
            received_approvals=0,
            reason=request.reason,
            approval_context={
                "risk_level": policy_eval.risk_level.value,
                "context_data": request.context_data,
            },
            expires_at=expires_at,
            created_at=now,
            updated_at=now,
        )

        db.add(appr_obj)
        db.commit()
        db.refresh(appr_obj)

        logger.info(
            "Approval request %s created for agent %s in tenant %s (Status: %s, Ref: %s)",
            approval_id,
            agent_id,
            tenant_id,
            status_str,
            ref_code,
        )
        return self._build_request_response(appr_obj)

    async def record_approval_decision(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        approval_id: uuid.UUID,
        decision_req: ApprovalDecisionRequest,
        reviewer_id: uuid.UUID,
        reviewer_email: str | None = None,
    ) -> ApprovalDecisionResponse:
        """Record human reviewer decision with strict anti-self-approval enforcement (Phase 162)."""
        appr_obj = db.execute(
            select(ApprovalRequest).where(
                ApprovalRequest.id == approval_id,
                ApprovalRequest.tenant_id == tenant_id,
            )
        ).scalar_one_or_none()

        if not appr_obj:
            raise HumanApprovalError(f"Approval request {approval_id} not found.")

        # Check expiration
        now = datetime.now(UTC)
        if appr_obj.expires_at and appr_obj.expires_at.replace(tzinfo=UTC) < now:
            appr_obj.status = ApprovalStatus.EXPIRED.value.lower()
            db.add(appr_obj)
            db.commit()
            raise ApprovalExpiredError(f"Approval request {approval_id} has expired.")

        # -------------------------------------------------------------------
        # STRICT SECURITY RULE: SELF-APPROVAL PREVENTION
        # -------------------------------------------------------------------
        # An agent or requesting user can NEVER approve its own request.
        if (appr_obj.requester_id and reviewer_id == appr_obj.requester_id) or (
            appr_obj.agent_id and reviewer_id == appr_obj.agent_id
        ):
            raise SelfApprovalForbiddenError(
                "Self-approval security violation: Reviewer cannot approve their own requested transaction."  # noqa: E501
            )

        # Record decision
        decision_id = uuid.uuid4()
        dec_ref = f"DEC-{uuid.uuid4().hex[:8].upper()}"

        decision_obj = ApprovalDecision(
            id=decision_id,
            tenant_id=tenant_id,
            approval_request_id=approval_id,
            reviewer_id=reviewer_id,
            decision_reference=dec_ref,
            decision=decision_req.decision.lower(),
            reason=decision_req.reason,
            decided_at=now,
            created_at=now,
            updated_at=now,
        )
        db.add(decision_obj)

        # Update approval request state
        if decision_req.decision == "APPROVED":
            appr_obj.received_approvals += 1
            if appr_obj.received_approvals >= appr_obj.required_approvals:
                appr_obj.status = ApprovalStatus.APPROVED.value.lower()
            else:
                appr_obj.status = "partially_approved"
        elif decision_req.decision == "REJECTED":
            appr_obj.status = ApprovalStatus.REJECTED.value.lower()

        appr_obj.updated_at = now
        db.add(appr_obj)
        db.commit()
        db.refresh(decision_obj)

        logger.info(
            "Approval decision %s (%s) recorded for request %s by reviewer %s",
            decision_id,
            decision_req.decision,
            approval_id,
            reviewer_id,
        )
        return ApprovalDecisionResponse(
            decision_id=decision_id,
            approval_id=approval_id,
            reviewer_id=reviewer_id,
            reviewer_email=reviewer_email,
            decision=decision_req.decision,
            reason=decision_req.reason,
            decided_at=now,
        )

    async def get_approval_request(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        approval_id: uuid.UUID,
    ) -> ApprovalRequestResponse:
        """Retrieve an approval request state with tenant isolation (Phase 162)."""
        appr_obj = db.execute(
            select(ApprovalRequest).where(
                ApprovalRequest.id == approval_id,
                ApprovalRequest.tenant_id == tenant_id,
            )
        ).scalar_one_or_none()

        if not appr_obj:
            raise HumanApprovalError(f"Approval request {approval_id} not found.")

        return self._build_request_response(appr_obj)

    def _build_request_response(self, obj: ApprovalRequest) -> ApprovalRequestResponse:
        """Map ApprovalRequest ORM object to ApprovalRequestResponse schema."""
        status_enum = ApprovalStatus.PENDING_APPROVAL
        try:
            status_enum = ApprovalStatus(obj.status.upper())
        except Exception:
            pass

        context_dict = obj.approval_context or {}
        risk_str = context_dict.get("risk_level", "MEDIUM")
        try:
            risk_enum = ApprovalRiskLevel(risk_str.upper())
        except Exception:
            risk_enum = ApprovalRiskLevel.MEDIUM

        expires_at_val = obj.expires_at or datetime.now(UTC)
        agent_id_val = obj.agent_id or uuid.uuid4()

        return ApprovalRequestResponse(
            approval_id=obj.id,
            tenant_id=obj.tenant_id,
            agent_id=agent_id_val,
            requesting_user_id=obj.requester_id,
            action_name=obj.requested_action,
            amount=float(obj.requested_amount) if obj.requested_amount is not None else 0.0,
            currency=obj.currency_code,
            risk_level=risk_enum,
            status=status_enum,
            required_approvals_count=obj.required_approvals,
            current_approvals_count=obj.received_approvals,
            reason=obj.reason or "Approval requested",
            expires_at=expires_at_val,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
