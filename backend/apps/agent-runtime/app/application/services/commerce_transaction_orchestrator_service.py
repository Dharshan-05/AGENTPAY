"""Commerce Transaction Orchestration Application Service for AGENTPAY (Phase 184)."""

from __future__ import annotations

import inspect
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select

from app.application.services.agent_execution_reliability_service import (
    AgentExecutionReliabilityService,
)
from app.application.services.agent_transaction_orchestrator_service import (
    AgentTransactionOrchestratorService,
)
from app.application.services.agentpay_tool_adapter import AgentPayToolAdapter
from app.application.services.commerce_validation_service import CommerceValidationService
from app.application.services.human_approval_workflow_service import HumanApprovalWorkflowService
from app.domain.exceptions.agent_exceptions import (
    ExecutionValidationError,
    ProductNotFoundError,
)
from app.infrastructure.database.models.purchase_intent import PurchaseIntent
from app.schemas.agentpay_integration import AgentPayTransactionRequest
from app.schemas.commerce_transaction_orchestration import (
    CommerceExecutionRequest,
    CommerceExecutionResponse,
)
from app.schemas.human_approval import ApprovalRequestCreate

logger = logging.getLogger("agentpay.commerce.orchestrator.service")


class CommerceTransactionOrchestratorService:
    """Production orchestrator executing validated purchase requests via AgentPay core (Phase 184)."""  # noqa: E501

    def __init__(
        self,
        validation_service: CommerceValidationService | None = None,
        agentpay_adapter: AgentPayToolAdapter | None = None,
        approval_service: HumanApprovalWorkflowService | None = None,
        reliability_service: AgentExecutionReliabilityService | None = None,
        base_orchestrator: AgentTransactionOrchestratorService | None = None,
    ) -> None:
        self.validation_service = validation_service or CommerceValidationService()
        self.agentpay_adapter = agentpay_adapter or AgentPayToolAdapter()
        self.approval_service = approval_service or HumanApprovalWorkflowService()
        self.reliability_service = reliability_service or AgentExecutionReliabilityService()
        self.base_orchestrator = base_orchestrator or AgentTransactionOrchestratorService()

    async def execute_commerce_transaction(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        request: CommerceExecutionRequest,
        *,
        user_id: uuid.UUID | None = None,
    ) -> CommerceExecutionResponse:
        """Orchestrate a validated purchase request into deterministic transaction execution (Phase 184)."""  # noqa: E501
        now = datetime.now(UTC)
        req_id = request.purchase_request_id

        # 1. Run authoritative CommerceValidationService
        val_res = await self.validation_service.validate_commerce_request(db, tenant_id, req_id)
        if not val_res.valid:
            logger.warning(
                "Commerce validation failed for request %s (%s errors)",
                req_id,
                len(val_res.validation_errors),
            )
            return CommerceExecutionResponse(
                execution_id=uuid.uuid4(),
                tenant_id=tenant_id,
                purchase_request_id=req_id,
                status="FAILED",
                requires_approval=False,
                approval_id=None,
                total_amount=val_res.total,
                currency_code=val_res.currency,
                executed_at=now,
            )

        # 2. Fetch target PurchaseIntent ORM entity
        stmt = select(PurchaseIntent).where(
            PurchaseIntent.id == req_id,
            PurchaseIntent.tenant_id == tenant_id,
            PurchaseIntent.deleted_at.is_(None),
        )
        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res
        intent: PurchaseIntent | None = res.scalars().first()

        if not intent:
            raise ProductNotFoundError(f"Purchase request '{req_id}' not found.")

        # 3. Idempotency replay check
        meta = intent.intent_metadata or {}
        if meta.get("execution_status") == "COMPLETED":
            return CommerceExecutionResponse(
                execution_id=uuid.UUID(meta.get("execution_id", str(uuid.uuid4()))),
                tenant_id=tenant_id,
                purchase_request_id=req_id,
                status="COMPLETED",
                requires_approval=False,
                approval_id=(uuid.UUID(meta["approval_id"]) if meta.get("approval_id") else None),
                total_amount=intent.total_amount,
                currency_code=intent.currency_code,
                executed_at=intent.updated_at or now,
            )

        # 4. Human Approval Workflow Evaluation
        if val_res.requires_approval:
            appr_req = ApprovalRequestCreate(
                action_name="commerce_purchase_execution",
                amount=float(intent.total_amount),
                currency=intent.currency_code,
                reason=f"Purchase request '{req_id}' total {intent.total_amount} {intent.currency_code} requires approval.",  # noqa: E501
                context_data={"purchase_request_id": str(req_id)},
            )
            appr_res = await self.approval_service.create_approval_request(
                db,
                tenant_id=tenant_id,
                agent_id=intent.agent_id,
                request=appr_req,
                requesting_user_id=user_id,
            )

            intent.status = "pending"
            intent.intent_metadata = {
                **meta,
                "execution_status": "PENDING_APPROVAL",
                "approval_id": str(appr_res.approval_id),
            }
            db.commit()

            return CommerceExecutionResponse(
                execution_id=uuid.uuid4(),
                tenant_id=tenant_id,
                purchase_request_id=req_id,
                status="PENDING_APPROVAL",
                requires_approval=True,
                approval_id=appr_res.approval_id,
                total_amount=intent.total_amount,
                currency_code=intent.currency_code,
                executed_at=now,
            )

        # 5. Financial Transaction Initiation via AgentPayToolAdapter
        exec_id = uuid.uuid4()
        idem_key = (
            f"exec_{request.idempotency_key.strip()}"
            if request.idempotency_key and request.idempotency_key.strip()
            else f"exec_{uuid.uuid4().hex[:16]}"
        )

        pay_req = AgentPayTransactionRequest(
            amount=float(intent.total_amount),
            currency=intent.currency_code,
            recipient=f"Merchant-{intent.merchant_id}",
            description=f"Commerce purchase transaction execution for request {req_id}",
            idempotency_key=idem_key,
            metadata={"purchase_request_id": str(req_id)},
        )
        await self.agentpay_adapter.initiate_payment(
            db, tenant_id, intent.agent_id, pay_req, user_id=user_id
        )

        # 6. Mark Intent status as COMPLETED
        intent.status = "approved"
        intent.intent_metadata = {
            **meta,
            "execution_status": "COMPLETED",
            "execution_id": str(exec_id),
        }
        db.commit()

        return CommerceExecutionResponse(
            execution_id=exec_id,
            tenant_id=tenant_id,
            purchase_request_id=req_id,
            status="COMPLETED",
            requires_approval=False,
            approval_id=None,
            total_amount=intent.total_amount,
            currency_code=intent.currency_code,
            executed_at=now,
        )

    async def cancel_commerce_transaction(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        purchase_request_id: uuid.UUID,
    ) -> CommerceExecutionResponse:
        """Cancel a pending purchase request, preventing cancellation of completed transactions (Phase 184)."""  # noqa: E501
        now = datetime.now(UTC)
        stmt = select(PurchaseIntent).where(
            PurchaseIntent.id == purchase_request_id,
            PurchaseIntent.tenant_id == tenant_id,
            PurchaseIntent.deleted_at.is_(None),
        )
        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res
        intent: PurchaseIntent | None = res.scalars().first()

        if not intent:
            raise ProductNotFoundError(f"Purchase request '{purchase_request_id}' not found.")

        meta = intent.intent_metadata or {}
        if meta.get("execution_status") == "COMPLETED" or intent.status == "approved":
            raise ExecutionValidationError(
                "Cannot cancel a purchase transaction that has already reached COMPLETED state."
            )

        intent.status = "cancelled"
        intent.intent_metadata = {**meta, "execution_status": "CANCELLED"}
        db.commit()

        return CommerceExecutionResponse(
            execution_id=uuid.uuid4(),
            tenant_id=tenant_id,
            purchase_request_id=purchase_request_id,
            status="CANCELLED",
            requires_approval=False,
            approval_id=None,
            total_amount=intent.total_amount,
            currency_code=intent.currency_code,
            executed_at=now,
        )
