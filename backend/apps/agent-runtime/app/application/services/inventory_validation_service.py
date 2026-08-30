"""Inventory Validation Application Service for AGENTPAY (Phase 177)."""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from typing import Any

from app.application.services.inventory_check_service import InventoryCheckService
from app.domain.exceptions.agent_exceptions import (
    ProductNotFoundError,
    ProductValidationError,
)
from app.infrastructure.database.repositories.product_repository import ProductRepository
from app.schemas.inventory import (
    InventoryValidationItem,
    InventoryValidationResponse,
    InventoryValidationResult,
)

logger = logging.getLogger("agentpay.inventory.validation.service")

_MAX_BULK_VALIDATION_ITEMS = 50


class InventoryValidationService:
    """Production service for read-only advisory inventory validation (Phase 177)."""

    def __init__(
        self,
        repository: ProductRepository | None = None,
        check_service: InventoryCheckService | None = None,
    ) -> None:
        self.repository = repository or ProductRepository()
        self.check_service = check_service or InventoryCheckService(self.repository)

    async def validate_inventory(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        items: list[InventoryValidationItem],
    ) -> InventoryValidationResponse:
        """Validate requested purchase quantities against inventory stock (read-only advisory) (Phase 177)."""  # noqa: E501
        if not items:
            raise ProductValidationError("Validation items list cannot be empty.")

        if len(items) > _MAX_BULK_VALIDATION_ITEMS:
            raise ProductValidationError(
                f"Bulk inventory validation exceeds maximum allowed size of {_MAX_BULK_VALIDATION_ITEMS} items."  # noqa: E501
            )

        results: list[InventoryValidationResult] = []
        all_valid = True

        for item in items:
            if item.requested_quantity <= Decimal("0.000"):
                all_valid = False
                results.append(
                    InventoryValidationResult(
                        valid=False,
                        product_id=item.product_id,
                        requested_quantity=item.requested_quantity,
                        available_quantity=Decimal("0.000"),
                        reason="INVALID_QUANTITY",
                    )
                )
                continue

            try:
                check_res = await self.check_service.check_inventory(
                    db,
                    tenant_id,
                    product_id=item.product_id,
                    requested_quantity=item.requested_quantity,
                )

                if check_res.inventory_status == "AVAILABLE":
                    results.append(
                        InventoryValidationResult(
                            valid=True,
                            product_id=item.product_id,
                            requested_quantity=item.requested_quantity,
                            available_quantity=check_res.available_quantity,
                            reason="VALID",
                        )
                    )
                elif check_res.inventory_status == "UNKNOWN":
                    all_valid = False
                    results.append(
                        InventoryValidationResult(
                            valid=False,
                            product_id=item.product_id,
                            requested_quantity=item.requested_quantity,
                            available_quantity=Decimal("0.000"),
                            reason="INVENTORY_UNKNOWN",
                        )
                    )
                else:
                    all_valid = False
                    results.append(
                        InventoryValidationResult(
                            valid=False,
                            product_id=item.product_id,
                            requested_quantity=item.requested_quantity,
                            available_quantity=check_res.available_quantity,
                            reason="INSUFFICIENT_STOCK",
                        )
                    )

            except ProductNotFoundError:
                all_valid = False
                results.append(
                    InventoryValidationResult(
                        valid=False,
                        product_id=item.product_id,
                        requested_quantity=item.requested_quantity,
                        available_quantity=Decimal("0.000"),
                        reason="PRODUCT_NOT_FOUND",
                    )
                )

        return InventoryValidationResponse(
            tenant_id=tenant_id,
            all_valid=all_valid,
            results=results,
        )
