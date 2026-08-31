"""ATIMPlanningService for dynamic plan proposals and tool sequence composition."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.application.services.plan_validation_service import SUPPORTED_PLAN_ACTIONS
from app.schemas.atim import (
    ATIMPlanProposal,
    ATIMProposedIntent,
    ToolProposal,
    ToolRiskLevel,
)
from app.schemas.plans import AgentPlan, PlanConstraints, PlanMetadata, PlanStep

logger = logging.getLogger("agentpay.atim.planning.service")


class ATIMPlanningService:
    """Production service for generating proposed ATIM transaction plans."""

    def propose_plan(
        self,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        intent: ATIMProposedIntent,
    ) -> ATIMPlanProposal:
        """Generate dynamic ToolProposal sequence based on normalized ATIM intent."""
        proposed_tools: list[ToolProposal] = []
        action = intent.action.upper()
        amount = intent.amount or Decimal("0.00")
        merchant = intent.merchant or "unknown_merchant"
        target_name = intent.product or intent.target or merchant

        # Check for ambiguity
        if intent.is_ambiguous or intent.confidence_level in ("AMBIGUOUS", "INVALID"):
            proposed_tools = [
                ToolProposal(
                    tool_name="validate_intent",
                    arguments={
                        "intent_id": str(intent.intent_id),
                        "status": "AMBIGUOUS",
                        "reason": intent.ambiguity_reason or "Incomplete financial details",
                    },
                    sequence=1,
                    risk_level=ToolRiskLevel.LOW,
                    requires_server_validation=True,
                )
            ]
            return ATIMPlanProposal(
                plan_id=uuid.uuid4(),
                intent_id=intent.intent_id,
                tenant_id=tenant_id,
                agent_id=agent_id,
                proposed_tools=proposed_tools,
                rationale=f"ATIM proposal marked ambiguous: {intent.ambiguity_reason}",
                estimated_operations=1,
                risk_classification="high",
                is_executable_proposal=False,
            )

        if action == "PAYMENT":
            proposed_tools = [
                ToolProposal(
                    tool_name="validate_intent",
                    arguments={"intent_id": str(intent.intent_id), "category": "PAYMENT"},
                    sequence=1,
                    risk_level=ToolRiskLevel.LOW,
                    depends_on=[],
                ),
                ToolProposal(
                    tool_name="lookup_merchant",
                    arguments={"merchant_identifier": merchant},
                    sequence=2,
                    risk_level=ToolRiskLevel.LOW,
                    depends_on=["step-1"],
                ),
                ToolProposal(
                    tool_name="check_constraints",
                    arguments={"amount": str(amount), "currency": intent.currency or "USD"},
                    sequence=3,
                    risk_level=ToolRiskLevel.MEDIUM,
                    depends_on=["step-1", "step-2"],
                ),
                ToolProposal(
                    tool_name="request_authorization",
                    arguments={"agent_id": str(agent_id), "amount": str(amount)},
                    sequence=4,
                    risk_level=ToolRiskLevel.HIGH,
                    is_financial=True,
                    depends_on=["step-3"],
                ),
                ToolProposal(
                    tool_name="prepare_payment",
                    arguments={
                        "merchant": merchant,
                        "amount": str(amount),
                        "currency": intent.currency or "USD",
                    },
                    sequence=5,
                    risk_level=ToolRiskLevel.PROPOSAL_ONLY,
                    is_financial=True,
                    depends_on=["step-4"],
                    requires_server_validation=True,
                ),
            ]
        elif action in ("PRODUCT_SEARCH", "PRODUCT_COMPARE") or "PURCHASE" in intent.sub_intents:
            proposed_tools = [
                ToolProposal(
                    tool_name="validate_intent",
                    arguments={"intent_id": str(intent.intent_id), "category": action},
                    sequence=1,
                    risk_level=ToolRiskLevel.LOW,
                    depends_on=[],
                ),
                ToolProposal(
                    tool_name="query_merchant_catalog",
                    arguments={
                        "product": target_name,
                        "brand": intent.brand or "",
                        "merchant": merchant,
                    },
                    sequence=2,
                    risk_level=ToolRiskLevel.LOW,
                    depends_on=["step-1"],
                ),
                ToolProposal(
                    tool_name="check_constraints",
                    arguments={
                        "amount": str(amount),
                        "currency": intent.currency or "USD",
                        "optimization": intent.optimization or "NONE",
                    },
                    sequence=3,
                    risk_level=ToolRiskLevel.MEDIUM,
                    depends_on=["step-2"],
                ),
            ]

            if "PURCHASE" in intent.sub_intents or amount > Decimal("0.00"):
                proposed_tools.extend([
                    ToolProposal(
                        tool_name="request_authorization",
                        arguments={"agent_id": str(agent_id), "amount": str(amount)},
                        sequence=4,
                        risk_level=ToolRiskLevel.HIGH,
                        is_financial=True,
                        depends_on=["step-3"],
                    ),
                    ToolProposal(
                        tool_name="prepare_payment",
                        arguments={
                            "merchant": merchant,
                            "product": target_name,
                            "amount": str(amount),
                            "currency": intent.currency or "USD",
                        },
                        sequence=5,
                        risk_level=ToolRiskLevel.PROPOSAL_ONLY,
                        is_financial=True,
                        depends_on=["step-4"],
                        requires_server_validation=True,
                    ),
                ])
        elif action == "REFUND":
            proposed_tools = [
                ToolProposal(
                    tool_name="validate_intent",
                    arguments={"intent_id": str(intent.intent_id), "category": "REFUND"},
                    sequence=1,
                    risk_level=ToolRiskLevel.LOW,
                    depends_on=[],
                ),
                ToolProposal(
                    tool_name="lookup_transaction",
                    arguments={"amount": str(amount)},
                    sequence=2,
                    risk_level=ToolRiskLevel.MEDIUM,
                    depends_on=["step-1"],
                ),
                ToolProposal(
                    tool_name="verify_refund_eligibility",
                    arguments={"amount": str(amount)},
                    sequence=3,
                    risk_level=ToolRiskLevel.HIGH,
                    is_financial=True,
                    depends_on=["step-2"],
                ),
                ToolProposal(
                    tool_name="prepare_refund",
                    arguments={"amount": str(amount)},
                    sequence=4,
                    risk_level=ToolRiskLevel.PROPOSAL_ONLY,
                    is_financial=True,
                    depends_on=["step-3"],
                    requires_server_validation=True,
                ),
            ]
        else:
            # General query / lookup operations
            proposed_tools = [
                ToolProposal(
                    tool_name="validate_intent",
                    arguments={"category": action},
                    sequence=1,
                    risk_level=ToolRiskLevel.LOW,
                    depends_on=[],
                ),
                ToolProposal(
                    tool_name="query_merchant_catalog" if action == "MERCHANT_LOOKUP" else "query_transaction_records",
                    arguments={"target": intent.target or "default"},
                    sequence=2,
                    risk_level=ToolRiskLevel.LOW,
                    depends_on=["step-1"],
                ),
            ]

        # Verify tool actions against canonical set
        is_executable = True
        for tp in proposed_tools:
            if tp.tool_name not in SUPPORTED_PLAN_ACTIONS:
                logger.warning("Proposed tool action '%s' is not supported.", tp.tool_name)
                is_executable = False

        return ATIMPlanProposal(
            plan_id=uuid.uuid4(),
            intent_id=intent.intent_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            proposed_tools=proposed_tools,
            rationale=f"ATIM proposal generated for intent {action}",
            estimated_operations=len(proposed_tools),
            risk_classification="high" if any(tp.is_financial for tp in proposed_tools) else "low",
            is_executable_proposal=is_executable,
        )

    def to_agent_plan(
        self,
        proposal: ATIMPlanProposal,
        intent: ATIMProposedIntent,
    ) -> AgentPlan:
        """Convert ATIMPlanProposal to standard domain AgentPlan object for DAG validation."""
        steps: list[PlanStep] = []
        is_executable = proposal.is_executable_proposal and not intent.is_ambiguous

        for tp in proposal.proposed_tools:
            deps = tp.depends_on if tp.depends_on else ([f"step-{tp.sequence - 1}"] if tp.sequence > 1 else [])
            risk_str = tp.risk_level.value if hasattr(tp.risk_level, "value") else str(tp.risk_level)

            steps.append(
                PlanStep(
                    step_id=f"step-{tp.sequence}",
                    sequence=tp.sequence,
                    action=tp.tool_name,
                    target=f"{tp.tool_name}:{intent.target or intent.product or 'default'}",
                    description=f"ATIM step {tp.sequence}: {tp.tool_name}",
                    inputs=tp.arguments,
                    dependencies=deps,
                    constraints={"server_validation": tp.requires_server_validation},
                    expected_result=f"{tp.tool_name} completed",
                    risk_level=risk_str if risk_str != "proposal_only" else "high",
                    requires_authorization=tp.risk_level in (ToolRiskLevel.HIGH, ToolRiskLevel.PROPOSAL_ONLY) or tp.is_financial,
                    requires_tool=True,
                    execution_eligible=is_executable,
                )
            )

        amount = intent.amount or Decimal("1000.00")
        currency = intent.currency or "USD"

        return AgentPlan(
            plan_id=proposal.plan_id,
            tenant_id=proposal.tenant_id,
            agent_id=proposal.agent_id,
            intent_id=proposal.intent_id,
            intent_type=intent.action if is_executable else "UNKNOWN",
            version="1.0.0",
            status="draft" if is_executable else "rejected",
            steps=steps,
            constraints=PlanConstraints(
                max_amount=amount,
                allowed_currencies=[currency],
                timeout_seconds=300,
                requires_human_approval=intent.action in ("PAYMENT", "REFUND"),
                risk_tolerance="high" if intent.action in ("PAYMENT", "REFUND") else "medium",
            ),
            metadata=PlanMetadata(
                intent_category=intent.action,
                confidence=intent.confidence,
                rationale=proposal.rationale,
                generator_version="1.0.0",
                planner_id="atim_planner_v1",
            ),
            created_at=datetime.now(UTC),
        )


