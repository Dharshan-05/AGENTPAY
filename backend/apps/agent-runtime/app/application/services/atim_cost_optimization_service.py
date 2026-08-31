"""ATIM Cost Optimization & Quota Enforcement Service (Phase 12 / Group 6)."""

import logging
from decimal import Decimal
from typing import Any, Optional
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.governance.models import CostBudgetRecord
from app.infrastructure.database.models.atim_governance import ATIMCostBudget

logger = logging.getLogger("agentpay.atim.cost_optimization")


class ATIMCostOptimizationService:
    """Service enforcing tenant & agent LLM cost budget quotas and cost-efficiency routing."""

    def __init__(
        self,
        default_max_per_request: Decimal = Decimal("0.050000"),
        default_daily_budget: Decimal = Decimal("50.000000"),
        default_monthly_budget: Decimal = Decimal("1000.000000"),
    ) -> None:
        self.default_max_per_request = default_max_per_request
        self.default_daily_budget = default_daily_budget
        self.default_monthly_budget = default_monthly_budget
        self._in_memory_budgets: dict[uuid.UUID, CostBudgetRecord] = {}

    async def get_or_create_budget(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        agent_id: Optional[uuid.UUID] = None,
    ) -> CostBudgetRecord:
        """Fetch active cost budget quota for tenant or agent."""
        if tenant_id in self._in_memory_budgets:
            return self._in_memory_budgets[tenant_id]

        budget = CostBudgetRecord(
            tenant_id=tenant_id,
            agent_id=agent_id,
            max_cost_per_request=self.default_max_per_request,
            daily_budget_usd=self.default_daily_budget,
            monthly_budget_usd=self.default_monthly_budget,
            current_daily_spend_usd=Decimal("0.000000"),
            current_monthly_spend_usd=Decimal("0.000000"),
        )
        self._in_memory_budgets[tenant_id] = budget
        return budget

    async def check_budget_eligibility(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        estimated_cost_usd: Decimal,
        agent_id: Optional[uuid.UUID] = None,
    ) -> tuple[bool, str]:
        """Check if request cost fits within tenant/agent quotas.

        Returns:
            Tuple of (is_eligible: bool, rejection_reason: str)
        """
        budget = await self.get_or_create_budget(db, tenant_id, agent_id)

        # 1. Per-request cost check
        if estimated_cost_usd > budget.max_cost_per_request:
            msg = f"Request cost ${estimated_cost_usd} exceeds max per-request limit ${budget.max_cost_per_request}"
            logger.warning("Cost budget violation for tenant %s: %s", tenant_id, msg)
            return False, msg

        # 2. Daily budget check
        if (budget.current_daily_spend_usd + estimated_cost_usd) > budget.daily_budget_usd:
            msg = f"Cumulative daily spend ${budget.current_daily_spend_usd + estimated_cost_usd} exceeds daily quota ${budget.daily_budget_usd}"
            logger.warning("Cost budget violation for tenant %s: %s", tenant_id, msg)
            return False, msg

        # 3. Monthly budget check
        if (budget.current_monthly_spend_usd + estimated_cost_usd) > budget.monthly_budget_usd:
            msg = f"Cumulative monthly spend ${budget.current_monthly_spend_usd + estimated_cost_usd} exceeds monthly quota ${budget.monthly_budget_usd}"
            logger.warning("Cost budget violation for tenant %s: %s", tenant_id, msg)
            return False, msg

        return True, "Budget quota check passed"

    async def record_spend(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        actual_cost_usd: Decimal,
        agent_id: Optional[uuid.UUID] = None,
    ) -> None:
        """Accumulate actual expenditure into tenant budget counters."""
        budget = await self.get_or_create_budget(db, tenant_id, agent_id)
        budget.current_daily_spend_usd += actual_cost_usd
        budget.current_monthly_spend_usd += actual_cost_usd
        self._in_memory_budgets[tenant_id] = budget
        logger.info(
            "Accumulated spend of $%s for tenant %s. Daily total: $%s",
            actual_cost_usd,
            tenant_id,
            budget.current_daily_spend_usd,
        )
