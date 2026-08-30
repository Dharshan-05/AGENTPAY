"""Tool Execution Application Service for AGENTPAY (Phase 156–160)."""

from __future__ import annotations

import logging
import time
import uuid
from datetime import UTC, datetime
from typing import Any

from app.application.services.agent_audit_service import AgentAuditService
from app.application.services.agent_execution_reliability_service import (
    AgentExecutionReliabilityService,
)
from app.application.services.agentpay_tool_adapter import AgentPayToolAdapter
from app.application.services.tool_audit_service import ToolAuditService
from app.application.services.tool_authorization_service import ToolAuthorizationService
from app.application.services.tool_registry_service import ToolRegistryService
from app.domain.exceptions.agent_exceptions import (
    ToolDisabledError,
    ToolNotFoundError,
    ToolPermissionDeniedError,
    ToolValidationError,
)
from app.schemas.agentpay_integration import AgentPayTransactionRequest
from app.schemas.tool_authorization import (
    ToolAuthorizationContext,
    ToolAuthorizationDecisionEnum,
)
from app.schemas.tool_calling import (
    ToolCallRequest,
    ToolCallResponse,
    ToolExecutionState,
    ToolResult,
)
from app.schemas.tool_registry import ToolRiskClassification, ToolStatus

logger = logging.getLogger("agentpay.tool.execution.service")


