"""ATIM AGENTGUARD Integration Service for authoritative policy evaluation and financial normalization (Phase 6)."""

from __future__ import annotations

import logging
import math
import re
import uuid
from decimal import Decimal, InvalidOperation
from typing import Any, Literal
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agentguard_integration_service import AgentGuardIntegrationService
from app.schemas.agentguard_decision import (
    AgentGuardDecisionRequest,
    AgentGuardDecisionResult,
)

logger = logging.getLogger("agentpay.atim.integration.agentguard")

SUPPORTED_ISO_CURRENCIES = frozenset({"USD", "INR", "EUR", "GBP", "CAD", "AUD", "SGD", "AED"})


class ATIMSecurityExecutionDecision(BaseModel):
    """Deterministic security decision envelope returned by ATIMAgentGuardIntegrationService."""

    allowed: bool
    requires_human_approval: bool
    decision_code: str
    reason_code: str
    policy_id: str | None = None
    evaluated_amount: Decimal | None = None
    evaluated_currency: str | None = None
    agent_id: uuid.UUID
    tenant_id: uuid.UUID
    source: Literal["AGENTGUARD"] = "AGENTGUARD"
    raw_decision_result: AgentGuardDecisionResult | None = None


class ATIMAgentGuardIntegrationService:
    """Production gateway connecting ATIM proposals to the authoritative AGENTGUARD policy engine."""

    def __init__(
        self,
        agentguard_service: AgentGuardIntegrationService | None = None,
    ) -> None:
        self.agentguard_service = agentguard_service or AgentGuardIntegrationService()

    def normalize_financial_amount(self, raw_amount: Any) -> Decimal:
        """Normalize amount to high-precision Decimal, rejecting NaN, Infinity, and invalid values."""
        if raw_amount is None:
            raise ValueError("Financial amount cannot be None.")

        if isinstance(raw_amount, float):
            if math.isnan(raw_amount) or math.isinf(raw_amount):
                raise ValueError("Financial amount cannot be NaN or Infinity.")

        str_val = str(raw_amount).strip().replace(",", "").replace("$", "").replace("₹", "")
        try:
            val = Decimal(str_val)
        except InvalidOperation as exc:
            raise ValueError(f"Invalid monetary Decimal string '{raw_amount}'.") from exc

        if val.is_nan() or val.is_infinite():
            raise ValueError("Financial amount cannot be NaN or Infinity.")

        if val < Decimal("0.00"):
            raise ValueError(f"Financial amount cannot be negative ({val}).")

        return val.quantize(Decimal("0.01"))

    def normalize_currency(self, raw_currency: str | None) -> str:
        """Normalize and validate ISO 4217 currency code."""
        if not raw_currency:
            return "USD"

        curr_str = raw_currency.strip().upper()
        if curr_str == "₹":
            curr_str = "INR"
        elif curr_str == "$":
            curr_str = "USD"
        elif curr_str == "€":
            curr_str = "EUR"
        elif curr_str == "£":
            curr_str = "GBP"

        if curr_str not in SUPPORTED_ISO_CURRENCIES:
            raise ValueError(f"Unsupported currency code '{raw_currency}'. Must be valid ISO 4217.")

        return curr_str

    async def evaluate_proposal(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        requested_action: str,
        amount: Any,
        currency: str = "USD",
        merchant_id: str | None = None,
        category: str | None = None,
        principal_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ATIMSecurityExecutionDecision:
        """Normalize proposal and evaluate through authoritative AGENTGUARD engine fail-closed."""
        try:
            norm_amount = self.normalize_financial_amount(amount)
            norm_currency = self.normalize_currency(currency)
        except Exception as exc:
            logger.warning("Financial normalization failed for agent %s in tenant %s: %s", agent_id, tenant_id, exc)
            return ATIMSecurityExecutionDecision(
                allowed=False,
                requires_human_approval=False,
                decision_code="DENIED",
                reason_code=f"MALFORMED_FINANCIAL_DATA: {exc}",
                evaluated_amount=None,
                evaluated_currency=None,
                agent_id=agent_id,
                tenant_id=tenant_id,
            )

        # Build AGENTGUARD request
        ag_request = AgentGuardDecisionRequest(
            tenant_id=tenant_id,
            agent_id=agent_id,
            principal_id=principal_id,
            requested_action=requested_action,
            amount=norm_amount,
            currency=norm_currency,
            merchant_id=merchant_id,
            category=category,
            metadata=metadata or {},
        )

        ag_result: AgentGuardDecisionResult = await self.agentguard_service.evaluate_agent_request(
            db, ag_request
        )

        allowed = ag_result.can_proceed and ag_result.decision in ("ALLOWED", "NO_APPLICABLE_POLICY")
        requires_approval = ag_result.requires_approval or ag_result.decision == "REQUIRE_APPROVAL"
        reason_code = ag_result.reason_codes[0] if ag_result.reason_codes else ag_result.decision


        logger.info(
            "AGENTGUARD evaluation for agent %s tenant %s: Decision=%s (Allowed=%s, Approval=%s)",
            agent_id,
            tenant_id,
            ag_result.decision,
            allowed,
            requires_approval,
        )

        return ATIMSecurityExecutionDecision(
            allowed=allowed,
            requires_human_approval=requires_approval,
            decision_code=ag_result.decision,
            reason_code=reason_code,
            policy_id=ag_result.blocking_factors[0] if ag_result.blocking_factors else None,
            evaluated_amount=norm_amount,
            evaluated_currency=norm_currency,
            agent_id=agent_id,
            tenant_id=tenant_id,
            source="AGENTGUARD",
            raw_decision_result=ag_result,
        )
