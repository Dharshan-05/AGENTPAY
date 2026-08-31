"""ATIM Enterprise Quota Engine (Phase 18 / Group 9)."""

from decimal import Decimal
import logging
from typing import Any, Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.governance.policy_models import QuotaRecord
from app.infrastructure.database.models.atim_policy import ATIMQuotaUsage

logger = logging.getLogger("agentpay.atim.quota")


class ATIMQuotaService:
    """Service enforcing request, token, and monetary quotas with Decimal precision."""

    def __init__(self) -> None:
        self._quotas: dict[tuple[uuid.UUID, Optional[uuid.UUID]], QuotaRecord] = {}

    def get_or_create_quota(
        self,
        tenant_id: uuid.UUID,
        agent_id: Optional[uuid.UUID] = None,
    ) -> QuotaRecord:
        """Get or initialize quota record for tenant and optional agent."""
        key = (tenant_id, agent_id)
        if key not in self._quotas:
            self._quotas[key] = QuotaRecord(
                tenant_id=tenant_id,
                agent_id=agent_id,
                max_requests_per_minute=120,
                max_requests_per_day=10000,
                max_tokens_per_day=1000000,
                max_cost_per_day_usd=Decimal("50.000000"),
            )
        return self._quotas[key]

    def check_and_consume_quota(
        self,
        tenant_id: uuid.UUID,
        tokens_requested: int = 100,
        cost_requested_usd: Decimal = Decimal("0.001500"),
        agent_id: Optional[uuid.UUID] = None,
    ) -> tuple[bool, str, QuotaRecord]:
        """Check if request fits within tenant/agent quota, and consume quota if allowed.

        Returns:
            Tuple of (is_allowed: bool, reason: str, updated_quota: QuotaRecord)
        """
        quota = self.get_or_create_quota(tenant_id, agent_id)

        if quota.current_daily_requests + 1 > quota.max_requests_per_day:
            reason = f"Daily request quota exceeded ({quota.current_daily_requests}/{quota.max_requests_per_day})."
            logger.warning("Quota violation for Tenant %s: %s", tenant_id, reason)
            return False, reason, quota

        if quota.current_daily_tokens + tokens_requested > quota.max_tokens_per_day:
            reason = f"Daily token quota exceeded ({quota.current_daily_tokens + tokens_requested}/{quota.max_tokens_per_day})."
            logger.warning("Quota violation for Tenant %s: %s", tenant_id, reason)
            return False, reason, quota

        if quota.current_daily_cost_usd + cost_requested_usd > quota.max_cost_per_day_usd:
            reason = f"Daily cost quota exceeded (${quota.current_daily_cost_usd + cost_requested_usd:.4f}/${quota.max_cost_per_day_usd:.2f})."
            logger.warning("Quota violation for Tenant %s: %s", tenant_id, reason)
            return False, reason, quota

        # Consume quota
        quota.current_daily_requests += 1
        quota.current_daily_tokens += tokens_requested
        quota.current_daily_cost_usd += cost_requested_usd

        return True, "Quota check passed.", quota
