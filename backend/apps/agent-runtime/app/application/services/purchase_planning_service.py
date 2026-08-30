"""Purchase Planning Application Service for AGENTPAY (Phase 180)."""

from __future__ import annotations

import inspect
import logging
import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import select

from app.application.services.inventory_validation_service import InventoryValidationService
from app.application.services.offer_optimization_service import OfferOptimizationService
from app.domain.exceptions.agent_exceptions import (
    ProductNotFoundError,
    ProductValidationError,
)
from app.infrastructure.database.models.purchase_intent import PurchaseIntent
from app.infrastructure.database.models.purchase_plan import PurchasePlan
from app.infrastructure.database.repositories.product_repository import ProductRepository
from app.schemas.inventory import InventoryValidationItem
from app.schemas.purchase_planning import (
    PurchasePlanCreateRequest,
    PurchasePlanItemResponse,
    PurchasePlanResponse,
)

logger = logging.getLogger("agentpay.purchase.planning.service")

_MAX_LINE_ITEMS = 50


class PurchasePlanningService:
    """Production service for purchase execution planning and snapshot persistence (Phase 180)."""  # noqa: E501

    def __init__(
        self,
        repository: ProductRepository | None = None,
        inventory_service: InventoryValidationService | None = None,
        offer_opt_service: OfferOptimizationService | None = None,
    ) -> None:
        self.repository = repository or ProductRepository()
        self.inventory_service = inventory_service or InventoryValidationService(self.repository)  # noqa: E501
        self.offer_opt_service = offer_opt_service or OfferOptimizationService(self.repository)

    async def create_purchase_plan(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        request: PurchasePlanCreateRequest,
        *,
        default_agent_id: uuid.UUID | None = None,
    ) -> PurchasePlanResponse:
        """Create a validated, idempotent purchase plan with financial pricing snapshots (Phase 180)."""  # noqa: E501
        if not request.items:
            raise ProductValidationError("Purchase plan must contain at least 1 item.")
        if len(request.items) > _MAX_LINE_ITEMS:
            raise ProductValidationError(
                f"Purchase plan exceeds maximum allowed size of {_MAX_LINE_ITEMS} items."
            )

        agent_id = request.agent_id or default_agent_id or uuid.uuid4()

        # Check for duplicate product IDs in request items
        seen_pids: set[uuid.UUID] = set()
        for it in request.items:
            if it.product_id in seen_pids:
                raise ProductValidationError(
                    f"Duplicate product_id '{it.product_id}' in purchase plan items."
                )
            seen_pids.add(it.product_id)

        # Idempotency replay check
        ref_key = (
            f"plan_{request.idempotency_key.strip()}"
            if request.idempotency_key and request.idempotency_key.strip()
            else f"plan_{uuid.uuid4().hex[:16]}"
        )

        existing_stmt = select(PurchasePlan).where(
            PurchasePlan.tenant_id == tenant_id,
            PurchasePlan.plan_reference == ref_key,
            PurchasePlan.deleted_at.is_(None),
        )
        e_res = db.execute(existing_stmt)
        if inspect.isawaitable(e_res):
            e_res = await e_res
        existing_plan: PurchasePlan | None = e_res.scalars().first()

        if existing_plan:
            return self._build_response_from_orm(existing_plan)

        # 1. Run advisory inventory validation
        inv_items = [
            InventoryValidationItem(product_id=it.product_id, requested_quantity=it.quantity)
            for it in request.items
        ]
        inv_resp = await self.inventory_service.validate_inventory(db, tenant_id, inv_items)
        if not inv_resp.all_valid:
            invalid_reasons = [
                f"{r.product_id}: {r.reason}" for r in inv_resp.results if not r.valid
            ]
            raise ProductValidationError(
                f"Inventory validation failed for plan items: {', '.join(invalid_reasons)}"
            )

        # 2. Process products and offer optimization
        item_responses: list[PurchasePlanItemResponse] = []
        gross_subtotal = Decimal("0.0000")
        total_discount = Decimal("0.0000")
        net_total = Decimal("0.0000")
        common_currency: str | None = None

        primary_merchant_id: uuid.UUID | None = None
        primary_product_id: uuid.UUID | None = None

        for it in request.items:
            prod = await self.repository.get_by_id(
                db, tenant_id, it.product_id, include_deleted=False
            )
            if not prod or prod.status != "active":
                raise ProductNotFoundError(f"Product '{it.product_id}' not found or inactive.")

            curr = getattr(prod, "currency_code", None) or "USD"
            if common_currency is None:
                common_currency = curr
            elif common_currency != curr:
                raise ProductValidationError(
                    f"Mixed currencies in purchase plan ({common_currency} vs {curr}). Multi-currency plans are not supported."  # noqa: E501
                )

            if primary_merchant_id is None:
                primary_merchant_id = prod.merchant_id
                primary_product_id = prod.id

            # Offer optimization
            opt_resp = await self.offer_opt_service.optimize_offer(
                db, tenant_id, it.product_id, quantity=it.quantity
            )

            unit_p = prod.price
            if opt_resp.has_applicable_offer and opt_resp.optimized_offer:
                off_item = opt_resp.optimized_offer
                sel_offer_id = off_item.offer_id
                disc_amt = off_item.discount_amount
                line_tot = off_item.final_total
            else:
                sel_offer_id = None
                disc_amt = Decimal("0.0000")
                line_tot = unit_p * it.quantity

            gross_subtotal += unit_p * it.quantity
            total_discount += disc_amt
            net_total += line_tot

            item_responses.append(
                PurchasePlanItemResponse(
                    product_id=prod.id,
                    merchant_id=prod.merchant_id,
                    sku=prod.sku,
                    name=prod.name,
                    unit_price=unit_p,
                    quantity=it.quantity,
                    selected_offer_id=sel_offer_id,
                    discount_amount=disc_amt,
                    line_total=line_tot,
                    currency_code=curr,
                )
            )

        # 3. Ensure backing PurchaseIntent exists (satisfy FK constraint fk_purchase_plans_purchase_intent_id)  # noqa: E501
        intent_ref = f"intent_{ref_key}"
        i_stmt = select(PurchaseIntent).where(
            PurchaseIntent.tenant_id == tenant_id,
            PurchaseIntent.intent_reference == intent_ref,
            PurchaseIntent.deleted_at.is_(None),
        )
        i_res = db.execute(i_stmt)
        if inspect.isawaitable(i_res):
            i_res = await i_res
        parent_intent: PurchaseIntent | None = i_res.scalars().first()

        if not parent_intent:
            parent_intent = PurchaseIntent(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                merchant_id=primary_merchant_id or uuid.uuid4(),
                agent_id=agent_id,
                product_id=primary_product_id or uuid.uuid4(),
                intent_reference=intent_ref,
                status="pending",
                quantity=request.items[0].quantity,
                unit_price=item_responses[0].unit_price,
                total_amount=net_total,
                currency_code=common_currency or "USD",
            )
            db.add(parent_intent)
            db.flush()

        # 4. Create and persist PurchasePlan ORM entity
        snapshot_items = [it_resp.model_dump(mode="json") for it_resp in item_responses]

        plan_entity = PurchasePlan(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            purchase_intent_id=parent_intent.id,
            merchant_id=primary_merchant_id or uuid.uuid4(),
            agent_id=agent_id,
            product_id=primary_product_id or uuid.uuid4(),
            offer_id=item_responses[0].selected_offer_id if item_responses else None,
            plan_reference=ref_key,
            status="validated",
            quantity=request.items[0].quantity,
            unit_price=item_responses[0].unit_price,
            subtotal=gross_subtotal,
            total_amount=net_total,
            currency_code=common_currency or "USD",
            plan_metadata={
                "snapshot_items": snapshot_items,
                "discount_total": str(total_discount),
            },
        )
        db.add(plan_entity)
        db.commit()

        return self._build_response_from_orm(plan_entity)

    async def get_purchase_plan(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        plan_id: uuid.UUID,
    ) -> PurchasePlanResponse:
        """Lookup purchase plan by plan_id within tenant boundary (Phase 180)."""
        stmt = select(PurchasePlan).where(
            PurchasePlan.id == plan_id,
            PurchasePlan.tenant_id == tenant_id,
            PurchasePlan.deleted_at.is_(None),
        )
        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res
        plan: PurchasePlan | None = res.scalars().first()

        if not plan:
            raise ProductNotFoundError(f"Purchase plan '{plan_id}' not found.")

        return self._build_response_from_orm(plan)

    def _build_response_from_orm(self, plan: PurchasePlan) -> PurchasePlanResponse:
        """Construct strongly typed PurchasePlanResponse from ORM model snapshot."""
        meta = plan.plan_metadata or {}
        raw_items = meta.get("snapshot_items", [])
        disc_tot = Decimal(meta.get("discount_total", "0.0000"))

        item_responses: list[PurchasePlanItemResponse] = []
        for raw in raw_items:
            item_responses.append(
                PurchasePlanItemResponse(
                    product_id=uuid.UUID(raw["product_id"]),
                    merchant_id=uuid.UUID(raw["merchant_id"]),
                    sku=raw["sku"],
                    name=raw["name"],
                    unit_price=Decimal(str(raw["unit_price"])),
                    quantity=Decimal(str(raw["quantity"])),
                    selected_offer_id=(
                        uuid.UUID(raw["selected_offer_id"])
                        if raw.get("selected_offer_id")
                        else None
                    ),
                    discount_amount=Decimal(str(raw["discount_amount"])),
                    line_total=Decimal(str(raw["line_total"])),
                    currency_code=raw["currency_code"],
                )
            )

        if not item_responses:
            item_responses = [
                PurchasePlanItemResponse(
                    product_id=plan.product_id,
                    merchant_id=plan.merchant_id,
                    sku="N/A",
                    name="Product Item",
                    unit_price=plan.unit_price,
                    quantity=plan.quantity,
                    selected_offer_id=plan.offer_id,
                    discount_amount=disc_tot,
                    line_total=plan.total_amount,
                    currency_code=plan.currency_code,
                )
            ]

        from datetime import UTC, datetime

        return PurchasePlanResponse(
            plan_id=plan.id,
            tenant_id=plan.tenant_id,
            agent_id=plan.agent_id,
            plan_reference=plan.plan_reference,
            status=plan.status,
            items=item_responses,
            subtotal=plan.subtotal,
            discount_total=disc_tot,
            total_amount=plan.total_amount,
            currency_code=plan.currency_code,
            planned_at=plan.planned_at or datetime.now(UTC),
        )
