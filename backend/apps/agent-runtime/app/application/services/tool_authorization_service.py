"""Tool Permission System Service for AGENTPAY (Phase 158)."""

from __future__ import annotations

import inspect
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from app.application.services.authorization import AuthorizationService
from app.application.services.human_approval_workflow_service import HumanApprovalWorkflowService
from app.domain.authorization.permissions_registry import TOOLS_EXECUTE
from app.schemas.tool_authorization import (
    ToolAuthorizationContext,
    ToolAuthorizationDecisionEnum,
    ToolAuthorizationResponse,
)
from app.schemas.tool_registry import ToolRiskClassification, ToolStatus

logger = logging.getLogger("agentpay.tool.authorization.service")


class ToolAuthorizationService:
    """Production service for mandatory, policy-driven tool authorization (Phase 158)."""

    def __init__(
        self,
        rbac_service: AuthorizationService | None = None,
        approval_service: HumanApprovalWorkflowService | None = None,
    ) -> None:
        self.rbac_service = rbac_service or AuthorizationService()
        self.approval_service = approval_service or HumanApprovalWorkflowService()

    async def evaluate_authorization(
        self,
        db: Any,
        context: ToolAuthorizationContext,
        tool: Any | None = None,
    ) -> ToolAuthorizationResponse:
        """Evaluate deterministic authorization decision (ALLOW, DENY, REQUIRE_APPROVAL) fail-closed (Phase 158)."""  # noqa: E501
        eval_id = uuid.uuid4()
        now = datetime.now(UTC)

        # -------------------------------------------------------------------
        # 1. FAIL-CLOSED CHECK FOR MISSING CONTEXT OR TOOL STATUS
        # -------------------------------------------------------------------
        if not context.tenant_id or not context.agent_id or not context.tool_id:
            return ToolAuthorizationResponse(
                evaluation_id=eval_id,
                decision=ToolAuthorizationDecisionEnum.DENY,
                tenant_id=context.tenant_id or uuid.UUID(int=0),
                agent_id=context.agent_id or uuid.UUID(int=0),
                tool_id=context.tool_id or "unknown",
                tool_version=context.tool_version,
                reason="Fail-closed: Missing mandatory tenant, agent, or tool context.",
                requires_approval=False,
                matched_permissions=[],
                evaluated_at=now,
            )

        if tool and getattr(tool, "status", None) not in (
            ToolStatus.ENABLED,
            ToolStatus.REGISTERED,
        ):  # noqa: E501
            return ToolAuthorizationResponse(
                evaluation_id=eval_id,
                decision=ToolAuthorizationDecisionEnum.DENY,
                tenant_id=context.tenant_id,
                agent_id=context.agent_id,
                tool_id=context.tool_id,
                tool_version=context.tool_version,
                reason=f"Fail-closed: Tool '{context.tool_id}' is disabled or unapproved.",
                requires_approval=False,
                matched_permissions=[],
                evaluated_at=now,
            )

        # -------------------------------------------------------------------
        # 2. RESOLVE AGENT RBAC PERMISSIONS
        # -------------------------------------------------------------------
        matched_perms: list[str] = []
        try:
            agent_perms_res = self.rbac_service.resolve_agent_permissions(
                db, context.tenant_id, context.agent_id
            )
            if inspect.isawaitable(agent_perms_res):
                agent_perms = await agent_perms_res
            else:
                agent_perms = agent_perms_res
            matched_perms = list(agent_perms)
        except Exception as exc:
            logger.warning("Error resolving agent permissions for %s: %s", context.agent_id, exc)

        # Check explicit TOOLS_EXECUTE permission
        if TOOLS_EXECUTE not in matched_perms:
            return ToolAuthorizationResponse(
                evaluation_id=eval_id,
                decision=ToolAuthorizationDecisionEnum.DENY,
                tenant_id=context.tenant_id,
                agent_id=context.agent_id,
                tool_id=context.tool_id,
                tool_version=context.tool_version,
                reason=f"Agent '{context.agent_id}' lacks mandatory '{TOOLS_EXECUTE}' permission.",
                requires_approval=False,
                matched_permissions=matched_perms,
                evaluated_at=now,
            )

        # -------------------------------------------------------------------
        # 3. HIGH RISK & HUMAN APPROVAL POLICY CHECK (PHASE 162 INTEGRATION)
        # -------------------------------------------------------------------
        tool_risk = context.risk_classification
        if tool:
            try:
                tool_risk = ToolRiskClassification(getattr(tool, "risk_classification", "LOW"))
            except Exception:
                pass

        amount = context.amount or 0.0
        policy_eval = await self.approval_service.evaluate_approval_policy(
            tenant_id=context.tenant_id,
            action_name=context.action_name or context.tool_id,
            amount=amount,
            currency=context.currency,
        )

        is_high_risk_tool = tool_risk in (
            ToolRiskClassification.HIGH,
            ToolRiskClassification.CRITICAL,
        )

        if is_high_risk_tool or policy_eval.requires_approval:
            return ToolAuthorizationResponse(
                evaluation_id=eval_id,
                decision=ToolAuthorizationDecisionEnum.REQUIRE_APPROVAL,
                tenant_id=context.tenant_id,
                agent_id=context.agent_id,
                tool_id=context.tool_id,
                tool_version=context.tool_version,
                reason=(
                    f"Tool execution for '{context.tool_id}' requires human approval due to "
                    f"risk classification ({tool_risk.value}) or financial policy limits."
                ),
                requires_approval=True,
                approval_policy_name=policy_eval.matched_policy_name,
                matched_permissions=matched_perms,
                evaluated_at=now,
            )

        # -------------------------------------------------------------------
        # 4. ALLOW DECISION
        # -------------------------------------------------------------------
        return ToolAuthorizationResponse(
            evaluation_id=eval_id,
            decision=ToolAuthorizationDecisionEnum.ALLOW,
            tenant_id=context.tenant_id,
            agent_id=context.agent_id,
            tool_id=context.tool_id,
            tool_version=context.tool_version,
            reason=f"Tool execution for '{context.tool_id}' authorized cleanly under policy.",
            requires_approval=False,
            approval_policy_name=None,
            matched_permissions=matched_perms,
            evaluated_at=now,
        )
