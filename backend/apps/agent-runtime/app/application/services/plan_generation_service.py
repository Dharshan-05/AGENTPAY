"""Plan Generation application service for AGENTPAY (Phase 147).

Responsibilities:
    - Transform normalized intent into ordered, deterministic plan steps
    - Select canonical action sequences based on intent taxonomy
    - Construct step dependencies, constraints, and risk classifications
    - Identify required capabilities and tool requirements WITHOUT executing them
    - Support taxonomy: PAYMENT, REFUND, TRANSACTION_LOOKUP, BALANCE_QUERY, MERCHANT_LOOKUP, etc.
    - 100% Deterministic: generate_plan(intent) == generate_plan(intent)
    - ZERO EXECUTION: Does not call tools, charge money, captured funds, or invoke providers
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.domain.exceptions.agent_exceptions import PlanGenerationError
from app.schemas.agents import StructuredIntent
from app.schemas.plans import AgentPlan, PlanConstraints, PlanMetadata, PlanStep

logger = logging.getLogger("agentpay.agent.plan_generation.service")

# Secret redaction pattern for plan input strings
SECRET_REDACT_PATTERN = re.compile(
    r"(?i)(password|secret|bearer\s+[a-z0-9\-\._~\+\/]+=*|api_key|private_key|token)[:=]\s*([^\s,]+)"  # noqa: E501
)


class PlanGenerationService:
    """Application service for generating deterministic Agent Plans (Phase 147)."""

    def _sanitize_string(self, text: str | None) -> str:
        if not text:
            return ""
        return SECRET_REDACT_PATTERN.sub(r"\1=[REDACTED]", text)

    def generate_plan(
        self,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        intent: StructuredIntent,
        intent_category: str,
        intent_id: uuid.UUID | None = None,
        context_metadata: dict[str, Any] | None = None,
    ) -> AgentPlan:
        """Generate a deterministic plan representation from normalized intent.

        Raises:
            PlanGenerationError: if plan generation fails.
        """
        category = intent_category.upper()
        entities = intent.entities
        amount = entities.amount
        currency = (entities.currency or "USD").upper()
        merchant = self._sanitize_string(entities.merchant or "unknown_merchant")
        user = self._sanitize_string(
            entities.recipient or entities.target_id or "authenticated_user"
        )

        steps: list[PlanStep] = []

        if category == "PAYMENT":
            steps = [
                PlanStep(
                    step_id="step-1",
                    sequence=1,
                    action="validate_intent",
                    target=f"intent:{intent.intent_id}",
                    description="Validate payment intent scope, confidence, and parameters",
                    inputs={"intent_id": str(intent.intent_id), "category": "PAYMENT"},
                    dependencies=[],
                    constraints={"fail_closed": True},
                    expected_result="Intent validated successfully",
                    risk_level="low",
                    requires_authorization=False,
                    requires_tool=False,
                    execution_eligible=True,
                ),
                PlanStep(
                    step_id="step-2",
                    sequence=2,
                    action="lookup_merchant",
                    target=f"merchant:{merchant}",
                    description=f"Resolve target merchant '{merchant}' identity and status",
                    inputs={"merchant_identifier": merchant},
                    dependencies=["step-1"],
                    constraints={"require_active_merchant": True},
                    expected_result="Merchant identity verified",
                    risk_level="low",
                    requires_authorization=False,
                    requires_tool=True,
                    execution_eligible=True,
                ),
                PlanStep(
                    step_id="step-3",
                    sequence=3,
                    action="check_constraints",
                    target=f"financial_limits:{currency}",
                    description=f"Check transaction limit for amount {amount} {currency}",
                    inputs={"amount": str(amount) if amount else "0.00", "currency": currency},
                    dependencies=["step-1", "step-2"],
                    constraints={"currency": currency},
                    expected_result="Transaction amount within risk limits",
                    risk_level="medium",
                    requires_authorization=False,
                    requires_tool=False,
                    execution_eligible=True,
                ),
                PlanStep(
                    step_id="step-4",
                    sequence=4,
                    action="request_authorization",
                    target=f"agent_policy:{agent_id}",
                    description="Verify agent budget approval and policy authorization",
                    inputs={"agent_id": str(agent_id), "amount": str(amount) if amount else "0.00"},
                    dependencies=["step-3"],
                    constraints={"policy_eval": "strict"},
                    expected_result="Payment execution policy authorized",
                    risk_level="high",
                    requires_authorization=True,
                    requires_tool=False,
                    execution_eligible=True,
                ),
                PlanStep(
                    step_id="step-5",
                    sequence=5,
                    action="prepare_payment",
                    target=f"payment_gateway:{currency}",
                    description=f"Prepare payment payload for {amount} {currency} to {merchant}",
                    inputs={
                        "merchant": merchant,
                        "amount": str(amount) if amount else "0.00",
                        "currency": currency,
                    },
                    dependencies=["step-4"],
                    constraints={"atomic": True},
                    expected_result="Payment payload ready for execution loop",
                    risk_level="high",
                    requires_authorization=True,
                    requires_tool=True,
                    execution_eligible=True,
                ),
            ]

        elif category == "REFUND":
            steps = [
                PlanStep(
                    step_id="step-1",
                    sequence=1,
                    action="validate_intent",
                    target=f"intent:{intent.intent_id}",
                    description="Validate refund intent parameters",
                    inputs={"intent_id": str(intent.intent_id), "category": "REFUND"},
                    dependencies=[],
                    constraints={},
                    expected_result="Refund intent validated",
                    risk_level="low",
                    requires_authorization=False,
                    requires_tool=False,
                    execution_eligible=True,
                ),
                PlanStep(
                    step_id="step-2",
                    sequence=2,
                    action="lookup_transaction",
                    target="transaction_records",
                    description="Locate original transaction record for refund matching",
                    inputs={"amount": str(amount) if amount else "0.00", "currency": currency},
                    dependencies=["step-1"],
                    constraints={},
                    expected_result="Original transaction located",
                    risk_level="medium",
                    requires_authorization=False,
                    requires_tool=True,
                    execution_eligible=True,
                ),
                PlanStep(
                    step_id="step-3",
                    sequence=3,
                    action="verify_refund_eligibility",
                    target="refund_policy",
                    description="Verify refund window and policy constraints",
                    inputs={"amount": str(amount) if amount else "0.00"},
                    dependencies=["step-2"],
                    constraints={},
                    expected_result="Refund eligibility confirmed",
                    risk_level="medium",
                    requires_authorization=True,
                    requires_tool=False,
                    execution_eligible=True,
                ),
                PlanStep(
                    step_id="step-4",
                    sequence=4,
                    action="prepare_refund",
                    target="refund_gateway",
                    description=f"Prepare refund payload of {amount} {currency}",
                    inputs={"amount": str(amount) if amount else "0.00", "currency": currency},
                    dependencies=["step-3"],
                    constraints={},
                    expected_result="Refund payload ready for execution loop",
                    risk_level="high",
                    requires_authorization=True,
                    requires_tool=True,
                    execution_eligible=True,
                ),
            ]

        elif category == "TRANSACTION_LOOKUP":
            steps = [
                PlanStep(
                    step_id="step-1",
                    sequence=1,
                    action="validate_intent",
                    target=f"intent:{intent.intent_id}",
                    description="Validate transaction lookup parameters",
                    inputs={"category": "TRANSACTION_LOOKUP"},
                    dependencies=[],
                    constraints={},
                    expected_result="Lookup intent validated",
                    risk_level="low",
                    requires_authorization=False,
                    requires_tool=False,
                    execution_eligible=True,
                ),
                PlanStep(
                    step_id="step-2",
                    sequence=2,
                    action="query_transaction_records",
                    target="ledger_service",
                    description="Query agent transaction ledger",
                    inputs={"agent_id": str(agent_id)},
                    dependencies=["step-1"],
                    constraints={"read_only": True},
                    expected_result="Transaction history records returned",
                    risk_level="low",
                    requires_authorization=False,
                    requires_tool=True,
                    execution_eligible=True,
                ),
            ]

        elif category == "BALANCE_QUERY":
            steps = [
                PlanStep(
                    step_id="step-1",
                    sequence=1,
                    action="validate_intent",
                    target=f"intent:{intent.intent_id}",
                    description="Validate balance query intent",
                    inputs={"category": "BALANCE_QUERY"},
                    dependencies=[],
                    constraints={},
                    expected_result="Query intent validated",
                    risk_level="low",
                    requires_authorization=False,
                    requires_tool=False,
                    execution_eligible=True,
                ),
                PlanStep(
                    step_id="step-2",
                    sequence=2,
                    action="query_account_balance",
                    target=f"account:{agent_id}",
                    description="Fetch current agent balance and reserve status",
                    inputs={"agent_id": str(agent_id)},
                    dependencies=["step-1"],
                    constraints={"read_only": True},
                    expected_result="Current agent balance retrieved",
                    risk_level="low",
                    requires_authorization=False,
                    requires_tool=True,
                    execution_eligible=True,
                ),
            ]

        elif category == "MERCHANT_LOOKUP":
            steps = [
                PlanStep(
                    step_id="step-1",
                    sequence=1,
                    action="validate_intent",
                    target=f"intent:{intent.intent_id}",
                    description="Validate merchant lookup intent",
                    inputs={"merchant": merchant},
                    dependencies=[],
                    constraints={},
                    expected_result="Merchant lookup validated",
                    risk_level="low",
                    requires_authorization=False,
                    requires_tool=False,
                    execution_eligible=True,
                ),
                PlanStep(
                    step_id="step-2",
                    sequence=2,
                    action="query_merchant_catalog",
                    target=f"merchant_catalog:{merchant}",
                    description=f"Query merchant information for '{merchant}'",
                    inputs={"merchant_identifier": merchant},
                    dependencies=["step-1"],
                    constraints={"read_only": True},
                    expected_result="Merchant details retrieved",
                    risk_level="low",
                    requires_authorization=False,
                    requires_tool=True,
                    execution_eligible=True,
                ),
            ]

        elif category == "USER_LOOKUP":
            steps = [
                PlanStep(
                    step_id="step-1",
                    sequence=1,
                    action="validate_intent",
                    target=f"intent:{intent.intent_id}",
                    description="Validate user lookup parameters",
                    inputs={"user": user},
                    dependencies=[],
                    constraints={},
                    expected_result="User lookup validated",
                    risk_level="low",
                    requires_authorization=False,
                    requires_tool=False,
                    execution_eligible=True,
                ),
                PlanStep(
                    step_id="step-2",
                    sequence=2,
                    action="query_user_profile",
                    target=f"user:{user}",
                    description=f"Query public user profile for '{user}'",
                    inputs={"user_identifier": user},
                    dependencies=["step-1"],
                    constraints={"read_only": True},
                    expected_result="User profile details retrieved",
                    risk_level="low",
                    requires_authorization=False,
                    requires_tool=True,
                    execution_eligible=True,
                ),
            ]

        elif category == "AGENT_OPERATION":
            steps = [
                PlanStep(
                    step_id="step-1",
                    sequence=1,
                    action="validate_intent",
                    target=f"intent:{intent.intent_id}",
                    description="Validate agent operation intent",
                    inputs={"category": "AGENT_OPERATION"},
                    dependencies=[],
                    constraints={},
                    expected_result="Agent operation validated",
                    risk_level="low",
                    requires_authorization=False,
                    requires_tool=False,
                    execution_eligible=True,
                ),
                PlanStep(
                    step_id="step-2",
                    sequence=2,
                    action="inspect_agent_configuration",
                    target=f"agent:{agent_id}",
                    description="Inspect agent operational parameters and permissions",
                    inputs={"agent_id": str(agent_id)},
                    dependencies=["step-1"],
                    constraints={"read_only": True},
                    expected_result="Agent state inspected",
                    risk_level="low",
                    requires_authorization=False,
                    requires_tool=False,
                    execution_eligible=True,
                ),
            ]

        elif category == "UNKNOWN":
            steps = [
                PlanStep(
                    step_id="step-1",
                    sequence=1,
                    action="reject_unknown_intent",
                    target="intent_evaluator",
                    description="Unknown intent category cannot produce executable plan steps",
                    inputs={"category": "UNKNOWN"},
                    dependencies=[],
                    constraints={"executable": False},
                    expected_result="Plan marked non-executable",
                    risk_level="high",
                    requires_authorization=False,
                    requires_tool=False,
                    execution_eligible=False,
                ),
            ]

        else:
            raise PlanGenerationError(
                f"Unsupported intent category '{category}' for plan generation."
            )

        # Determine overall constraints
        plan_constraints = PlanConstraints(
            max_amount=amount if amount and amount > Decimal("0.00") else Decimal("1000.00"),
            allowed_currencies=[currency],
            timeout_seconds=300,
            requires_human_approval=category in ("PAYMENT", "REFUND"),
            risk_tolerance="high" if category in ("PAYMENT", "REFUND") else "medium",
        )

        plan_metadata = PlanMetadata(
            intent_category=category,
            confidence=intent.confidence,
            rationale=f"Deterministic {category} plan generated for agent {agent_id}",
            generator_version="1.0.0",
            planner_id="deterministic_planner_v1",
        )

        plan_status = "draft" if category != "UNKNOWN" else "rejected"

        # Deterministic deterministic seed derived from intent_id or generated
        derived_plan_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"plan-{intent.intent_id}")

        created_at = (
            getattr(intent, "extracted_at", None)
            or getattr(intent, "created_at", None)
            or datetime.now(UTC)
        )

        return AgentPlan(
            plan_id=derived_plan_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            intent_id=intent_id or intent.intent_id,
            intent_type=category,
            version="1.0.0",
            status=plan_status,
            steps=steps,
            constraints=plan_constraints,
            metadata=plan_metadata,
            created_at=created_at,
        )
