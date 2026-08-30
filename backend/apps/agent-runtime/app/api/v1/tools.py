"""Tool Registry REST controller router for AGENTPAY (Phase 157-159)."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.api.dependencies.authorization import require_permission
from app.application.services.tool_audit_service import ToolAuditService
from app.application.services.tool_authorization_service import ToolAuthorizationService
from app.application.services.tool_registry_service import ToolRegistryService
from app.domain.authorization.permissions_registry import (
    TOOLS_DISABLE,
    TOOLS_ENABLE,
    TOOLS_READ,
    TOOLS_REGISTER,
    TOOLS_UPDATE,
)
from app.domain.exceptions.agent_exceptions import (
    ExecutionNotFoundError,
    ToolAlreadyExistsError,
    ToolNotFoundError,
    ToolValidationError,
)
from app.infrastructure.database.session import get_db_session
from app.schemas.tool_audit import ToolAuditListResponse, ToolAuditResponse
from app.schemas.tool_authorization import (
    ToolAuthorizationContext,
    ToolAuthorizationRequest,
    ToolAuthorizationResponse,
)
from app.schemas.tool_registry import (
    ToolListResponse,
    ToolRegisterRequest,
    ToolResponse,
    ToolUpdateRequest,
)

logger = logging.getLogger("agentpay.api.tools")

tools_router = APIRouter(prefix="/tools", tags=["Tool Registry & Execution"])


def get_tool_registry_service() -> ToolRegistryService:
    """Dependency factory for ToolRegistryService."""
    return ToolRegistryService()


def get_tool_auth_service() -> ToolAuthorizationService:
    """Dependency factory for ToolAuthorizationService."""
    return ToolAuthorizationService()


def get_tool_audit_service() -> ToolAuditService:
    """Dependency factory for ToolAuditService."""
    return ToolAuditService()


@tools_router.post(
    "",
    response_model=ToolResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New Tool",
    description="Register a new agent tool definition in the Tool Registry (Phase 157).",
    operation_id="register_tool",
    dependencies=[Depends(require_permission(TOOLS_REGISTER))],
)
async def register_tool(
    request: ToolRegisterRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[ToolRegistryService, Depends(get_tool_registry_service)],
) -> ToolResponse:
    """Register a tool definition with tenant isolation."""
    try:
        return await service.register_tool(
            db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.user.id,
            request=request,
        )
    except ToolAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ToolValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@tools_router.get(
    "",
    response_model=ToolListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Registered Tools",
    description="Discover tools based on filter criteria with tenant isolation (Phase 157).",
    operation_id="list_tools",
    dependencies=[Depends(require_permission(TOOLS_READ))],
)
async def list_tools(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[ToolRegistryService, Depends(get_tool_registry_service)],
    category: str | None = Query(default=None, description="Filter by category"),
    status_filter: str | None = Query(default=None, alias="status", description="Filter by status"),
    environment: str | None = Query(default=None, description="Filter by environment"),
    risk_classification: str | None = Query(
        default=None, description="Filter by risk classification"
    ),
) -> ToolListResponse:
    """List registered tools for the tenant."""
    return await service.list_tools(
        db,
        tenant_id=current_user.tenant_id,
        category=category,
        status=status_filter,
        environment=environment,
        risk_classification=risk_classification,
    )


@tools_router.get(
    "/audit/logs",
    response_model=ToolAuditListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Tool Audit Logs",
    description="List tenant-isolated tool execution audit records (Phase 159).",
    operation_id="list_tool_audit_logs",
    dependencies=[Depends(require_permission(TOOLS_READ))],
)
async def list_tool_audit_logs(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    audit_service: Annotated[ToolAuditService, Depends(get_tool_audit_service)],
    agent_id: Annotated[uuid.UUID | None, Query(description="Filter by agent UUID")] = None,
    tool_id: Annotated[str | None, Query(description="Filter by tool ID")] = None,
    execution_state: Annotated[str | None, Query(description="Filter by execution state")] = None,
    cursor_created_at: Annotated[
        datetime | None, Query(description="Keyset cursor datetime")
    ] = None,  # noqa: E501
    cursor_id: Annotated[uuid.UUID | None, Query(description="Keyset cursor UUID")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Page limit")] = 20,
) -> ToolAuditListResponse:
    """List tool execution audit records for tenant."""
    return await audit_service.list_tool_execution_audits(
        db,
        tenant_id=current_user.tenant_id,
        agent_id=agent_id,
        tool_id=tool_id,
        execution_state=execution_state,
        cursor_created_at=cursor_created_at,
        cursor_id=cursor_id,
        limit=limit,
    )


@tools_router.get(
    "/audit/logs/{execution_id}",
    response_model=ToolAuditResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Tool Audit Detail",
    description="Lookup single tool execution audit details by execution_id (Phase 159).",
    operation_id="get_tool_audit_detail",
    dependencies=[Depends(require_permission(TOOLS_READ))],
)
async def get_tool_audit_detail(
    execution_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    audit_service: Annotated[ToolAuditService, Depends(get_tool_audit_service)],
) -> ToolAuditResponse:
    """Lookup tool execution audit detail."""
    try:
        return await audit_service.get_tool_execution_audit(
            db, tenant_id=current_user.tenant_id, execution_id=execution_id
        )
    except ExecutionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@tools_router.get(
    "/{tool_id}",
    response_model=ToolResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Tool Definition",
    description="Lookup a specific tool definition by tool_id and optional version (Phase 157).",
    operation_id="get_tool",
    dependencies=[Depends(require_permission(TOOLS_READ))],
)
async def get_tool(
    tool_id: str,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[ToolRegistryService, Depends(get_tool_registry_service)],
    version: str | None = Query(default=None, description="Optional tool version"),
) -> ToolResponse:
    """Lookup tool definition by tool_id."""
    try:
        return await service.get_tool(
            db, tenant_id=current_user.tenant_id, tool_id=tool_id, version=version
        )
    except ToolNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@tools_router.post(
    "/{tool_id}/authorize",
    response_model=ToolAuthorizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Authorize Tool Execution",
    description="Pre-evaluate tool authorization decision (ALLOW, DENY, REQUIRE_APPROVAL) (Phase 158).",  # noqa: E501
    operation_id="authorize_tool_execution",
    dependencies=[Depends(require_permission(TOOLS_READ))],
)
async def authorize_tool_execution(
    tool_id: str,
    request: ToolAuthorizationRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    registry_service: Annotated[ToolRegistryService, Depends(get_tool_registry_service)],
    auth_service: Annotated[ToolAuthorizationService, Depends(get_tool_auth_service)],
) -> ToolAuthorizationResponse:
    """Pre-evaluate permission decision for tool execution."""
    try:
        tool = await registry_service.get_tool(
            db, tenant_id=current_user.tenant_id, tool_id=tool_id, version=request.tool_version
        )
        ctx = ToolAuthorizationContext(
            tenant_id=current_user.tenant_id,
            agent_id=request.agent_id,
            user_id=current_user.user.id,
            tool_id=tool_id,
            tool_version=request.tool_version or tool.version,
            risk_classification=tool.risk_classification,
            environment=request.environment or tool.environment,
            amount=request.amount,
            currency=request.currency,
            action_name=tool_id,
            correlation_id=request.correlation_id,
        )
        return await auth_service.evaluate_authorization(db, ctx, tool=tool)
    except ToolNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@tools_router.patch(
    "/{tool_id}",
    response_model=ToolResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Tool Definition",
    description="Update a tool definition in the Tool Registry (Phase 157).",
    operation_id="update_tool",
    dependencies=[Depends(require_permission(TOOLS_UPDATE))],
)
async def update_tool(
    tool_id: str,
    request: ToolUpdateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[ToolRegistryService, Depends(get_tool_registry_service)],
    version: str | None = Query(default=None, description="Optional tool version"),
) -> ToolResponse:
    """Update tool definition details."""
    try:
        return await service.update_tool(
            db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.user.id,
            tool_id=tool_id,
            request=request,
            version=version,
        )
    except ToolNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@tools_router.post(
    "/{tool_id}/enable",
    response_model=ToolResponse,
    status_code=status.HTTP_200_OK,
    summary="Enable Tool",
    description="Enable a tool definition for agent execution (Phase 157).",
    operation_id="enable_tool",
    dependencies=[Depends(require_permission(TOOLS_ENABLE))],
)
async def enable_tool(
    tool_id: str,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[ToolRegistryService, Depends(get_tool_registry_service)],
    version: str | None = Query(default=None, description="Optional tool version"),
) -> ToolResponse:
    """Enable a tool for execution."""
    try:
        return await service.enable_tool(
            db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.user.id,
            tool_id=tool_id,
            version=version,
        )
    except ToolNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@tools_router.post(
    "/{tool_id}/disable",
    response_model=ToolResponse,
    status_code=status.HTTP_200_OK,
    summary="Disable Tool",
    description="Disable a tool, blocking execution requests (Phase 157).",
    operation_id="disable_tool",
    dependencies=[Depends(require_permission(TOOLS_DISABLE))],
)
async def disable_tool(
    tool_id: str,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[ToolRegistryService, Depends(get_tool_registry_service)],
    version: str | None = Query(default=None, description="Optional tool version"),
) -> ToolResponse:
    """Disable a tool."""
    try:
        return await service.disable_tool(
            db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.user.id,
            tool_id=tool_id,
            version=version,
        )
    except ToolNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
