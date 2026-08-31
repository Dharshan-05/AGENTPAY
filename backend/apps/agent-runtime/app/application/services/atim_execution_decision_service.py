"""ATIM Execution Decision Service implementing strict deterministic decision matrix precedence (Phase 6)."""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from typing import Any, Literal
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.atim_agentguard_integration_service import (
    ATIMAgentGuardIntegrationService,
    ATIMSecurityExecutionDecision,
)
from app.application.services.atim_fraudguard_integration_service import (
    ATIMFraudDecision,
    ATIMFraudGuardIntegrationService,
)
from app.application.services.human_approval_workflow_service import HumanApprovalWorkflowService
from app.application.services.plan_validation_service import PlanValidationService
from app.schemas.atim import ATIMPlanProposal
from app.schemas.human_approval import ApprovalPolicyEvaluationResponse, ApprovalRequestCreate
from app.schemas.plans import AgentPlan, PlanValidationResult

logger = logging.getLogger("agentpay.atim.execution.decision")


class FinancialToolClassification(BaseModel):
    """Financial tool classification metadata governing execution boundaries."""

    tool_name: str
    is_financial: bool = True
    requires_authorization: bool = True
    requires_fraud_check: bool = True
    requires_human_approval: bool = True
    required_scopes: list[str] = Field(default_factory=lambda: ["payments:write"])
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "HIGH"


class FinalExecutionDecision(BaseModel):
    """Authoritative final decision envelope combining all security and risk gates."""

    decision: Literal["DENY", "REVIEW", "ALLOW"]
    execution_eligible: bool = False
    requires_human_approval: bool = False
    reason_codes: list[str] = Field(default_factory=list)
    security_status: str = "ALLOW"
    plan_status: str = "VALID"
    agentguard_status: str = "ALLOWED"
    fraudguard_status: str = "ALLOW"
    hitl_status: str = "NOT_REQUIRED"
    approval_id: uuid.UUID | None = None
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agentguard_decision: ATIMSecurityExecutionDecision | None = None
    fraudguard_decision: ATIMFraudDecision | None = None
    hitl_policy_evaluation: ApprovalPolicyEvaluationResponse | None = None


