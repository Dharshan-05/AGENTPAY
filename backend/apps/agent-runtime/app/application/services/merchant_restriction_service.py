"""Merchant Restriction Evaluation Service for AGENTPAY (Phase 193)."""

from __future__ import annotations

import inspect
import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.agent_exceptions import MerchantNotFoundError
from app.infrastructure.database.models.merchant import Merchant
from app.schemas.merchant_restrictions import (
    MerchantRestrictionEvaluationRequest,
    MerchantRestrictionEvaluationResult,
)

logger = logging.getLogger("agentguard.security.merchant_restriction_service")


class MerchantRestrictionService:
    """Production Merchant Restriction Evaluation Engine (Phase 193 - Read/Decision Only)."""

    async def evaluate_merchant_restriction(
        self,
        db: AsyncSession | Any,
        request: MerchantRestrictionEvaluationRequest,
    ) -> MerchantRestrictionEvaluationResult:
        """Evaluate target merchant against tenant allowlist/denylist rules (Phase 193)."""
        now = datetime.now(UTC)

        # 1. Missing merchant handling
        if not request.merchant_id and not request.merchant_slug:
            if request.allowed_merchants:
                return MerchantRestrictionEvaluationResult(
                    agent_id=request.agent_id,
                    tenant_id=request.tenant_id,
                    merchant_id=None,
                    decision="DENIED",
                    reason_code="MERCHANT_NOT_ALLOWED",
                    explanation="Merchant identification missing but restrictive allowlist policies apply.",  # noqa: E501
                    evaluated_at=now,
                )
            return MerchantRestrictionEvaluationResult(
                agent_id=request.agent_id,
                tenant_id=request.tenant_id,
                merchant_id=None,
                decision="ALLOW",
                reason_code="MERCHANT_NOT_RESTRICTED",
                explanation="No merchant provided and no merchant restrictions configured.",
                evaluated_at=now,
            )

        # 2. Resolve merchant within strict tenant boundary
        stmt = select(Merchant).where(
            Merchant.tenant_id == request.tenant_id,
            Merchant.deleted_at.is_(None),
        )
        if request.merchant_id:
            stmt = stmt.where(Merchant.id == request.merchant_id)
        elif request.merchant_slug:
            stmt = stmt.where(Merchant.slug == request.merchant_slug)

        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res
        merchant: Merchant | None = res.scalars().first() if hasattr(res, "scalars") else None

        if not merchant:
            raise MerchantNotFoundError(
                f"Merchant '{request.merchant_id or request.merchant_slug}' not found in tenant boundary."  # noqa: E501
            )

        # 3. Check merchant status (Inactive, suspended, archived => DENIED)
        if merchant.status != "active":
            return MerchantRestrictionEvaluationResult(
                agent_id=request.agent_id,
                tenant_id=request.tenant_id,
                merchant_id=merchant.id,
                decision="DENIED",
                reason_code="MERCHANT_INACTIVE",
                explanation=f"Merchant '{merchant.name}' is currently {merchant.status} and cannot process transactions.",  # noqa: E501
                evaluated_at=now,
            )

        # 4. Normalize merchant IDs & Slugs
        m_id_str = str(merchant.id).lower()
        m_slug_str = merchant.slug.lower()
        norm_blocked = [m.strip().lower() for m in request.blocked_merchants if m.strip()]
        norm_allowed = [m.strip().lower() for m in request.allowed_merchants if m.strip()]

        # 5. Explicit Denylist Precedence Check (DENY > ALLOW)
        if m_id_str in norm_blocked or m_slug_str in norm_blocked:
            return MerchantRestrictionEvaluationResult(
                agent_id=request.agent_id,
                tenant_id=request.tenant_id,
                merchant_id=merchant.id,
                decision="DENIED",
                reason_code="MERCHANT_DENIED",
                explanation=f"Merchant '{merchant.name}' is explicitly blocked by security policy.",  # noqa: E501
                evaluated_at=now,
            )

        # 6. Explicit Allowlist Check
        if norm_allowed:
            if m_id_str not in norm_allowed and m_slug_str not in norm_allowed:
                return MerchantRestrictionEvaluationResult(
                    agent_id=request.agent_id,
                    tenant_id=request.tenant_id,
                    merchant_id=merchant.id,
                    decision="DENIED",
                    reason_code="MERCHANT_NOT_ALLOWED",
                    explanation=f"Merchant '{merchant.name}' is not present in policy allowlist.",
                    evaluated_at=now,
                )

        # 7. Permitted merchant -> ALLOW
        return MerchantRestrictionEvaluationResult(
            agent_id=request.agent_id,
            tenant_id=request.tenant_id,
            merchant_id=merchant.id,
            decision="ALLOW",
            reason_code="MERCHANT_ALLOWED",
            explanation=f"Merchant '{merchant.name}' is permitted by security policy.",
            evaluated_at=now,
        )
