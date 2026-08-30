"""Daily Spending Limit Application Service for AGENTPAY (Phase 190)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, time
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.spending_limit_service import SpendingLimitService
from app.infrastructure.database.providers.daily_spending_usage_provider import (
    DailySpendingUsageProvider,
)
from app.schemas.daily_spending_limits import DailySpendingLimitResult
from app.schemas.spending_limits import SpendingLimitEvaluationRequest

logger = logging.getLogger("agentguard.security.daily_spending_limit_service")


class DailySpendingLimitService:
    """Production Daily Spending Limit Engine (Phase 190 - Read/Decision Only)."""

    def __init__(
        self,
        usage_provider: DailySpendingUsageProvider | None = None,
        spending_limit_service: SpendingLimitService | None = None,
    ) -> None:
        self.usage_provider = usage_provider or DailySpendingUsageProvider()
        self.spending_limit_service = spending_limit_service or SpendingLimitService()

    async def evaluate_daily_spending_limit(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        amount: Decimal,
        configured_daily_limit: Decimal,
        *,
        currency: str = "USD",
        limit_currency: str = "USD",
        enforcement_mode: str = "enforce",
    ) -> DailySpendingLimitResult:
        """Evaluate daily cumulative spending limit for an agent (Phase 190)."""
        now = datetime.now(UTC)

        # 1. Deterministic Daily Window Calculation (UTC Midnight to Midnight)
        start_of_day = datetime.combine(now.date(), time.min, tzinfo=UTC)
        end_of_day = datetime.combine(now.date(), time.max, tzinfo=UTC)

        # 2. Query Authoritative Cumulative Usage
        current_usage = await self.usage_provider.get_daily_spending_usage(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            window_start=start_of_day,
            window_end=end_of_day,
            currency=currency,
        )

        projected_usage = current_usage + amount
        remaining_limit = max(Decimal("0.00"), configured_daily_limit - current_usage)

        # 3. Evaluate via SpendingLimitService
        req = SpendingLimitEvaluationRequest(
            tenant_id=tenant_id,
            agent_id=agent_id,
            amount=amount,
            currency=currency,
            configured_limit=configured_daily_limit,
            limit_currency=limit_currency,
            enforcement_mode=enforcement_mode,
        )
        base_res = self.spending_limit_service.evaluate_spending_limit(
            req, cumulative_usage=current_usage
        )

        reason_code = f"DAILY_{base_res.reason_code}"
        explanation = (
            f"Daily spending limit check ({base_res.decision}): "
            f"current usage={current_usage} {currency}, requested={amount} {currency}, "
            f"projected={projected_usage} {currency}, daily limit={configured_daily_limit} {currency}."  # noqa: E501
        )

        return DailySpendingLimitResult(
            agent_id=agent_id,
            tenant_id=tenant_id,
            daily_limit=configured_daily_limit,
            current_usage=current_usage,
            requested_amount=amount,
            projected_usage=projected_usage,
            remaining_limit=remaining_limit,
            currency=currency,
            decision=base_res.decision,
            reason_code=reason_code,
            explanation=explanation,
            evaluation_period_start=start_of_day,
            evaluation_period_end=end_of_day,
            evaluated_at=now,
        )
