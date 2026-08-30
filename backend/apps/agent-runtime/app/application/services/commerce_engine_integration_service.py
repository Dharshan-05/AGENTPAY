"""Commerce Engine Core Integration Application Service for AGENTPAY (Phase 183)."""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from typing import Any

from app.application.services.agent_execution_reliability_service import (
    AgentExecutionReliabilityService,
)
from app.application.services.agentpay_tool_adapter import AgentPayToolAdapter
from app.application.services.commerce_validation_service import CommerceValidationService
from app.application.services.inventory_check_service import InventoryCheckService
from app.application.services.offer_service import OfferService
from app.application.services.product_search_service import ProductSearchService
from app.application.services.purchase_planning_service import PurchasePlanningService
from app.application.services.purchase_request_service import PurchaseRequestService
from app.domain.exceptions.agent_exceptions import (
    ExecutionValidationError,
)
from app.schemas.commerce_validation import CommerceValidationResult
from app.schemas.inventory import InventoryCheckResult
from app.schemas.offers import OfferListResponse
from app.schemas.product_search import ProductSearchResponse
from app.schemas.purchase_planning import (
    PurchasePlanCreateRequest,
    PurchasePlanResponse,
)
from app.schemas.purchase_request import (
    PurchaseRequestCreateRequest,
    PurchaseRequestResponse,
)

logger = logging.getLogger("agentpay.commerce.integration.service")


class CommerceEngineIntegrationService:
    """Production service integrating Commerce Engine with AgentPay core tool framework (Phase 183)."""  # noqa: E501

    def __init__(
        self,
        search_service: ProductSearchService | None = None,
        inventory_service: InventoryCheckService | None = None,
        offer_service: OfferService | None = None,
        planning_service: PurchasePlanningService | None = None,
        request_service: PurchaseRequestService | None = None,
        validation_service: CommerceValidationService | None = None,
        agentpay_adapter: AgentPayToolAdapter | None = None,
        reliability_service: AgentExecutionReliabilityService | None = None,
    ) -> None:
        self.search_service = search_service or ProductSearchService()
        self.inventory_service = inventory_service or InventoryCheckService()
        self.offer_service = offer_service or OfferService()
        self.planning_service = planning_service or PurchasePlanningService()
        self.request_service = request_service or PurchaseRequestService()
        self.validation_service = validation_service or CommerceValidationService()
        self.agentpay_adapter = agentpay_adapter or AgentPayToolAdapter()
        self.reliability_service = reliability_service or AgentExecutionReliabilityService()

    async def execute_commerce_operation(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        operation_name: str,
        payload: dict[str, Any],
        *,
        user_id: uuid.UUID | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Execute a tool-wrapped commerce engine operation through AgentPay core (Phase 183)."""
        op = operation_name.strip().lower()
        logger.info("Executing commerce operation '%s' for agent %s", op, agent_id)

        if op == "product_discovery":
            query = str(payload.get("query", "catalog"))
            res_search: ProductSearchResponse = await self.search_service.search_products(
                db, tenant_id, query, limit=int(payload.get("limit", 20))
            )
            return res_search.model_dump(mode="json")

        elif op == "inventory_check":
            pid = uuid.UUID(str(payload["product_id"]))
            qty = Decimal(str(payload.get("quantity", "1.000")))
            res_inv: InventoryCheckResult = await self.inventory_service.check_inventory(
                db, tenant_id, pid, requested_quantity=qty
            )
            return res_inv.model_dump(mode="json")

        elif op == "offer_discovery":
            pid = uuid.UUID(str(payload["product_id"]))
            qty = Decimal(str(payload.get("quantity", "1.000")))
            res_off: OfferListResponse = await self.offer_service.get_product_offers(
                db, tenant_id, pid, requested_quantity=qty
            )
            return res_off.model_dump(mode="json")

        elif op == "purchase_plan_create":
            req_plan = PurchasePlanCreateRequest.model_validate(payload)
            if idempotency_key and not req_plan.idempotency_key:
                req_plan.idempotency_key = idempotency_key
            res_plan: PurchasePlanResponse = await self.planning_service.create_purchase_plan(
                db, tenant_id, req_plan, default_agent_id=agent_id
            )
            return res_plan.model_dump(mode="json")

        elif op == "purchase_request_create":
            req_req = PurchaseRequestCreateRequest.model_validate(payload)
            if idempotency_key and not req_req.idempotency_key:
                req_req.idempotency_key = idempotency_key
            res_req: PurchaseRequestResponse = await self.request_service.create_purchase_request(
                db, tenant_id, req_req, default_agent_id=agent_id
            )
            return res_req.model_dump(mode="json")

        elif op == "purchase_request_validate":
            req_id = uuid.UUID(str(payload["purchase_request_id"]))
            res_val: CommerceValidationResult = (
                await self.validation_service.validate_commerce_request(db, tenant_id, req_id)
            )
            return res_val.model_dump(mode="json")

        else:
            raise ExecutionValidationError(f"Unsupported commerce operation '{operation_name}'.")
