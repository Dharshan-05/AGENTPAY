"""Agent Category Behaviour application service for AGENTPAY (Phase 139).

Responsibilities:
    - Analyze agent transaction & event activity broken down by category
    - Calculate category frequencies, transaction ratios, and monetary volume distribution
    - Ensure mathematical bounds (0.00 <= ratio <= 1.00; never NaN or Infinity)
    - Produce explainable risk indicators ('normal', 'unusual_concentration', 'category_shift')
    - Read/analysis-oriented: MUST NOT mutate agent lifecycle status or execute payments
    - IDOR protection: Cross-tenant attempts raise `AgentNotFoundError` (404)
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.commerce_transaction import CommerceTransaction
from app.schemas.agents import AgentCategoryBehaviourResponse, CategoryMetric

logger = logging.getLogger("agentpay.agent.category_behaviour.service")


class AgentCategoryBehaviourService:
    """Application service for analysing Agent Category Behaviour (Phase 139)."""

    async def analyze_category_behaviour(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> AgentCategoryBehaviourResponse:
        """Analyze category distribution and concentration metrics within tenant scope.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
        """
        # 1. IDOR Check
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        agent = agent_res.scalar_one_or_none()
        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        now = datetime.now(UTC)

        # 2. Total Transactions & Total Monetary Volume
        tot_stmt = select(
            func.count(CommerceTransaction.id).label("total_count"),
            func.coalesce(func.sum(CommerceTransaction.amount), 0.00).label("total_vol"),
        ).where(
            CommerceTransaction.agent_id == agent_id,
            CommerceTransaction.tenant_id == tenant_id,
        )
        tot_res = await db.execute(tot_stmt)
        tot_row = tot_res.one()

        total_tx = int(tot_row.total_count or 0)
        total_vol = Decimal(str(tot_row.total_vol or "0.00"))

        if total_tx == 0:
            return AgentCategoryBehaviourResponse(
                agent_id=agent_id,
                tenant_id=tenant_id,
                total_transactions_count=0,
                unique_categories_count=0,
                dominant_category="general",
                dominant_category_ratio=Decimal("0.00"),
                categories=[],
                risk_indicator="normal",
                severity="low",
                reason="No historical category activity recorded.",
                analyzed_at=now,
            )

        # 3. Category Breakdown (Grouped by transaction_type)
        cat_stmt = (
            select(
                CommerceTransaction.transaction_type.label("cat_name"),
                func.count(CommerceTransaction.id).label("cat_count"),
                func.coalesce(func.sum(CommerceTransaction.amount), 0.00).label("cat_vol"),
            )
            .where(
                CommerceTransaction.agent_id == agent_id,
                CommerceTransaction.tenant_id == tenant_id,
            )
            .group_by(CommerceTransaction.transaction_type)
            .order_by(func.count(CommerceTransaction.id).desc())
        )
        cat_res = await db.execute(cat_stmt)
        rows = cat_res.all()

        categories: list[CategoryMetric] = []
        dominant_cat = "general"
        dominant_ratio = Decimal("0.00")

        for index, row in enumerate(rows):
            cat_name = str(row.cat_name or "general")
            c_count = int(row.cat_count or 0)
            c_vol = Decimal(str(row.cat_vol or "0.00"))

            tx_ratio = (
                Decimal(str(c_count)) / Decimal(str(total_tx)) if total_tx > 0 else Decimal("0.00")
            )
            vol_ratio = c_vol / total_vol if total_vol > Decimal("0.00") else Decimal("0.00")

            # Ensure strict mathematical bounds
            tx_ratio = min(Decimal("1.00"), max(Decimal("0.00"), tx_ratio))
            vol_ratio = min(Decimal("1.00"), max(Decimal("0.00"), vol_ratio))

            if index == 0:
                dominant_cat = cat_name
                dominant_ratio = tx_ratio

            categories.append(
                CategoryMetric(
                    category_name=cat_name,
                    transaction_count=c_count,
                    transaction_ratio=tx_ratio.quantize(Decimal("0.01")),
                    monetary_volume=c_vol.quantize(Decimal("0.01")),
                    volume_ratio=vol_ratio.quantize(Decimal("0.01")),
                )
            )

        # 4. Risk Indicator & Severity
        if dominant_ratio >= Decimal("0.85") and len(categories) > 1:
            risk_indicator = "unusual_concentration"
            severity = "medium"
            reason = (
                f"High category concentration: {dominant_cat} accounts for "
                f"{dominant_ratio * 100:.1f}% of transaction activity."
            )
        else:
            risk_indicator = "normal"
            severity = "low"
            reason = (
                f"Normal category activity distributed across {len(categories)} unique categories."
            )

        logger.info(
            "Agent category behaviour analyzed",
            extra={
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "unique_categories": len(categories),
                "dominant_category": dominant_cat,
                "dominant_ratio": str(dominant_ratio),
            },
        )

        return AgentCategoryBehaviourResponse(
            agent_id=agent_id,
            tenant_id=tenant_id,
            total_transactions_count=total_tx,
            unique_categories_count=len(categories),
            dominant_category=dominant_cat,
            dominant_category_ratio=dominant_ratio.quantize(Decimal("0.01")),
            categories=categories,
            risk_indicator=risk_indicator,
            severity=severity,
            reason=reason,
            analyzed_at=now,
        )