class ToolExecutionService:
    """Production service orchestrating agent tool call executions (Phase 156–160)."""

    def __init__(
        self,
        registry_service: ToolRegistryService | None = None,
        reliability_service: AgentExecutionReliabilityService | None = None,
        audit_service: AgentAuditService | None = None,
        auth_service: ToolAuthorizationService | None = None,
        tool_audit_service: ToolAuditService | None = None,
        agentpay_adapter: AgentPayToolAdapter | None = None,
    ) -> None:
        self.registry_service = registry_service or ToolRegistryService()
        self.reliability_service = reliability_service or AgentExecutionReliabilityService()
        self.audit_service = audit_service or AgentAuditService()
        self.auth_service = auth_service or ToolAuthorizationService()
        self.tool_audit_service = tool_audit_service or ToolAuditService()
        self.agentpay_adapter = agentpay_adapter or AgentPayToolAdapter(
            reliability_service=self.reliability_service
        )

    async def execute_tool(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        request: ToolCallRequest,
        user_id: uuid.UUID | None = None,
    ) -> ToolCallResponse:
        """Execute a tool request with deterministic lifecycle states, Phase 158 auth, Phase 159 audit, and Phase 160 AgentPay (Phase 156-160)."""  # noqa: E501
        request_id = uuid.uuid4()
        start_time = time.perf_counter()
        correlation_id = request.correlation_id or f"CORR-{uuid.uuid4().hex[:8]}"

        # -------------------------------------------------------------------
        # 1. RESOLVE TOOL FROM REGISTRY
        # -------------------------------------------------------------------
        tool = await self.registry_service.get_tool(
            db, tenant_id, request.tool_id, version=request.tool_version
        )
        if not tool:
            raise ToolNotFoundError(f"Tool {request.tool_id} not found.")

        # -------------------------------------------------------------------
        # 2. STATUS & LIFECYCLE GATE
        # -------------------------------------------------------------------
        if tool.status not in (ToolStatus.ENABLED, ToolStatus.REGISTERED):
            raise ToolDisabledError(
                f"Tool '{request.tool_id}' is currently {tool.status.value} and cannot be executed."
            )

        # -------------------------------------------------------------------
        # 3. INPUT SCHEMA ARGUMENT VALIDATION
        # -------------------------------------------------------------------
        self._validate_arguments(tool.input_schema, request.arguments)

        # -------------------------------------------------------------------
        # 4. PERMISSION GATE (PHASE 158 ENFORCEMENT)
        # -------------------------------------------------------------------
        auth_decision = await self._enforce_permission_gate(
            db, tenant_id, agent_id, tool, request, user_id
        )

        # -------------------------------------------------------------------
        # 5. FINANCIAL SAFETY CHECK (PHASE 160 EXTENSION POINT)
        # -------------------------------------------------------------------
        if tool.risk_classification in (
            ToolRiskClassification.HIGH,
            ToolRiskClassification.CRITICAL,
        ):
            if not request.idempotency_key:
                raise ToolValidationError(
                    f"Financial/high-risk tool '{request.tool_id}' requires an explicit idempotency_key."  # noqa: E501
                )

        # -------------------------------------------------------------------
        # 6. TOOL EXECUTION IMPLEMENTATION
        # -------------------------------------------------------------------
        try:
            result_data = await self._run_tool_implementation(
                db, tenant_id, agent_id, tool, request.arguments, request, user_id
            )
            duration_ms = (time.perf_counter() - start_time) * 1000.0

            approval_st = "NOT_REQUIRED"
            if auth_decision.decision == ToolAuthorizationDecisionEnum.REQUIRE_APPROVAL:
                approval_st = "PENDING_APPROVAL"
                if isinstance(result_data, dict) and result_data.get("requires_approval"):
                    approval_st = "PENDING_APPROVAL"

            # ---------------------------------------------------------------
            # 7. AUDIT TELEMETRY LAYER (PHASE 159 PERSISTENCE)
            # ---------------------------------------------------------------
            await self.tool_audit_service.record_tool_execution_audit(
                db,
                tenant_id=tenant_id,
                agent_id=agent_id,
                user_id=user_id,
                execution_id=request_id,
                request_id=str(request_id),
                correlation_id=correlation_id,
                tool_id=tool.tool_id,
                tool_version=tool.version,
                permission_decision=auth_decision.decision.value,
                approval_state=approval_st,
                execution_state=ToolExecutionState.SUCCEEDED.value,
                risk_classification=tool.risk_classification.value,
                duration_ms=round(duration_ms, 2),
                environment=request.context.environment or tool.environment,
                payload_metadata={
                    "arguments": request.arguments,
                    "result": result_data,
                    "idempotency_key": request.idempotency_key,
                },
            )

            await self.audit_service.record_audit_event(
                db,
                tenant_id=tenant_id,
                agent_id=agent_id,
                actor_id=user_id or agent_id,
                event_type="tool_executed",
                event_action="execute_tool",
                event_result="success",
                event_metadata={
                    "request_id": str(request_id),
                    "tool_id": tool.tool_id,
                    "tool_version": tool.version,
                    "duration_ms": duration_ms,
                    "correlation_id": correlation_id,
                },
            )

            return ToolCallResponse(
                request_id=request_id,
                tool_id=tool.tool_id,
                tool_version=tool.version,
                agent_id=agent_id,
                tenant_id=tenant_id,
                state=ToolExecutionState.SUCCEEDED,
                result=ToolResult(status="success", data=result_data),
                error=None,
                correlation_id=correlation_id,
                idempotency_key=request.idempotency_key,
                duration_ms=round(duration_ms, 2),
                executed_at=datetime.now(UTC),
            )

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error("Tool execution failed for %s: %s", tool.tool_id, exc)

            await self.tool_audit_service.record_tool_execution_audit(
                db,
                tenant_id=tenant_id,
                agent_id=agent_id,
                user_id=user_id,
                execution_id=request_id,
                request_id=str(request_id),
                correlation_id=correlation_id,
                tool_id=tool.tool_id,
                tool_version=tool.version,
                permission_decision=auth_decision.decision.value,
                approval_state="FAILED",
                execution_state=ToolExecutionState.FAILED.value,
                risk_classification=tool.risk_classification.value,
                duration_ms=round(duration_ms, 2),
                error_code=str(type(exc).__name__),
                environment=request.context.environment or tool.environment,
                payload_metadata={
                    "arguments": request.arguments,
                    "error": str(exc),
                },
            )

            await self.audit_service.record_audit_event(
                db,
                tenant_id=tenant_id,
                agent_id=agent_id,
                actor_id=user_id or agent_id,
                event_type="tool_execution_failed",
                event_action="execute_tool",
                event_result="failure",
                event_metadata={
                    "request_id": str(request_id),
                    "tool_id": tool.tool_id,
                    "error": str(exc),
                },
            )

            return ToolCallResponse(
                request_id=request_id,
                tool_id=tool.tool_id,
                tool_version=tool.version,
                agent_id=agent_id,
                tenant_id=tenant_id,
                state=ToolExecutionState.FAILED,
                result=None,
                error=str(exc),
                correlation_id=correlation_id,
                idempotency_key=request.idempotency_key,
                duration_ms=round(duration_ms, 2),
                executed_at=datetime.now(UTC),
            )

    def _validate_arguments(self, input_schema: dict[str, Any], arguments: dict[str, Any]) -> None:
        """Validate execution arguments against tool JSON schema (Phase 156)."""
        if not input_schema:
            return

        required_fields = input_schema.get("required", [])
        for req_field in required_fields:
            if req_field not in arguments:
                raise ToolValidationError(f"Missing required tool argument: '{req_field}'")

        properties = input_schema.get("properties", {})
        for key, val in arguments.items():
            if key in properties:
                expected_type = properties[key].get("type")
                if expected_type == "string" and not isinstance(val, str):
                    raise ToolValidationError(
                        f"Argument '{key}' expected type 'string', got '{type(val).__name__}'."
                    )
                elif expected_type == "number" and not isinstance(val, (int, float)):
                    raise ToolValidationError(
                        f"Argument '{key}' expected type 'number', got '{type(val).__name__}'."
                    )
                elif expected_type == "boolean" and not isinstance(val, bool):
                    raise ToolValidationError(
                        f"Argument '{key}' expected type 'boolean', got '{type(val).__name__}'."
                    )

    async def _enforce_permission_gate(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        tool: Any,
        request: ToolCallRequest,
        user_id: uuid.UUID | None,
    ) -> Any:
        """Mandatory policy-driven tool permission evaluation gate (Phase 158)."""
        amount_val = request.arguments.get("amount")
        amount_float: float | None = (
            float(amount_val) if isinstance(amount_val, (int, float)) else None
        )  # noqa: E501

        auth_ctx = ToolAuthorizationContext(
            tenant_id=tenant_id,
            agent_id=agent_id,
            user_id=user_id,
            tool_id=tool.tool_id,
            tool_version=tool.version,
            risk_classification=tool.risk_classification,
            environment=tool.environment,
            amount=amount_float,
            currency=str(request.arguments.get("currency", "USD")),
            action_name=tool.tool_id,
            correlation_id=request.correlation_id,
        )

        decision_res = await self.auth_service.evaluate_authorization(db, auth_ctx, tool=tool)

        if decision_res.decision == ToolAuthorizationDecisionEnum.DENY:
            raise ToolPermissionDeniedError(decision_res.reason)

        return decision_res

    async def _run_tool_implementation(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        tool: Any,
        arguments: dict[str, Any],
        request: ToolCallRequest,
        user_id: uuid.UUID | None,
    ) -> dict[str, Any]:
        """Internal tool execution runner with Phase 160 AgentPay core integration."""
        is_financial_tool = (
            tool.category == "finance"
            or "payment" in tool.tool_id
            or tool.tool_id in ("payment_initiation", "payment_create", "transfer", "payout")
        )

        if is_financial_tool:
            amount = float(arguments.get("amount", 10.0))
            currency = str(arguments.get("currency", "USD"))
            recipient = str(
                arguments.get("recipient", arguments.get("merchant", "Default Merchant"))
            )  # noqa: E501
            description = str(arguments.get("description", f"Payment to {recipient}"))
            idempotency_key = request.idempotency_key or f"IDEM-{uuid.uuid4().hex[:12]}"

            pay_req = AgentPayTransactionRequest(
                amount=amount,
                currency=currency,
                recipient=recipient,
                description=description,
                idempotency_key=idempotency_key,
                correlation_id=request.correlation_id,
                metadata=arguments,
            )

            pay_res = await self.agentpay_adapter.initiate_payment(
                db, tenant_id, agent_id, pay_req, user_id=user_id
            )

            return {
                "transaction_id": str(pay_res.transaction_id),
                "reference_code": pay_res.reference_code,
                "status": pay_res.status,
                "amount": pay_res.amount,
                "currency": pay_res.currency,
                "recipient": pay_res.recipient,
                "requires_approval": pay_res.requires_approval,
                "approval_request_id": str(pay_res.approval_request_id)
                if pay_res.approval_request_id
                else None,  # noqa: E501
                "idempotency_key": pay_res.idempotency_key,
                "retry_safety": pay_res.retry_safety,
            }

        return {
            "tool_id": tool.tool_id,
            "version": tool.version,
            "executed_arguments": arguments,
            "status": "executed",
        }
