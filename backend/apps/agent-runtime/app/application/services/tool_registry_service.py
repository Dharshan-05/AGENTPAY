"""Tool Registry Service for AGENTPAY (Phase 157)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select

from app.application.services.agent_audit_service import AgentAuditService
from app.domain.exceptions.agent_exceptions import (
    ToolAlreadyExistsError,
    ToolNotFoundError,
    ToolValidationError,
)
from app.infrastructure.database.models.tool_definition import ToolDefinition
from app.schemas.tool_registry import (
    ToolListResponse,
    ToolRegisterRequest,
    ToolResponse,
    ToolRiskClassification,
    ToolStatus,
    ToolUpdateRequest,
)

logger = logging.getLogger("agentpay.tool.registry.service")


class ToolRegistryService:
    """Production application service managing agent tool definitions (Phase 157)."""

    def __init__(self, audit_service: AgentAuditService | None = None) -> None:
        self.audit_service = audit_service or AgentAuditService()

    async def register_tool(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        request: ToolRegisterRequest,
    ) -> ToolResponse:
        """Register a new tool in the central registry with tenant isolation (Phase 157)."""
        # Validate input schema structure
        if not isinstance(request.input_schema, dict):
            raise ToolValidationError("Tool input_schema must be a valid JSON object.")

        # Check for existing tool with same tenant, name, version
        stmt = select(ToolDefinition).where(
            ToolDefinition.tenant_id == tenant_id,
            ToolDefinition.name == request.name,
            ToolDefinition.version == request.version,
            ToolDefinition.deleted_at.is_(None),
        )
        res = db.execute(stmt)
        if res.scalar_one_or_none() is not None:
            raise ToolAlreadyExistsError(
                f"Tool '{request.name}' with version '{request.version}' already registered."
            )

        now = datetime.now(UTC)
        tool_obj = ToolDefinition(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            tool_id=request.tool_id,
            name=request.name,
            version=request.version,
            description=request.description,
            category=request.category,
            owner=request.owner or f"user:{user_id}",
            status=ToolStatus.REGISTERED.value,
            environment=request.environment,
            risk_classification=request.risk_classification.value,
            input_schema=request.input_schema,
            output_schema=request.output_schema or {},
            capabilities=request.capabilities,
            tool_metadata=request.metadata,
            created_at=now,
            updated_at=now,
        )

        db.add(tool_obj)

        await self.audit_service.record_audit_event(
            db,
            tenant_id=tenant_id,
            agent_id=user_id,
            actor_id=user_id,
            event_type="tool_registered",
            event_action="register_tool",
            event_result="success",
            event_metadata={
                "tool_id": request.tool_id,
                "name": request.name,
                "version": request.version,
            },
        )

        db.commit()
        db.refresh(tool_obj)
        logger.info(
            "Registered tool %s (v%s) for tenant %s", request.tool_id, request.version, tenant_id
        )
        return self._to_response(tool_obj)

    async def get_tool(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        tool_id: str,
        version: str | None = None,
    ) -> ToolResponse:
        """Lookup a registered tool definition by tool_id and optional version (Phase 157)."""
        query = select(ToolDefinition).where(
            ToolDefinition.tenant_id == tenant_id,
            ToolDefinition.tool_id == tool_id,
            ToolDefinition.deleted_at.is_(None),
        )
        if version:
            query = query.where(ToolDefinition.version == version)

        res = db.execute(query)
        tool = res.scalars().first()
        if not tool:
            raise ToolNotFoundError(f"Tool '{tool_id}' (version: {version or 'any'}) not found.")

        return self._to_response(tool)

    async def update_tool(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        tool_id: str,
        request: ToolUpdateRequest,
        version: str | None = None,
    ) -> ToolResponse:
        """Update a tool definition in the registry (Phase 157)."""
        query = select(ToolDefinition).where(
            ToolDefinition.tenant_id == tenant_id,
            ToolDefinition.tool_id == tool_id,
            ToolDefinition.deleted_at.is_(None),
        )
        if version:
            query = query.where(ToolDefinition.version == version)

        res = db.execute(query)
        tool = res.scalars().first()
        if not tool:
            raise ToolNotFoundError(f"Tool '{tool_id}' not found.")

        now = datetime.now(UTC)
        if request.description is not None:
            tool.description = request.description
        if request.category is not None:
            tool.category = request.category
        if request.owner is not None:
            tool.owner = request.owner
        if request.status is not None:
            tool.status = request.status.value
        if request.environment is not None:
            tool.environment = request.environment
        if request.risk_classification is not None:
            tool.risk_classification = request.risk_classification.value
        if request.input_schema is not None:
            tool.input_schema = request.input_schema
        if request.output_schema is not None:
            tool.output_schema = request.output_schema
        if request.capabilities is not None:
            tool.capabilities = request.capabilities
        if request.metadata is not None:
            tool.tool_metadata = request.metadata

        tool.updated_at = now
        db.add(tool)

        await self.audit_service.record_audit_event(
            db,
            tenant_id=tenant_id,
            agent_id=user_id,
            actor_id=user_id,
            event_type="tool_updated",
            event_action="update_tool",
            event_result="success",
            event_metadata={"tool_id": tool_id, "version": tool.version},
        )

        db.commit()
        db.refresh(tool)
        return self._to_response(tool)

    async def enable_tool(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        tool_id: str,
        version: str | None = None,
    ) -> ToolResponse:
        """Enable a registered tool for execution (Phase 157)."""
        req = ToolUpdateRequest(status=ToolStatus.ENABLED)
        return await self.update_tool(db, tenant_id, user_id, tool_id, req, version=version)

    async def disable_tool(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        tool_id: str,
        version: str | None = None,
    ) -> ToolResponse:
        """Disable a tool, preventing execution requests (Phase 157)."""
        req = ToolUpdateRequest(status=ToolStatus.DISABLED)
        return await self.update_tool(db, tenant_id, user_id, tool_id, req, version=version)

    async def list_tools(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        category: str | None = None,
        status: str | None = None,
        environment: str | None = None,
        risk_classification: str | None = None,
    ) -> ToolListResponse:
        """Discover tools based on filter criteria with strict tenant isolation (Phase 157)."""
        query = select(ToolDefinition).where(
            ToolDefinition.tenant_id == tenant_id,
            ToolDefinition.deleted_at.is_(None),
        )

        if category:
            query = query.where(ToolDefinition.category == category)
        if status:
            query = query.where(ToolDefinition.status == status)
        if environment:
            query = query.where(ToolDefinition.environment == environment)
        if risk_classification:
            query = query.where(ToolDefinition.risk_classification == risk_classification)

        res = db.execute(query)
        tools = res.scalars().all()
        responses = [self._to_response(t) for t in tools]

        return ToolListResponse(
            tenant_id=tenant_id,
            total_count=len(responses),
            tools=responses,
        )

    def _to_response(self, tool: ToolDefinition) -> ToolResponse:
        """Map ToolDefinition ORM entity to ToolResponse schema."""
        status_enum = ToolStatus.REGISTERED
        try:
            status_enum = ToolStatus(tool.status)
        except Exception:
            pass

        risk_enum = ToolRiskClassification.LOW
        try:
            risk_enum = ToolRiskClassification(tool.risk_classification)
        except Exception:
            pass

        return ToolResponse(
            id=tool.id,
            tenant_id=tool.tenant_id,
            tool_id=tool.tool_id,
            name=tool.name,
            version=tool.version,
            description=tool.description,
            category=tool.category,
            owner=tool.owner,
            status=status_enum,
            environment=tool.environment,
            risk_classification=risk_enum,
            input_schema=tool.input_schema or {},
            output_schema=tool.output_schema,
            capabilities=tool.capabilities or [],
            metadata=tool.tool_metadata or {},
            created_at=tool.created_at,
            updated_at=tool.updated_at,
        )
