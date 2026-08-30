"""Merchant Behaviour Analysis application service for AGENTPAY (Phase 138).

Responsibilities:
    - Analyze merchant interaction frequency, concentration ratio, and new merchant addition rate
    - Detect unusual merchant concentration or sudden bursts of new merchant interactions
    - Generate explainable merchant pattern deviation results
    - Read/analysis-oriented: MUST NOT mutate agent lifecycle state or execute payments
    - STRICT SCOPE: Category Behaviour Analysis (Phase 139) is strictly excluded
    - IDOR protection: Cross-tenant attempts raise `AgentNotFoundError` (404)
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.commerce_transaction import CommerceTransaction
from app.schemas.agents import AgentMerchantBehaviourResponse

logger = logging.getLogger("agentpay.agent.merchant_behaviour.service")


class AgentMerchantBehaviourService:
    """Application service for analysing Agent Merchant Behaviour patterns (Phase 138)."""

    async def analyze_merchant_behaviour(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> AgentMerchantBehaviourResponse:
        """Analyze merchant interaction patterns for an agent within tenant scope.

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
        seven_days_ago = now - timedelta(days=7)

        # 2. Total Transactions & Unique Merchants
        tx_stmt = select(
            func.count(CommerceTransaction.id).label("total_count"),
            func.count(func.distinct(CommerceTransaction.merchant_id)).label("unique_merchants"),
            func.coalesce(func.sum(CommerceTransaction.amount), 0.00).label("total_vol"),
        ).where(
            CommerceTransaction.agent_id == agent_id,
            CommerceTransaction.tenant_id == tenant_id,
        )
        tx_res = await db.execute(tx_stmt)
        tx_row = tx_res.one()

        total_tx = int(tx_row.total_count or 0)
        unique_merchants = int(tx_row.unique_merchants or 0)
        total_amount = Decimal(str(tx_row.total_vol or "0.00"))

        if total_tx == 0:
            return AgentMerchantBehaviourResponse(
                agent_id=agent_id,
                tenant_id=tenant_id,
                unique_merchants_count=0,
                top_merchant_concentration=Decimal("0.00"),
                new_merchants_last_7d=0,
                total_transactions_count=0,
                total_amount=Decimal("0.00"),
                deviation_score=Decimal("0.00"),
                risk_indicator="normal",
                severity="low",
                reason="No historical merchant transactions recorded.",
                evaluated_at=now,
            )

        # 3. Top Merchant Concentration Ratio
        top_m_stmt = (
            select(
                CommerceTransaction.merchant_id,
                func.count(CommerceTransaction.id).label("m_count"),
            )
            .where(
                CommerceTransaction.agent_id == agent_id,
                CommerceTransaction.tenant_id == tenant_id,
            )
            .group_by(CommerceTransaction.merchant_id)
            .order_by(func.count(CommerceTransaction.id).desc())
            .limit(1)
        )
        top_m_res = await db.execute(top_m_stmt)
        top_m_row = top_m_res.one_or_none()

        top_m_count = int(top_m_row.m_count) if top_m_row else 0
        concentration_ratio = (
            Decimal(str(top_m_count)) / Decimal(str(total_tx)) if total_tx > 0 else Decimal("0.00")
        )

        # 4. New Merchants in Last 7 Days
        new_m_stmt = select(func.count(func.distinct(CommerceTransaction.merchant_id))).where(
            CommerceTransaction.agent_id == agent_id,
            CommerceTransaction.tenant_id == tenant_id,
            CommerceTransaction.created_at >= seven_days_ago,
        )
        new_m_res = await db.execute(new_m_stmt)
        new_m_count = int(new_m_res.scalar() or 0)

        # 5. Risk Assessment & Deviation Score
        if new_m_count >= 5:
            risk_indicator = "new_merchant_burst"
            deviation_score = Decimal("75.00")
            severity = "high"
            reason = f"High burst of {new_m_count} new merchant interactions in past 7 days."
        elif concentration_ratio >= Decimal("0.90") and total_tx >= 10:
            risk_indicator = "unusual_concentration"
            deviation_score = Decimal("60.00")
            severity = "medium"
            reason = (
                f"High merchant concentration: top merchant represents "
                f"{concentration_ratio * 100:.1f}% of transactions."
            )
        else:
            risk_indicator = "normal"
            deviation_score = Decimal("0.00")
            severity = "low"
            reason = (
                f"Normal merchant interaction pattern across {unique_merchants} unique merchants."
            )

        logger.info(
            "Agent merchant behaviour evaluated",
            extra={
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "unique_merchants": unique_merchants,
                "concentration_ratio": str(concentration_ratio),
                "risk_indicator": risk_indicator,
            },
        )

        return AgentMerchantBehaviourResponse(
            agent_id=agent_id,
            tenant_id=tenant_id,
            unique_merchants_count=unique_merchants,
            top_merchant_concentration=concentration_ratio.quantize(Decimal("0.01")),
            new_merchants_last_7d=new_m_count,
            total_transactions_count=total_tx,
            total_amount=total_amount.quantize(Decimal("0.01")),
            deviation_score=deviation_score.quantize(Decimal("0.01")),
            risk_indicator=risk_indicator,
            severity=severity,
            reason=reason,
            evaluated_at=now,
        )
