"""Purchase Request Pre-Execution Application Service for AGENTPAY (Phase 181)."""

from __future__ import annotations

import inspect
import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select

from app.application.services.human_approval_workflow_service import HumanApprovalWorkflowService
from app.application.services.inventory_validation_service import InventoryValidationService
from app.application.services.offer_optimization_service import OfferOptimizationService
from app.domain.exceptions.agent_exceptions import ProductNotFoundError
from app.infrastructure.database.models.purchase_intent import PurchaseIntent
from app.infrastructure.database.models.purchase_plan import PurchasePlan
from app.infrastructure.database.repositories.product_repository import ProductRepository
from app.schemas.inventory import InventoryValidationItem
from app.schemas.purchase_request import (
    PurchaseRequestCreateRequest,
    PurchaseRequestResponse,
)

logger = logging.getLogger("agentpay.purchase.request.service")

# Default approval threshold amount
_APPROVAL_THRESHOLD_AMOUNT = Decimal("500.0000")


class PurchaseRequestService:
    """Production service for pre-execution purchase request revalidation and approval integration (Phase 181)."""  # noqa: E501

    def __init__(
        self,
        repository: ProductRepository | None = None,
        planning_service: Any | None = None,
        inventory_service: InventoryValidationService | None = None,
        offer_opt_service: OfferOptimizationService | None = None,
        approval_service: HumanApprovalWorkflowService | None = None,
    ) -> None:
        self.repository = repository or ProductRepository()
        self.inventory_service = inventory_service or InventoryValidationService(self.repository)  # noqa: E501
        self.offer_opt_service = offer_opt_service or OfferOptimizationService(self.repository)
        self.approval_service = approval_service or HumanApprovalWorkflowService()

    async def create_purchase_request(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        request: PurchaseRequestCreateRequest,
        *,
        default_agent_id: uuid.UUID | None = None,
    ) -> PurchaseRequestResponse:
        """Validate purchase plan, perform revalidation for stale pricing/stock, and create pre-execution request (Phase 181)."""  # noqa: E501
        # 1. Fetch PurchasePlan in tenant boundary fail-closed
        p_stmt = select(PurchasePlan).where(
            PurchasePlan.id == request.purchase_plan_id,
            PurchasePlan.tenant_id == tenant_id,
            PurchasePlan.deleted_at.is_(None),
        )
        p_res = db.execute(p_stmt)
        if inspect.isawaitable(p_res):
            p_res = await p_res
        plan: PurchasePlan | None = p_res.scalars().first()

        if not plan:
            raise ProductNotFoundError(f"Purchase plan '{request.purchase_plan_id}' not found.")

        agent_id = plan.agent_id or default_agent_id or uuid.uuid4()
        ref_key = (
            f"req_{request.idempotency_key.strip()}"
            if request.idempotency_key and request.idempotency_key.strip()
            else f"req_{uuid.uuid4().hex[:16]}"
        )

        # 2. Revalidate items against current inventory and pricing
        meta = plan.plan_metadata or {}
        snapshot_items = meta.get("snapshot_items", [])

        inv_items: list[InventoryValidationItem] = []
        for raw in snapshot_items:
            inv_items.append(
                InventoryValidationItem(
                    product_id=uuid.UUID(raw["product_id"]),
                    requested_quantity=Decimal(str(raw["quantity"])),
                )
            )

        if inv_items:
            inv_resp = await self.inventory_service.validate_inventory(db, tenant_id, inv_items)  # noqa: E501
            if not inv_resp.all_valid:
                logger.warning(
                    "Plan %s failed inventory revalidation. Marking as REPLAN_REQUIRED", plan.id
                )
                return PurchaseRequestResponse(
                    request_id=uuid.uuid4(),
                    tenant_id=tenant_id,
                    agent_id=agent_id,
                    purchase_plan_id=plan.id,
                    status="REPLAN_REQUIRED",
                    requires_approval=False,
                    total_amount=plan.total_amount,
                    currency_code=plan.currency_code,
                    created_at=plan.created_at or datetime.now(UTC),
                )

        # Revalidate current pricing/offers
        revalidated_net_total = Decimal("0.0000")
        for raw in snapshot_items:
            pid = uuid.UUID(raw["product_id"])
            qty = Decimal(str(raw["quantity"]))
            prod = await self.repository.get_by_id(db, tenant_id, pid, include_deleted=False)
            if not prod or prod.status != "active":
                return PurchaseRequestResponse(
                    request_id=uuid.uuid4(),
                    tenant_id=tenant_id,
                    agent_id=agent_id,
                    purchase_plan_id=plan.id,
                    status="REPLAN_REQUIRED",
                    requires_approval=False,
                    total_amount=plan.total_amount,
                    currency_code=plan.currency_code,
                    created_at=plan.created_at or datetime.now(UTC),
                )

            opt_resp = await self.offer_opt_service.optimize_offer(db, tenant_id, pid, quantity=qty)  # noqa: E501
            unit_p = prod.price
            if opt_resp.has_applicable_offer and opt_resp.optimized_offer:
                revalidated_net_total += opt_resp.optimized_offer.final_total
            else:
                revalidated_net_total += unit_p * qty

        # Stale pricing check (difference > 0.01)
        if abs(revalidated_net_total - plan.total_amount) > Decimal("0.0100"):
            logger.warning(
                "Plan %s snapshot pricing differs from revalidated pricing. Marking REPLAN_REQUIRED",  # noqa: E501
                plan.id,
            )
            return PurchaseRequestResponse(
                request_id=uuid.uuid4(),
                tenant_id=tenant_id,
                agent_id=agent_id,
                purchase_plan_id=plan.id,
                status="REPLAN_REQUIRED",
                requires_approval=False,
                total_amount=plan.total_amount,
                currency_code=plan.currency_code,
                created_at=plan.created_at or datetime.now(UTC),
            )

        # 3. Approval integration check
        requires_approval = plan.total_amount >= _APPROVAL_THRESHOLD_AMOUNT
        final_status = "PENDING_APPROVAL" if requires_approval else "READY_FOR_EXECUTION"

        # 4. Create and persist pre-execution PurchaseIntent ORM entity
        intent = PurchaseIntent(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            merchant_id=plan.merchant_id,
            agent_id=agent_id,
            product_id=plan.product_id,
            intent_reference=ref_key,
            status="pending" if requires_approval else "approved",
            quantity=plan.quantity,
            unit_price=plan.unit_price,
            total_amount=plan.total_amount,
            currency_code=plan.currency_code,
            intent_metadata={
                "purchase_plan_id": str(plan.id),
                "requires_approval": requires_approval,
                "status_code": final_status,
            },
        )
        db.add(intent)
        db.commit()

        return PurchaseRequestResponse(
            request_id=intent.id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            purchase_plan_id=plan.id,
            status=final_status,
            requires_approval=requires_approval,
            total_amount=plan.total_amount,
            currency_code=plan.currency_code,
            created_at=intent.created_at or datetime.now(UTC),
        )

    async def get_purchase_request(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        request_id: uuid.UUID,
    ) -> PurchaseRequestResponse:
        """Lookup purchase request (intent) by request_id within tenant boundary (Phase 181)."""  # noqa: E501
        stmt = select(PurchaseIntent).where(
            PurchaseIntent.id == request_id,
            PurchaseIntent.tenant_id == tenant_id,
            PurchaseIntent.deleted_at.is_(None),
        )
        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res
        intent: PurchaseIntent | None = res.scalars().first()

        if not intent:
            raise ProductNotFoundError(f"Purchase request '{request_id}' not found.")

        meta = intent.intent_metadata or {}
        req_approval = meta.get("requires_approval", False)
        status_code = meta.get("status_code", "READY_FOR_EXECUTION")
        plan_id_str = meta.get("purchase_plan_id", str(uuid.uuid4()))

        return PurchaseRequestResponse(
            request_id=intent.id,
            tenant_id=intent.tenant_id,
            agent_id=intent.agent_id,
            purchase_plan_id=uuid.UUID(plan_id_str),
            status=status_code,
            requires_approval=req_approval,
            total_amount=intent.total_amount,
            currency_code=intent.currency_code,
            created_at=intent.created_at or datetime.now(UTC),
        )
