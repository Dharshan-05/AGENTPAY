"""Spending Limit Evaluation Service for AGENTPAY (Phase 189)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal

from app.schemas.spending_limits import (
    SpendingLimitEvaluationRequest,
    SpendingLimitEvaluationResult,
)

logger = logging.getLogger("agentguard.security.spending_limit_service")


class SpendingLimitService:
    """Production Spending Limit Evaluation Engine (Phase 189 - Read/Decision Only)."""

    def evaluate_spending_limit(
        self,
        request: SpendingLimitEvaluationRequest,
        cumulative_usage: Decimal = Decimal("0.00"),
    ) -> SpendingLimitEvaluationResult:
        """Evaluate single proposed transaction against configured spending limit (Phase 189)."""
        now = datetime.now(UTC)

        # 1. Invalid transaction amount validation
        if request.amount <= Decimal("0.00"):
            return SpendingLimitEvaluationResult(
                agent_id=request.agent_id,
                tenant_id=request.tenant_id,
                amount=request.amount,
                limit_amount=request.configured_limit,
                currency=request.currency,
                decision="INVALID_AMOUNT",
                reason_code="AMOUNT_MUST_BE_POSITIVE",
                explanation="Transaction amount must be strictly greater than zero.",
                evaluated_at=now,
            )

        # 2. Currency mismatch check (Fail-closed)
        if request.currency.strip().upper() != request.limit_currency.strip().upper():
            logger.warning(
                "Spending limit currency mismatch: request %s != limit %s",
                request.currency,
                request.limit_currency,
            )
            return SpendingLimitEvaluationResult(
                agent_id=request.agent_id,
                tenant_id=request.tenant_id,
                amount=request.amount,
                limit_amount=request.configured_limit,
                currency=request.currency,
                decision="INVALID_CURRENCY",
                reason_code="CURRENCY_MISMATCH",
                explanation=f"Currency mismatch: transaction ({request.currency}) != limit ({request.limit_currency}).",  # noqa: E501
                evaluated_at=now,
            )

        # 3. Projected spending calculation (Decimal precision)
        projected_total = cumulative_usage + request.amount

        # 4. Limit boundary decision
        if projected_total <= request.configured_limit:
            return SpendingLimitEvaluationResult(
                agent_id=request.agent_id,
                tenant_id=request.tenant_id,
                amount=request.amount,
                limit_amount=request.configured_limit,
                currency=request.currency,
                decision="WITHIN_LIMIT",
                reason_code="SPENDING_WITHIN_LIMIT",
                explanation=f"Projected spending ({projected_total} {request.currency}) is within configured limit ({request.configured_limit} {request.currency}).",  # noqa: E501
                evaluated_at=now,
            )

        # 5. Over limit behavior depending on enforcement mode
        if request.enforcement_mode in ("block", "enforce"):
            return SpendingLimitEvaluationResult(
                agent_id=request.agent_id,
                tenant_id=request.tenant_id,
                amount=request.amount,
                limit_amount=request.configured_limit,
                currency=request.currency,
                decision="LIMIT_EXCEEDED",
                reason_code="SPENDING_LIMIT_EXCEEDED",
                explanation=f"Projected spending ({projected_total} {request.currency}) exceeds configured limit ({request.configured_limit} {request.currency}).",  # noqa: E501
                evaluated_at=now,
            )

        return SpendingLimitEvaluationResult(
            agent_id=request.agent_id,
            tenant_id=request.tenant_id,
            amount=request.amount,
            limit_amount=request.configured_limit,
            currency=request.currency,
            decision="REQUIRES_APPROVAL",
            reason_code="SPENDING_LIMIT_REQUIRES_APPROVAL",
            explanation=f"Projected spending ({projected_total} {request.currency}) exceeds limit but mode is '{request.enforcement_mode}'. Human approval required.",  # noqa: E501
            evaluated_at=now,
        )
