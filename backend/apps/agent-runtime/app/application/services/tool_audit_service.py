"""Tool Execution Audit Service for AGENTPAY (Phase 159)."""

from __future__ import annotations

import inspect
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, or_, select

from app.domain.exceptions.agent_exceptions import ExecutionNotFoundError
from app.infrastructure.database.models.tool_execution_audit import ToolExecutionAudit
from app.schemas.tool_audit import ToolAuditListResponse, ToolAuditResponse

logger = logging.getLogger("agentpay.tool.audit.service")

_LIMIT_DEFAULT = 20
_LIMIT_MAX = 100

SENSITIVE_TOOL_AUDIT_KEYS: frozenset[str] = frozenset(
    {
        "password",
        "raw_secret",
        "secret",
        "secret_hash",
        "access_token",
        "refresh_token",
        "jwt",
        "private_key",
        "authorization",
        "api_key",
        "card_number",
        "cvv",
        "client_secret",
    }
)


def _sanitize_tool_metadata(data: dict[str, Any] | None) -> dict[str, Any]:
    """Recursively redact secrets and sanitize sensitive keys from tool execution metadata."""
    if not data:
        return {}
    clean: dict[str, Any] = {}
    for k, v in data.items():
        if k.lower() in SENSITIVE_TOOL_AUDIT_KEYS:
            clean[k] = "[REDACTED]"
        elif isinstance(v, dict):
            clean[k] = _sanitize_tool_metadata(v)
        elif isinstance(v, list):
            clean[k] = [
                _sanitize_tool_metadata(item) if isinstance(item, dict) else item for item in v
            ]
        else:
            clean[k] = v
    return clean


class ToolAuditService:
    """Production service managing immutable append-only tool execution telemetry logs (Phase 159)."""  # noqa: E501

    async def record_tool_execution_audit(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        tool_id: str,
        execution_state: str,
        *,
        user_id: uuid.UUID | None = None,
        execution_id: uuid.UUID | None = None,
        request_id: str | None = None,
        correlation_id: str | None = None,
        tool_version: str = "1.0.0",
        permission_decision: str = "ALLOW",
        approval_state: str = "NOT_REQUIRED",
        risk_classification: str = "LOW",
        duration_ms: float = 0.0,
        error_code: str | None = None,
        environment: str = "production",
        payload_metadata: dict[str, Any] | None = None,
    ) -> ToolAuditResponse:
        """Create and persist an immutable append-only `ToolExecutionAudit` record (Phase 159)."""
        exec_uuid = execution_id or uuid.uuid4()
        clean_meta = _sanitize_tool_metadata(payload_metadata)
        now = datetime.now(UTC)

        audit_entry = ToolExecutionAudit(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            user_id=user_id,
            execution_id=exec_uuid,
            request_id=request_id,
            correlation_id=correlation_id,
            tool_id=tool_id,
            tool_version=tool_version,
            permission_decision=permission_decision,
            approval_state=approval_state,
            execution_state=execution_state,
            risk_classification=risk_classification,
            duration_ms=duration_ms,
            error_code=error_code,
            environment=environment,
            payload_metadata=clean_meta,
            created_at=now,
        )

        db.add(audit_entry)
        if hasattr(db.commit, "__await__"):
            await db.commit()
            await db.refresh(audit_entry)
        else:
            db.commit()

        logger.info(
            "Recorded tool execution audit entry: %s (tool: %s, state: %s)",
            exec_uuid,
            tool_id,
            execution_state,
        )

        return self._to_response(audit_entry)

    async def get_tool_execution_audit(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        execution_id: uuid.UUID,
    ) -> ToolAuditResponse:
        """Lookup a single tool execution audit record by execution_id within tenant scope."""
        query = select(ToolExecutionAudit).where(
            ToolExecutionAudit.tenant_id == tenant_id,
            or_(
                ToolExecutionAudit.execution_id == execution_id,
                ToolExecutionAudit.id == execution_id,
            ),
        )
        res = await self._exec(db, query)
        audit = res.scalars().first()
        if not audit:
            raise ExecutionNotFoundError(f"Tool execution audit record '{execution_id}' not found.")

        return self._to_response(audit)

    async def list_tool_execution_audits(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID | None = None,
        tool_id: str | None = None,
        execution_state: str | None = None,
        cursor_created_at: datetime | None = None,
        cursor_id: uuid.UUID | None = None,
        limit: int = _LIMIT_DEFAULT,
    ) -> ToolAuditListResponse:
        """List tenant-scoped tool execution audit records using keyset pagination."""
        fetch_limit = min(max(1, limit), _LIMIT_MAX) + 1

        query = select(ToolExecutionAudit).where(ToolExecutionAudit.tenant_id == tenant_id)

        if agent_id:
            query = query.where(ToolExecutionAudit.agent_id == agent_id)
        if tool_id:
            query = query.where(ToolExecutionAudit.tool_id == tool_id)
        if execution_state:
            query = query.where(ToolExecutionAudit.execution_state == execution_state)

        if cursor_created_at and cursor_id:
            query = query.where(
                or_(
                    ToolExecutionAudit.created_at < cursor_created_at,
                    and_(
                        ToolExecutionAudit.created_at == cursor_created_at,
                        ToolExecutionAudit.id < cursor_id,
                    ),
                )
            )

        query = query.order_by(
            ToolExecutionAudit.created_at.desc(), ToolExecutionAudit.id.desc()
        ).limit(fetch_limit)

        res = await self._exec(db, query)
        audits = res.scalars().all()

        has_more = len(audits) > limit
        if has_more:
            audits = audits[:limit]

        responses = [self._to_response(a) for a in audits]

        return ToolAuditListResponse(
            tenant_id=tenant_id,
            total_count=len(responses),
            has_more=has_more,
            audits=responses,
        )

    async def _exec(self, db: Any, stmt: Any) -> Any:
        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res
        return res

    def _to_response(self, audit: ToolExecutionAudit) -> ToolAuditResponse:
        """Map ORM entity to ToolAuditResponse schema."""
        return ToolAuditResponse(
            id=audit.id,
            tenant_id=audit.tenant_id,
            agent_id=audit.agent_id,
            user_id=audit.user_id,
            execution_id=audit.execution_id,
            request_id=audit.request_id,
            correlation_id=audit.correlation_id,
            tool_id=audit.tool_id,
            tool_version=audit.tool_version,
            permission_decision=audit.permission_decision,
            approval_state=audit.approval_state,
            execution_state=audit.execution_state,
            risk_classification=audit.risk_classification,
            duration_ms=audit.duration_ms,
            error_code=audit.error_code,
            environment=audit.environment,
            payload_metadata=audit.payload_metadata or {},
            created_at=audit.created_at,
        )
