"""Behaviour Tracking Application Service for AGENTPAY (Phase 200)."""

from __future__ import annotations

import inspect
import logging
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.payment_order import PaymentOrder
from app.schemas.behaviour_tracking import (
    BehaviourEvent,
    BehaviourTrackingQueryRequest,
    BehaviourTrackingQueryResponse,
)

logger = logging.getLogger("agentguard.security.behaviour_tracking")


class BehaviourTrackingService:
    """Production Behaviour Tracking Subsystem (Phase 200 - Read/Query Only)."""

    async def get_agent_events(
        self,
        db: AsyncSession | Any,
        request: BehaviourTrackingQueryRequest,
    ) -> BehaviourTrackingQueryResponse:
        """Query and normalize authoritative historical activity events for an agent (Phase 200)."""  # noqa: E501
        now = datetime.now(UTC)

        # Build query over authoritative PaymentOrder entity
        stmt = select(PaymentOrder).where(
            PaymentOrder.tenant_id == request.tenant_id,
            PaymentOrder.agent_id == request.agent_id,
        )

        if request.start_time:
            stmt = stmt.where(PaymentOrder.created_at >= request.start_time)
        if request.end_time:
            stmt = stmt.where(PaymentOrder.created_at <= request.end_time)

        stmt = stmt.order_by(PaymentOrder.created_at.desc()).limit(request.limit)

        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res

        orders: list[PaymentOrder] = []
        if hasattr(res, "scalars") and callable(getattr(res, "scalars", None)):

            try:
                scalars_obj = res.scalars()
                if inspect.isawaitable(scalars_obj):
                    scalars_obj = await scalars_obj
                if hasattr(scalars_obj, "all") and callable(getattr(scalars_obj, "all", None)):
                    all_res = scalars_obj.all()
                    if inspect.isawaitable(all_res):
                        all_res = await all_res
                    if isinstance(all_res, (list, tuple, set)):
                        orders = list(all_res)
            except Exception:
                orders = []



        events: list[BehaviourEvent] = []
        for order in orders:
            if hasattr(order, "agent_id") and hasattr(order, "total_amount"):
                outcome = (
                    "SUCCESS" if order.status in ("completed", "authorized", "paid") else "FAILED"
                )
                events.append(
                    BehaviourEvent(
                        event_id=order.id,
                        tenant_id=order.tenant_id,
                        agent_id=order.agent_id or request.agent_id,
                        event_type="PAYMENT",
                        occurred_at=(
                            order.created_at.replace(tzinfo=UTC)
                            if order.created_at and order.created_at.tzinfo is None
                            else (order.created_at or now)
                        ),
                        amount=Decimal(str(order.total_amount)),
                        currency=order.currency_code,
                        merchant_id=getattr(order, "merchant_id", None),
                        category=None,
                        status=order.status,
                        outcome=outcome,
                    )
                )

        return BehaviourTrackingQueryResponse(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            events=events,
            total_count=len(events),
            retrieved_at=now,
        )
