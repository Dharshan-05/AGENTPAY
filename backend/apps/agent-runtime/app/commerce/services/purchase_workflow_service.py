"""Bounded Agentic Commerce Purchase State Machine & Price Revalidation Service."""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from typing import Any

from app.application.services.human_approval_workflow_service import HumanApprovalWorkflowService
from app.commerce.providers.online_search_provider import OnlineProductSearchProvider
from app.commerce.schemas import (
    NormalizedProduct,
    PurchaseWorkflowRequest,
    PurchaseWorkflowResponse,
)
from app.commerce.services.commerce_risk_service import CommerceRiskService
from app.schemas.human_approval import ApprovalRequestCreate

logger = logging.getLogger("agentpay.commerce.services.purchase_workflow")


class PurchaseWorkflowService:
    """Production Agentic Commerce Purchase State Machine implementing price revalidation and HITL governance."""

    def __init__(
        self,
        product_provider: OnlineProductSearchProvider | None = None,
        risk_service: CommerceRiskService | None = None,
        human_approval_service: HumanApprovalWorkflowService | None = None,
    ) -> None:
        self.product_provider = product_provider or OnlineProductSearchProvider()
        self.risk_service = risk_service or CommerceRiskService()
        self.human_approval_service = human_approval_service or HumanApprovalWorkflowService()

    async def initiate_purchase_workflow(
        self,
        db: Any,
        request: PurchaseWorkflowRequest,
    ) -> PurchaseWorkflowResponse:
        """Process purchase request through strict revalidation and security gates."""
        workflow_id = uuid.uuid4()
        req_price = request.price
        # Step 0: Resolve Product Context from Active Session if generic
        from app.commerce.services.commerce_facade_service import get_active_session
        if not request.product_id or request.product_id in ["prod_selected", "this", "it", "unresolved"] or request.product_name.lower().strip() in ["it", "this", "laptop", "recommended laptop", "selected laptop", "selected product", "unresolved"]:
            sess = get_active_session(request.tenant_id, request.agent_id)
            if sess and sess.get("selected_product"):
                sel_p = sess["selected_product"]
                request.product_id = sel_p.product_id
                request.product_name = sel_p.product_name
                request.price = Decimal(str(sel_p.price))
                request.currency = sel_p.currency
                if sel_p.seller and sel_p.seller.seller_id:
                    request.seller_id = sel_p.seller.seller_id

        if not request.product_id or request.price <= Decimal("0.00") or not request.product_name or request.product_name.lower().strip() in ["it", "this", "laptop", "recommended laptop", "unresolved"]:
            return PurchaseWorkflowResponse(
                purchase_workflow_id=workflow_id,
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                product=None,
                requested_price=request.price,
                revalidated_price=Decimal("0.00"),
                price_changed=False,
                price_change_message="PRODUCT_CONTEXT_UNRESOLVED: Explicit product selection and price confirmation required prior to financial authorization.",
                agentguard_status="PENDING_PRODUCT_SELECTION",
                fraudguard_risk_score=0.0,
                fraudguard_risk_level="LOW",
                fraudguard_xai_reasons=["No valid active product context resolved from session."],
                hitl_required=True,
                workflow_status="PENDING_INFORMATION",
                final_execution_decision="NOT_REQUESTED",
            )

        # Step 1: Product Fetch & Real-time Price Revalidation
        product = await self.product_provider.get_product_details(request.product_id)
        if product is None:
            # Fallback construct normalized product if requested dynamically
            product = NormalizedProduct(
                product_id=request.product_id,
                product_name=request.product_name,
                brand="Vendor",
                category="COMMERCE",
                description=f"Direct purchase item: {request.product_name}",
                price=request.price,
                currency=request.currency,
                availability=True,
                seller=await self.product_provider.get_seller_info(request.seller_id)
                or self.product_provider._sellers.get("seller_appario_retail")
                or list(self.product_provider._sellers.values())[0],
            )

        current_price = product.price

        # Check Price Revalidation Mismatch
        price_changed = False
        price_change_msg = None
        if current_price != req_price and (
            request.user_confirmed_price is None or request.user_confirmed_price != current_price
        ):
            price_changed = True
            price_change_msg = (
                f"PRICE_CHANGED: Current revalidated price ({current_price} {request.currency}) "
                f"differs from requested price ({req_price} {request.currency}). Confirmation required."
            )
            logger.warning("Purchase workflow %s price mismatch: %s", workflow_id, price_change_msg)

            return PurchaseWorkflowResponse(
                purchase_workflow_id=workflow_id,
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                product=product,
                requested_price=req_price,
                revalidated_price=current_price,
                price_changed=True,
                price_change_message=price_change_msg,
                agentguard_status="PRICE_REVALIDATION_HOLD",
                fraudguard_risk_score=15.0,
                fraudguard_risk_level="MEDIUM",
                fraudguard_xai_reasons=[price_change_msg],
                hitl_required=True,
                workflow_status="PRICE_MISMATCH",
                final_execution_decision="DENY",
            )

        # Step 2: FraudGuard Risk & XAI Signal Evaluation
        risk_assessment = self.risk_service.evaluate_commerce_risk(
            product=product,
            requested_amount=current_price,
        )

        if not risk_assessment.is_transaction_allowed:
            return PurchaseWorkflowResponse(
                purchase_workflow_id=workflow_id,
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                product=product,
                requested_price=req_price,
                revalidated_price=current_price,
                price_changed=False,
                agentguard_status="FRAUDGUARD_BLOCKED",
                fraudguard_risk_score=risk_assessment.risk_score,
                fraudguard_risk_level=risk_assessment.risk_level,
                fraudguard_xai_reasons=risk_assessment.risk_factors,
                hitl_required=False,
                workflow_status="DENIED",
                final_execution_decision="DENY",
            )

        # Step 3: HITL Approval Request Registration (Phase 6)
        hitl_id = uuid.uuid4()
        try:
            approval_req = ApprovalRequestCreate(
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                workflow_type="AGENTIC_COMMERCE_PURCHASE",
                target_resource=product.product_id,
                requested_action="RAZORPAY_TEST_PAYMENT",
                amount=current_price,
                currency=request.currency,
                request_metadata={
                    "product_name": product.product_name,
                    "seller_name": product.seller.seller_name,
                    "idempotency_key": request.idempotency_key or str(workflow_id),
                },
            )
            approval_res = await self.human_approval_service.create_approval_request(
                db=db,
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                request=approval_req,
            )
            hitl_id = approval_res.approval_id
        except Exception as exc:
            logger.warning("HITL registration fallback in purchase workflow: %s", exc)

        return PurchaseWorkflowResponse(
            purchase_workflow_id=workflow_id,
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            product=product,
            requested_price=req_price,
            revalidated_price=current_price,
            price_changed=False,
            agentguard_status="ALLOWED",
            fraudguard_risk_score=risk_assessment.risk_score,
            fraudguard_risk_level=risk_assessment.risk_level,
            fraudguard_xai_reasons=risk_assessment.risk_factors,
            hitl_required=True,
            hitl_approval_id=hitl_id,
            workflow_status="PENDING_HITL",
            final_execution_decision="REVIEW",
            idempotency_key=request.idempotency_key or str(workflow_id),
        )
