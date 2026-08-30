"""Agent Violation Tracking Application Service for AGENTPAY (Phase 209)."""

from __future__ import annotations

import inspect
import logging
from collections import Counter
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.payment_order import PaymentOrder
from app.schemas.agent_violations import (
    AgentViolation,
    AgentViolationQueryRequest,
    AgentViolationQueryResponse,
)

logger = logging.getLogger("agentguard.security.agent_violation_tracking")


class AgentViolationTrackingService:
    """Production Agent Violation Tracking Service (Phase 209 - Read/Query Only)."""

    async def get_agent_violations(
        self,
        db: AsyncSession | Any,
        request: AgentViolationQueryRequest,
    ) -> AgentViolationQueryResponse:
        """Query authoritative historical violations for an agent (Phase 209)."""
        now = datetime.now(UTC)

        stmt = (
            select(PaymentOrder)
            .where(
                PaymentOrder.tenant_id == request.tenant_id,
                PaymentOrder.agent_id == request.agent_id,
                PaymentOrder.status.in_(["failed", "cancelled", "expired"]),
            )
            .order_by(PaymentOrder.created_at.desc())
            .limit(request.limit)
        )

        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res
        orders: list[PaymentOrder] = list(res.scalars().all()) if hasattr(res, "scalars") else []

        type_counter = Counter([o.status for o in orders if hasattr(o, "status")])

        violations: list[AgentViolation] = []
        for order in orders:
            if hasattr(order, "agent_id") and hasattr(order, "status"):
                rec_count = type_counter[order.status]
                severity = (
                    "CRITICAL"
                    if rec_count >= 5
                    else ("HIGH" if order.status == "failed" else "MEDIUM")
                )
                violations.append(
                    AgentViolation(
                        violation_id=order.id,
                        tenant_id=order.tenant_id,
                        agent_id=order.agent_id or request.agent_id,
                        violation_type=f"PAYMENT_ORDER_{order.status.upper()}",
                        severity=severity,
                        occurred_at=(
                            order.created_at.replace(tzinfo=UTC)
                            if order.created_at and order.created_at.tzinfo is None
                            else (order.created_at or now)
                        ),
                        source="PAYMENT_ORDER",
                        status="ACTIVE",
                        recurrence_count=rec_count,
                        policy_id=getattr(order, "policy_id", None),
                    )
                )

        return AgentViolationQueryResponse(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            violations=violations,
            total_count=len(violations),
            retrieved_at=now,
        )