class ATIMExecutionDecisionService:
    """Production Orchestration Gateway evaluating proposals through authoritative server gates."""

    def __init__(
        self,
        agentguard_integration: ATIMAgentGuardIntegrationService | None = None,
        fraudguard_integration: ATIMFraudGuardIntegrationService | None = None,
        human_approval_service: HumanApprovalWorkflowService | None = None,
        plan_validation_service: PlanValidationService | None = None,
    ) -> None:
        self.agentguard_integration = agentguard_integration or ATIMAgentGuardIntegrationService()
        self.fraudguard_integration = fraudguard_integration or ATIMFraudGuardIntegrationService()
        self.human_approval_service = human_approval_service or HumanApprovalWorkflowService()
        self.plan_validation_service = plan_validation_service or PlanValidationService()

    async def evaluate_proposal_execution(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        proposal: ATIMPlanProposal,
        user_prompt_security_allowed: bool = True,
        security_rejection_reason: str | None = None,
    ) -> FinalExecutionDecision:
        """Evaluate proposal against strict decision matrix precedence order fail-closed.

        Precedence Matrix Order:
        1. SECURITY BLOCK -> DENY
        2. PLAN INVALID -> DENY
        3. AGENTGUARD DENY -> DENY
        4. FRAUDGUARD BLOCK -> DENY
        5. HITL REQUIRED -> REVIEW
        6. ALLOW -> ALLOW
        """
        corr_id = str(uuid.uuid4())
        reasons: list[str] = []

        # -------------------------------------------------------------------
        # GATE 1: SECURITY BLOCK (ATIM Phase 4 Input Security)
        # -------------------------------------------------------------------
        if not user_prompt_security_allowed:
            logger.warning("Execution blocked by GATE 1: ATIM Security Threat (%s)", security_rejection_reason)
            return FinalExecutionDecision(
                decision="DENY",
                execution_eligible=False,
                requires_human_approval=False,
                reason_codes=[security_rejection_reason or "PROMPT_SECURITY_THREAT_REJECTED"],
                security_status="REJECTED",
                plan_status="NOT_EVALUATED",
                agentguard_status="NOT_EVALUATED",
                fraudguard_status="NOT_EVALUATED",
                hitl_status="NOT_EVALUATED",
                correlation_id=corr_id,
            )

        # Extract proposal details
        proposed_intent = proposal.proposed_intent
        amount = proposed_intent.amount or Decimal("0.00")
        currency = proposed_intent.currency or "USD"
        action = proposed_intent.action or "purchase"
        merchant = proposed_intent.merchant

        # -------------------------------------------------------------------
        # GATE 2: PLAN VALIDATION (Phase 3 DAG & Taxonomy Validation)
        # -------------------------------------------------------------------
        plan_validation: PlanValidationResult = self.plan_validation_service.validate_plan(
            plan=proposal.plan,
            target_tenant_id=tenant_id,
            target_agent_id=agent_id,
        )

        if not plan_validation.is_valid:
            logger.warning("Execution blocked by GATE 2: Invalid Plan (%s)", plan_validation.errors)
            return FinalExecutionDecision(
                decision="DENY",
                execution_eligible=False,
                requires_human_approval=False,
                reason_codes=plan_validation.errors or ["INVALID_PLAN_STRUCTURE"],
                security_status="ALLOW",
                plan_status="INVALID",
                agentguard_status="NOT_EVALUATED",
                fraudguard_status="NOT_EVALUATED",
                hitl_status="NOT_EVALUATED",
                correlation_id=corr_id,
            )

        # -------------------------------------------------------------------
        # GATE 3: AGENTGUARD AUTHORITATIVE EVALUATION (Phase 6)
        # -------------------------------------------------------------------
        ag_decision: ATIMSecurityExecutionDecision = await self.agentguard_integration.evaluate_proposal(
            db=db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            requested_action=action,
            amount=amount,
            currency=currency,
            merchant_id=merchant,
        )

        if not ag_decision.allowed:
            logger.warning("Execution blocked by GATE 3: AGENTGUARD Denied (%s)", ag_decision.reason_code)
            return FinalExecutionDecision(
                decision="DENY",
                execution_eligible=False,
                requires_human_approval=False,
                reason_codes=[ag_decision.reason_code],
                security_status="ALLOW",
                plan_status="VALID",
                agentguard_status="DENIED",
                fraudguard_status="NOT_EVALUATED",
                hitl_status="NOT_EVALUATED",
                correlation_id=corr_id,
                agentguard_decision=ag_decision,
            )

        # -------------------------------------------------------------------
        # GATE 4: FRAUDGUARD AUTHORITATIVE ML EVALUATION (Phase 6)
        # -------------------------------------------------------------------
        fg_decision: ATIMFraudDecision = await self.fraudguard_integration.evaluate_fraud_risk(
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id=f"TX-{corr_id[:8]}",
            amount=ag_decision.evaluated_amount or Decimal("0.00"),
            currency=ag_decision.evaluated_currency or "USD",
            merchant_id=merchant,
        )

        if fg_decision.decision == "BLOCK":
            logger.warning("Execution blocked by GATE 4: FRAUDGUARD Blocked (%s)", fg_decision.risk_level)
            return FinalExecutionDecision(
                decision="DENY",
                execution_eligible=False,
                requires_human_approval=False,
                reason_codes=[f"FRAUDGUARD_BLOCKED_{fg_decision.risk_level}"],
                security_status="ALLOW",
                plan_status="VALID",
                agentguard_status="ALLOWED",
                fraudguard_status="BLOCK",
                hitl_status="NOT_EVALUATED",
                correlation_id=corr_id,
                agentguard_decision=ag_decision,
                fraudguard_decision=fg_decision,
            )

        # -------------------------------------------------------------------
        # GATE 5: HITL HUMAN APPROVAL EVALUATION (Phase 6)
        # -------------------------------------------------------------------
        hitl_policy: ApprovalPolicyEvaluationResponse = await self.human_approval_service.evaluate_approval_policy(
            tenant_id=tenant_id,
            action_name=action,
            amount=float(ag_decision.evaluated_amount or Decimal("0.00")),
            currency=ag_decision.evaluated_currency or "USD",
        )

        requires_hitl = (
            ag_decision.requires_human_approval
            or fg_decision.decision == "REVIEW"
            or hitl_policy.requires_approval
        )

        approval_id: uuid.UUID | None = None
        if requires_hitl:
            try:
                appr_req = ApprovalRequestCreate(
                    action_name=action,
                    amount=float(ag_decision.evaluated_amount or Decimal("0.00")),
                    currency=ag_decision.evaluated_currency or "USD",
                    reason=f"HITL approval required for {action} of {ag_decision.evaluated_currency} {ag_decision.evaluated_amount}",
                    context_data={
                        "agentguard_decision": ag_decision.decision_code,
                        "fraudguard_risk_level": fg_decision.risk_level,
                        "fraudguard_risk_score": float(fg_decision.risk_score),
                    },
                )
                appr_res = await self.human_approval_service.create_approval_request(
                    db=db,
                    tenant_id=tenant_id,
                    agent_id=agent_id,
                    request=appr_req,
                )
                approval_id = appr_res.approval_id
            except Exception as exc:
                logger.warning("Failed to create HITL approval record: %s", exc)

            logger.info("Execution requires GATE 5: HITL Human Approval (ApprovalID: %s)", approval_id)
            return FinalExecutionDecision(
                decision="REVIEW",
                execution_eligible=False,  # Financial tool execution suspended until HITL approval
                requires_human_approval=True,
                reason_codes=["REQUIRES_HUMAN_APPROVAL"],
                security_status="ALLOW",
                plan_status="VALID",
                agentguard_status="ALLOWED",
                fraudguard_status=fg_decision.decision,
                hitl_status="REQUIRED",
                approval_id=approval_id,
                correlation_id=corr_id,
                agentguard_decision=ag_decision,
                fraudguard_decision=fg_decision,
                hitl_policy_evaluation=hitl_policy,
            )

        # -------------------------------------------------------------------
        # GATE 6: ALLOW (All Authoritative Gates Passed)
        # -------------------------------------------------------------------
        logger.info("All authoritative security gates passed for proposal %s", proposal.plan.plan_id)
        return FinalExecutionDecision(
            decision="ALLOW",
            execution_eligible=True,
            requires_human_approval=False,
            reason_codes=["ALL_SECURITY_GATES_PASSED"],
            security_status="ALLOW",
            plan_status="VALID",
            agentguard_status="ALLOWED",
            fraudguard_status="ALLOW",
            hitl_status="AUTO_APPROVED",
            correlation_id=corr_id,
            agentguard_decision=ag_decision,
            fraudguard_decision=fg_decision,
            hitl_policy_evaluation=hitl_policy,
        )
