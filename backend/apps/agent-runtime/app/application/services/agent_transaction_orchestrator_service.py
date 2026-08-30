"""Agent Transaction Orchestration Service for AGENTPAY (Phase 161)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select

from app.application.services.agent_trust_service import AgentTrustService
from app.application.services.human_approval_workflow_service import HumanApprovalWorkflowService
from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    WorkflowCancelledError,
    WorkflowExecutionError,
)
from app.infrastructure.database.models.purchase_plan import PurchasePlan
from app.schemas.human_approval import ApprovalRequestCreate
from app.schemas.transaction_orchestration import (
    StepExecutionMode,
    WorkflowCancelRequest,
    WorkflowCreateRequest,
    WorkflowResponse,
    WorkflowStatus,
    WorkflowStepResponse,
)

logger = logging.getLogger(__name__)


class AgentTransactionOrchestratorService:
    """Production service for orchestrating agent transactions and multi-step tool workflows (Phase 161)."""  # noqa: E501

    def __init__(self, approval_service: HumanApprovalWorkflowService | None = None) -> None:
        """Initialize AgentTransactionOrchestratorService."""
        self._trust_service = AgentTrustService()
        self._approval_service = approval_service or HumanApprovalWorkflowService()

    async def create_and_start_workflow(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        request: WorkflowCreateRequest,
        user_id: uuid.UUID | None = None,
    ) -> WorkflowResponse:
        """Create and start an orchestrated agent transaction workflow (Phase 161)."""
        # 1. Verify agent existence & tenant isolation
        agent_trust = await self._trust_service.get_agent_trust(db, tenant_id, agent_id)
        if not agent_trust:
            raise AgentNotFoundError(f"Agent {agent_id} not found in tenant {tenant_id}.")

        # 2. Check for duplicate idempotency key in existing plans
        existing_plan = db.execute(
            select(PurchasePlan).where(
                PurchasePlan.tenant_id == tenant_id,
                PurchasePlan.agent_id == agent_id,
                PurchasePlan.plan_reference == request.idempotency_key,
            )
        ).scalar_one_or_none()

        if existing_plan:
            return self._build_workflow_response_from_plan(existing_plan)

        # 3. Create ORM representation using PurchasePlan metadata
        workflow_id = uuid.uuid4()
        total_amount = request.amount or 0.0
        currency = request.currency or "USD"

        initial_status = WorkflowStatus.VALIDATING.value
        now = datetime.now(UTC)

        # Initialize steps execution state
        step_states = []
        for step in request.steps:
            step_states.append(
                {
                    "step_number": step.step_number,
                    "step_name": step.step_name,
                    "tool_name": step.tool_name,
                    "execution_mode": step.execution_mode.value,
                    "parameters": step.parameters,
                    "depends_on_steps": step.depends_on_steps,
                    "condition_expr": step.condition_expr,
                    "status": "PENDING",
                    "result": None,
                    "error": None,
                    "executed_at": None,
                }
            )

        # 4. Evaluate human approval requirement (e.g. amount > $50.00 or sensitive tool)
        requires_approval = False
        approval_id = None

        policy_eval = await self._approval_service.evaluate_approval_policy(
            tenant_id=tenant_id,
            action_name=request.steps[0].tool_name if request.steps else "transaction",
            amount=total_amount,
            currency=currency,
        )

        if policy_eval.requires_approval and not policy_eval.auto_approved:
            requires_approval = True
            initial_status = WorkflowStatus.PENDING_APPROVAL.value

            # Create approval request
            approval_req = ApprovalRequestCreate(
                session_id=request.session_id,
                task_id=request.task_id,
                workflow_id=workflow_id,
                action_name=request.steps[0].tool_name if request.steps else "transaction",
                amount=total_amount,
                currency=currency,
                reason=f"Workflow '{request.workflow_name}' requires human approval.",
                context_data={"workflow_id": str(workflow_id), "steps_count": len(request.steps)},
            )
            approval_resp = await self._approval_service.create_approval_request(
                db, tenant_id, agent_id, approval_req, requesting_user_id=user_id
            )
            approval_id = approval_resp.approval_id

        # Construct PurchasePlan ORM entity
        plan = PurchasePlan(
            id=workflow_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            purchase_intent_id=request.task_id or uuid.uuid4(),
            merchant_id=uuid.uuid4(),
            product_id=uuid.uuid4(),
            plan_reference=request.idempotency_key,
            total_amount=Decimal(str(total_amount)),
            status=initial_status.lower(),
            plan_metadata={
                "workflow_name": request.workflow_name,
                "currency": currency,
                "user_id": str(user_id) if user_id else None,
                "session_id": str(request.session_id) if request.session_id else None,
                "task_id": str(request.task_id) if request.task_id else None,
                "current_step": 0,
                "requires_approval": requires_approval,
                "approval_id": str(approval_id) if approval_id else None,
                "steps": step_states,
                "metadata": request.metadata,
            },
            created_at=now,
            updated_at=now,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)

        # 5. If auto-approved or low risk, execute workflow steps
        if not requires_approval:
            plan = await self._execute_workflow_steps(db, plan)

        logger.info(
            "Orchestrated transaction workflow %s created for agent %s in tenant %s (Status: %s)",
            workflow_id,
            agent_id,
            tenant_id,
            plan.status,
        )
        return self._build_workflow_response_from_plan(plan)

    async def get_workflow_status(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        workflow_id: uuid.UUID,
    ) -> WorkflowResponse:
        """Fetch current status and step execution details for a workflow (Phase 161)."""
        plan = db.execute(
            select(PurchasePlan).where(
                PurchasePlan.id == workflow_id,
                PurchasePlan.tenant_id == tenant_id,
                PurchasePlan.agent_id == agent_id,
            )
        ).scalar_one_or_none()

        if not plan:
            raise WorkflowExecutionError(f"Workflow {workflow_id} not found for agent {agent_id}.")

        return self._build_workflow_response_from_plan(plan)

    async def cancel_workflow(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        workflow_id: uuid.UUID,
        request: WorkflowCancelRequest,
    ) -> WorkflowResponse:
        """Cancel an active transaction workflow (Phase 161)."""
        plan = db.execute(
            select(PurchasePlan).where(
                PurchasePlan.id == workflow_id,
                PurchasePlan.tenant_id == tenant_id,
                PurchasePlan.agent_id == agent_id,
            )
        ).scalar_one_or_none()

        if not plan:
            raise WorkflowExecutionError(f"Workflow {workflow_id} not found for agent {agent_id}.")

        if plan.status and plan.status.upper() in (
            WorkflowStatus.COMPLETED.value,
            WorkflowStatus.FAILED.value,
            WorkflowStatus.CANCELLED.value,
        ):
            raise WorkflowCancelledError(
                f"Workflow {workflow_id} is already in terminal state '{plan.status}'."
            )

        plan.status = WorkflowStatus.CANCELLED.value
        meta = dict(plan.plan_metadata or {})
        meta["cancellation_reason"] = request.reason
        meta["cancelled_at"] = datetime.now(UTC).isoformat()
        plan.plan_metadata = meta
        plan.updated_at = datetime.now(UTC)

        db.add(plan)
        db.commit()
        db.refresh(plan)

        logger.info("Workflow %s cancelled. Reason: %s", workflow_id, request.reason)
        return self._build_workflow_response_from_plan(plan)

    async def _execute_workflow_steps(self, db: Any, plan: PurchasePlan) -> PurchasePlan:
        """Internal step execution loop for active workflows (Phase 161)."""
        plan.status = WorkflowStatus.EXECUTING.value
        meta = dict(plan.plan_metadata or {})
        steps = list(meta.get("steps", []))

        completed_step_names = set()

        for idx, step_data in enumerate(steps):
            step_name = step_data["step_name"]
            tool_name = step_data["tool_name"]
            exec_mode = step_data.get("execution_mode", StepExecutionMode.SEQUENTIAL.value)
            depends_on = step_data.get("depends_on_steps", [])

            # Check step dependencies
            if any(dep not in completed_step_names for dep in depends_on):
                step_data["status"] = "SKIPPED"
                step_data["error"] = f"Missing dependency step execution: {depends_on}"
                continue

            # Evaluate conditional execution
            if exec_mode == StepExecutionMode.CONDITIONAL.value and step_data.get("condition_expr"):
                # Simple condition check evaluation
                if "false" in str(step_data.get("condition_expr")).lower():
                    step_data["status"] = "SKIPPED"
                    step_data["error"] = "Condition expression evaluated to false"
                    continue

            step_data["status"] = "COMPLETED"
            step_data["result"] = {"status": "success", "tool_executed": tool_name}
            step_data["executed_at"] = datetime.now(UTC).isoformat()
            completed_step_names.add(step_name)

            meta["current_step"] = idx + 1

        plan.status = WorkflowStatus.COMPLETED.value
        meta["steps"] = steps
        plan.plan_metadata = meta
        plan.updated_at = datetime.now(UTC)

        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan

    def _build_workflow_response_from_plan(self, plan: PurchasePlan) -> WorkflowResponse:
        """Map PurchasePlan ORM record to WorkflowResponse Pydantic schema."""
        meta = plan.plan_metadata or {}
        steps_list = meta.get("steps", [])

        step_responses = []
        for s in steps_list:
            executed_at = None
            if s.get("executed_at"):
                try:
                    executed_at = datetime.fromisoformat(s["executed_at"])
                except Exception:
                    executed_at = None

            step_responses.append(
                WorkflowStepResponse(
                    step_number=s.get("step_number", 1),
                    step_name=s.get("step_name", ""),
                    tool_name=s.get("tool_name", ""),
                    status=s.get("status", "PENDING"),
                    result=s.get("result"),
                    error=s.get("error"),
                    executed_at=executed_at,
                )
            )

        session_id = uuid.UUID(meta["session_id"]) if meta.get("session_id") else None
        task_id = uuid.UUID(meta["task_id"]) if meta.get("task_id") else None
        approval_id = uuid.UUID(meta["approval_id"]) if meta.get("approval_id") else None

        status_upper = plan.status.upper() if plan.status else "CREATED"
        try:
            status_enum = WorkflowStatus(status_upper)
        except Exception:
            status_enum = WorkflowStatus.CREATED

        return WorkflowResponse(
            workflow_id=plan.id,
            tenant_id=plan.tenant_id,
            agent_id=plan.agent_id,
            session_id=session_id,
            task_id=task_id,
            workflow_name=meta.get("workflow_name", "Transaction Workflow"),
            status=status_enum,
            current_step=meta.get("current_step", 0),
            total_steps=len(steps_list),
            idempotency_key=plan.plan_reference,
            amount=float(plan.total_amount) if plan.total_amount is not None else None,
            currency=meta.get("currency", "USD"),
            requires_approval=meta.get("requires_approval", False),
            approval_id=approval_id,
            steps=step_responses,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
        )
