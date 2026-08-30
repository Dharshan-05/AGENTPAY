"""Velocity Detection Application Service for AGENTPAY (Phase 203)."""

from __future__ import annotations

import inspect
import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.payment_order import PaymentOrder
from app.schemas.velocity_detection import (
    VelocityDetectionRequest,
    VelocityDetectionResult,
)

logger = logging.getLogger("agentguard.security.velocity_detection")


class VelocityDetectionService:
    """Production Velocity Detection Engine (Phase 203 - Read/Analysis Only)."""

    async def detect_velocity(
        self,
        db: AsyncSession | Any,
        request: VelocityDetectionRequest,
    ) -> VelocityDetectionResult:
        """Analyze agent transaction velocity over bounded time windows (Phase 203)."""
        now = datetime.now(UTC)
        end_time = request.window_end or now
        start_time = request.window_start or (end_time - timedelta(minutes=request.window_minutes))

        if start_time >= end_time:
            start_time = end_time - timedelta(minutes=request.window_minutes)

        # Query authoritative PaymentOrder table in tenant and agent scope
        stmt = select(PaymentOrder).where(
            PaymentOrder.tenant_id == request.tenant_id,
            PaymentOrder.agent_id == request.agent_id,
            PaymentOrder.created_at >= start_time,
            PaymentOrder.created_at <= end_time,
        )

        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res
        orders: list[PaymentOrder] = list(res.scalars().all()) if hasattr(res, "scalars") else []

        # Filter valid order entities
        valid_orders = [o for o in orders if hasattr(o, "total_amount")]
        tx_count = len(valid_orders)
        total_amount = sum([Decimal(str(o.total_amount)) for o in valid_orders], Decimal("0.00"))

        duration_seconds = max((end_time - start_time).total_seconds(), 1.0)
        duration_minutes = Decimal(str(round(duration_seconds / 60.0, 4)))
        duration_hours = Decimal(str(round(duration_seconds / 3600.0, 4)))

        tx_per_min = (
            round(Decimal(str(tx_count)) / duration_minutes, 2)
            if duration_minutes > Decimal("0.00")
            else Decimal("0.00")
        )
        tx_per_hour = (
            round(Decimal(str(tx_count)) / duration_hours, 2)
            if duration_hours > Decimal("0.00")
            else Decimal("0.00")
        )

        reason_codes: list[str] = []
        severity = "NORMAL"
        detection_state = "NORMAL"
        velocity_score = Decimal("0.00")

        if request.max_allowed_count is not None and tx_count > request.max_allowed_count:
            reason_codes.append("VELOCITY_COUNT_EXCEEDED")
            severity = "CRITICAL"
            detection_state = "THRESHOLD_EXCEEDED"
            velocity_score = Decimal("1.00")
        elif request.max_allowed_amount is not None and total_amount > request.max_allowed_amount:
            reason_codes.append("VELOCITY_AMOUNT_EXCEEDED")
            severity = "HIGH"
            detection_state = "THRESHOLD_EXCEEDED"
            velocity_score = Decimal("0.80")

        return VelocityDetectionResult(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            window_start=start_time,
            window_end=end_time,
            transaction_count=tx_count,
            total_amount=total_amount,
            transactions_per_minute=tx_per_min,
            transactions_per_hour=tx_per_hour,
            baseline_available=True,
            velocity_score=velocity_score,
            severity=severity,
            detection_state=detection_state,
            reason_codes=reason_codes,
            evaluated_at=now,
        )
