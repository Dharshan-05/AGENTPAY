"""Authoritative Daily Spending Usage Database Provider for AGENTPAY (Phase 190)."""

from __future__ import annotations

import inspect
import logging
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.payment_order import PaymentOrder

logger = logging.getLogger("agentguard.infrastructure.daily_spending_usage")


class DailySpendingUsageProvider:
    """Authoritative database provider for querying cumulative spending usage (Phase 190)."""

    async def get_daily_spending_usage(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        window_start: datetime,
        window_end: datetime,
        currency: str = "USD",
    ) -> Decimal:
        """Query sum of qualifying transactions within tenant/agent daily window (Phase 190)."""
        stmt = select(func.coalesce(func.sum(PaymentOrder.total_amount), 0)).where(
            PaymentOrder.tenant_id == tenant_id,
            PaymentOrder.agent_id == agent_id,
            PaymentOrder.status.in_(["completed", "authorized", "pending", "created", "paid"]),
            PaymentOrder.currency_code == currency.upper(),
            PaymentOrder.created_at >= window_start,
            PaymentOrder.created_at <= window_end,
        )

        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res

        total_raw = res.scalar_one() if hasattr(res, "scalar_one") else 0
        return Decimal(str(total_raw))
