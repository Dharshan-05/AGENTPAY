"""Authoritative Commerce Validation Application Service for AGENTPAY (Phase 182)."""

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
from app.schemas.commerce_validation import (
    CommerceValidationError,
    CommerceValidationResult,
)
from app.schemas.inventory import InventoryValidationItem

logger = logging.getLogger("agentpay.commerce.validation.service")

_APPROVAL_THRESHOLD_AMOUNT = Decimal("500.0000")


class CommerceValidationService:
    """Authoritative validation service evaluating complete commerce transaction context (Phase 182)."""  # noqa: E501

    def __init__(
        self,
        repository: ProductRepository | None = None,
        inventory_service: InventoryValidationService | None = None,
        offer_opt_service: OfferOptimizationService | None = None,
        approval_service: HumanApprovalWorkflowService | None = None,
    ) -> None:
        self.repository = repository or ProductRepository()
        self.inventory_service = inventory_service or InventoryValidationService(self.repository)  # noqa: E501
        self.offer_opt_service = offer_opt_service or OfferOptimizationService(self.repository)
        self.approval_service = approval_service or HumanApprovalWorkflowService()

    async def validate_commerce_request(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        purchase_request_id: uuid.UUID,
    ) -> CommerceValidationResult:
        """Authoritatively validate complete purchase request context (Phase 182)."""
        now = datetime.now(UTC)
        errors: list[CommerceValidationError] = []
        warnings: list[str] = []

        # 1. Resolve PurchaseIntent (Purchase Request) in tenant boundary fail-closed
        i_stmt = select(PurchaseIntent).where(
            PurchaseIntent.id == purchase_request_id,
            PurchaseIntent.tenant_id == tenant_id,
            PurchaseIntent.deleted_at.is_(None),
        )
        i_res = db.execute(i_stmt)
        if inspect.isawaitable(i_res):
            i_res = await i_res
        intent: PurchaseIntent | None = i_res.scalars().first()

        if not intent:
            raise ProductNotFoundError(f"Purchase request '{purchase_request_id}' not found.")

        # 2. Resolve parent PurchasePlan
        meta = intent.intent_metadata or {}
        plan_id_str = meta.get("purchase_plan_id")
        plan_id = uuid.UUID(plan_id_str) if plan_id_str else intent.id

        p_stmt = select(PurchasePlan).where(
            PurchasePlan.id == plan_id,
            PurchasePlan.tenant_id == tenant_id,
            PurchasePlan.deleted_at.is_(None),
        )
        p_res = db.execute(p_stmt)
        if inspect.isawaitable(p_res):
            p_res = await p_res
        plan: PurchasePlan | None = p_res.scalars().first()

        if not plan:
            errors.append(
                CommerceValidationError(
                    code="PLAN_NOT_FOUND",
                    message=f"Parent purchase plan '{plan_id}' not found in tenant.",
                    field="purchase_plan_id",
                )
            )
            return CommerceValidationResult(
                valid=False,
                purchase_request_id=purchase_request_id,
                purchase_plan_id=plan_id,
                currency=intent.currency_code,
                subtotal=Decimal("0.0000"),
                discount_total=Decimal("0.0000"),
                total=intent.total_amount,
                requires_approval=False,
                validation_errors=errors,
                warnings=warnings,
                validated_at=now,
            )

        # 3. Validate request state
        if intent.status in ("rejected", "expired", "cancelled"):
            errors.append(
                CommerceValidationError(
                    code="INVALID_REQUEST_STATE",
                    message=f"Purchase request is in terminal state '{intent.status}'.",
                    field="status",
                )
            )

        # 4. Revalidate inventory stock
        plan_meta = plan.plan_metadata or {}
        snapshot_items = plan_meta.get("snapshot_items", [])
        inv_items = [
            InventoryValidationItem(
                product_id=uuid.UUID(raw["product_id"]),
                requested_quantity=Decimal(str(raw["quantity"])),
            )
            for raw in snapshot_items
        ]

        if inv_items:
            inv_resp = await self.inventory_service.validate_inventory(db, tenant_id, inv_items)  # noqa: E501
            if not inv_resp.all_valid:
                for r in inv_resp.results:
                    if not r.valid:
                        errors.append(
                            CommerceValidationError(
                                code=r.reason,
                                message=f"Product '{r.product_id}' stock check failed ({r.reason}).",  # noqa: E501
                                field="inventory",
                            )
                        )

        # 5. Revalidate offer & pricing snapshots (Stale Plan Detection)
        revalidated_net_total = Decimal("0.0000")
        for raw in snapshot_items:
            pid = uuid.UUID(raw["product_id"])
            qty = Decimal(str(raw["quantity"]))
            prod = await self.repository.get_by_id(db, tenant_id, pid, include_deleted=False)
            if not prod or prod.status != "active":
                errors.append(
                    CommerceValidationError(
                        code="PRODUCT_INACTIVE",
                        message=f"Product '{pid}' is no longer active.",
                        field="product_id",
                    )
                )
                continue

            opt_resp = await self.offer_opt_service.optimize_offer(db, tenant_id, pid, quantity=qty)  # noqa: E501
            if opt_resp.has_applicable_offer and opt_resp.optimized_offer:
                revalidated_net_total += opt_resp.optimized_offer.final_total
            else:
                revalidated_net_total += prod.price * qty

        if abs(revalidated_net_total - plan.total_amount) > Decimal("0.0100"):
            errors.append(
                CommerceValidationError(
                    code="PRICE_CHANGED",
                    message=f"Current product pricing ({revalidated_net_total}) differs from plan snapshot ({plan.total_amount}). Re-planning required.",  # noqa: E501
                    field="total_amount",
                )
            )

        # 6. Check human approval policy
        requires_approval = plan.total_amount >= _APPROVAL_THRESHOLD_AMOUNT
        if requires_approval:
            warnings.append("Transaction amount exceeds threshold; human approval required.")

        disc_tot = Decimal(plan_meta.get("discount_total", "0.0000"))

        return CommerceValidationResult(
            valid=len(errors) == 0,
            purchase_request_id=purchase_request_id,
            purchase_plan_id=plan.id,
            currency=plan.currency_code,
            subtotal=plan.subtotal,
            discount_total=disc_tot,
            total=plan.total_amount,
            requires_approval=requires_approval,
            validation_errors=errors,
            warnings=warnings,
            validated_at=now,
        )
