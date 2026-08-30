"""Inventory Check Application Service for AGENTPAY (Phase 176)."""

from __future__ import annotations

import inspect
import logging
import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import select

from app.domain.exceptions.agent_exceptions import (
    ProductNotFoundError,
    ProductValidationError,
)
from app.infrastructure.database.models.inventory import Inventory
from app.infrastructure.database.repositories.product_repository import ProductRepository
from app.schemas.inventory import InventoryCheckResult

logger = logging.getLogger("agentpay.inventory.check.service")


class InventoryCheckService:
    """Production service for read-only inventory availability check (Phase 176)."""

    def __init__(self, repository: ProductRepository | None = None) -> None:
        self.repository = repository or ProductRepository()

    async def check_inventory(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        product_id: uuid.UUID,
        requested_quantity: Decimal = Decimal("1.000"),
    ) -> InventoryCheckResult:
        """Perform read-only stock availability check for a product (Phase 176)."""
        if requested_quantity <= Decimal("0.000"):
            raise ProductValidationError("requested_quantity must be greater than zero.")

        # 1. Verify Product exists in tenant scope fail-closed
        product = await self.repository.get_by_id(db, tenant_id, product_id, include_deleted=False)
        if not product or product.status != "active":
            raise ProductNotFoundError(f"Product '{product_id}' not found or inactive.")

        # 2. Query Inventory ORM model for stock availability
        stmt = select(Inventory).where(
            Inventory.tenant_id == tenant_id,
            Inventory.product_id == product_id,
            Inventory.deleted_at.is_(None),
        )
        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res
        inv: Inventory | None = res.scalars().first()

        # 3. Determine status without fabricating stock values
        if not inv or inv.status != "active":
            return InventoryCheckResult(
                product_id=product_id,
                requested_quantity=requested_quantity,
                available_quantity=Decimal("0.000"),
                is_available=False,
                inventory_status="UNKNOWN",
            )

        avail_qty = inv.available_quantity
        if avail_qty >= requested_quantity:
            status_str = "AVAILABLE"
            is_avail = True
        elif avail_qty > Decimal("0.000"):
            status_str = "PARTIALLY_AVAILABLE"
            is_avail = False
        else:
            status_str = "UNAVAILABLE"
            is_avail = False

        return InventoryCheckResult(
            product_id=product_id,
            requested_quantity=requested_quantity,
            available_quantity=avail_qty,
            is_available=is_avail,
            inventory_status=status_str,
        )
