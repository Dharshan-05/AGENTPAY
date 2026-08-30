"""Intent Validation application service for AGENTPAY (Phase 143).

Responsibilities:
    - Validate StructuredIntent deterministically and fail-closed
    - Verify required fields, canonical taxonomy, bounded confidence, and financial precision
    - Enforce category-specific validation rules (PAYMENT, REFUND, BALANCE_QUERY, etc.)
    - Mark UNKNOWN or low-confidence intents as ineligible for execution
    - Reject client injection of server-controlled security fields
    - IDOR protection: Cross-tenant attempts raise `AgentNotFoundError` (404)
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.agent_exceptions import AgentNotFoundError, IntentValidationError
from app.infrastructure.database.models.agent import Agent
from app.schemas.agents import StructuredIntent

logger = logging.getLogger("agentpay.agent.intent_validation.service")

# Canonical Intent Taxonomy matching Phase 141
CANONICAL_TAXONOMY = frozenset(
    {
        "PAYMENT",
        "REFUND",
        "TRANSACTION_LOOKUP",
        "BALANCE_QUERY",
        "MERCHANT_LOOKUP",
        "USER_LOOKUP",
        "AGENT_OPERATION",
        "UNKNOWN",
    }
)

# Supported ISO 4217 Currency codes
SUPPORTED_CURRENCIES = frozenset({"INR", "USD", "EUR", "GBP", "CAD", "AUD", "SGD", "JPY"})

# Secret patterns to detect forbidden secret leakage in intent parameters
FORBIDDEN_SECRET_PATTERN = re.compile(
    r"(?i)(password|secret|bearer\s+[a-z0-9\-\._~\+\/]+=*|api_key|private_key|token)[:=]"
)


class IntentValidationResult(BaseModel):
    """Structured result of intent validation."""

    is_valid: bool = Field(..., description="Whether intent passed validation")
    intent_category: str = Field(..., description="Validated intent category")
    validation_errors: list[str] = Field(
        default_factory=list, description="Detailed validation error list"
    )
    is_execution_eligible: bool = Field(
        ..., description="Whether intent is eligible for downstream execution"
    )
    validated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Validation timestamp"
    )

    model_config = ConfigDict(extra="forbid")


class IntentValidationService:
    """Application service for validating Structured Intents (Phase 143)."""

    async def validate_intent(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        intent: StructuredIntent,
        intent_category: str,
    ) -> IntentValidationResult:
        """Validate StructuredIntent within authenticated tenant scope.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
            IntentValidationError: if fail-closed validation check fails catastrophically.
        """
        # 1. IDOR Check: Ensure agent exists in authenticated tenant
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        agent = agent_res.scalar_one_or_none()
        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        # Check agent operational lifecycle status
        if agent.status in ("revoked", "suspended", "deactivated"):
            raise IntentValidationError(
                f"Agent {agent_id} is in '{agent.status}' status and cannot process intent."
            )

        errors: list[str] = []
        now = datetime.now(UTC)

        # 2. Canonical Taxonomy Verification
        category_upper = intent_category.upper().strip()
        if category_upper not in CANONICAL_TAXONOMY:
            errors.append(f"Invalid intent category '{intent_category}' not in canonical taxonomy.")

        # 3. Bounded Confidence Verification (0.00 <= confidence <= 1.00)
        if intent.confidence < Decimal("0.00") or intent.confidence > Decimal("1.00"):
            errors.append(f"Confidence score {intent.confidence} outside valid range [0.00, 1.00].")

        # 4. Entity Structure & Secret Sanitization Check
        entities = intent.entities
        if entities.custom_entities:
            for k, v in entities.custom_entities.items():
                if FORBIDDEN_SECRET_PATTERN.search(f"{k}:{v}"):
                    errors.append(
                        f"Forbidden secret material detected in custom entity field '{k}'."
                    )

        # Parameter/Constraint secret leakage check
        str_params = str(intent.parameters) + str(intent.constraints)
        if FORBIDDEN_SECRET_PATTERN.search(str_params):
            errors.append("Forbidden secret material detected in parameters or constraints.")

        # 5. Category-Specific Validation Rules
        if category_upper == "PAYMENT":
            if entities.amount is None:
                errors.append("PAYMENT intent requires explicit monetary amount.")
            elif not isinstance(entities.amount, Decimal):
                errors.append("PAYMENT monetary amount must use Decimal precision.")
            elif entities.amount <= Decimal("0.00"):
                errors.append("PAYMENT monetary amount must be strictly positive (> 0.00).")

            if not entities.currency:
                errors.append("PAYMENT intent requires explicit currency code.")
            elif entities.currency.upper() not in SUPPORTED_CURRENCIES:
                errors.append(f"Unsupported payment currency code '{entities.currency}'.")

        elif category_upper == "REFUND":
            if entities.amount is not None:
                if not isinstance(entities.amount, Decimal):
                    errors.append("REFUND monetary amount must use Decimal precision.")
                elif entities.amount <= Decimal("0.00"):
                    errors.append("REFUND monetary amount must be positive.")
                if not entities.currency:
                    errors.append("REFUND intent with amount requires explicit currency code.")

        elif category_upper == "UNKNOWN":
            # UNKNOWN intent is a valid representation, but NEVER execution-eligible
            pass

        # Determine overall validity and downstream execution eligibility
        is_valid = len(errors) == 0
        is_execution_eligible = (
            is_valid and category_upper != "UNKNOWN" and intent.confidence >= Decimal("0.50")
        )

        logger.info(
            "Intent validated",
            extra={
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "category": category_upper,
                "is_valid": is_valid,
                "is_execution_eligible": is_execution_eligible,
                "error_count": len(errors),
            },
        )

        return IntentValidationResult(
            is_valid=is_valid,
            intent_category=category_upper,
            validation_errors=errors,
            is_execution_eligible=is_execution_eligible,
            validated_at=now,
        )
