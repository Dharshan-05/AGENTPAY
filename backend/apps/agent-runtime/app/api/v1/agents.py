"""AGENTPAY Agent Management REST API Controller (Phase 119–145).

Endpoints:
    GET    /api/v1/agents — List tenant agents
    POST   /api/v1/agents — Create new agent + identity
    GET    /api/v1/agents/{agent_id} — Get agent details
    GET    /api/v1/agents/{agent_id}/identity — Get agent identity
    POST   /api/v1/agents/{agent_id}/credentials — Issue credential
    GET    /api/v1/agents/{agent_id}/credentials — List credentials
    GET    /api/v1/agents/{agent_id}/credentials/{cred_id} — Get credential
    POST   /api/v1/agents/{agent_id}/activate — Activate agent (Phase 124)
    POST   /api/v1/agents/{agent_id}/suspend — Suspend agent (Phase 125)
    POST   /api/v1/agents/{agent_id}/revoke — Revoke agent (Phase 126)
    POST   /api/v1/agents/{agent_id}/sessions — Create session (Phase 127)
    GET    /api/v1/agents/{agent_id}/sessions — List sessions (Phase 127)
    GET    /api/v1/agents/{agent_id}/sessions/{session_id} — Get session (Phase 127)
    POST   /api/v1/agents/{agent_id}/sessions/{sess_id}/revoke — Revoke session (Phase 127)
    POST   /api/v1/agents/{agent_id}/sessions/revoke-all — Bulk revoke sessions (Phase 127)
    GET    /api/v1/agents/{agent_id}/permissions — List permissions (Phase 128)
    POST   /api/v1/agents/{agent_id}/permissions — Assign permission (Phase 128)
    DELETE /api/v1/agents/{agent_id}/permissions/{perm_id} — Revoke permission (Phase 128)
    GET    /api/v1/agents/{agent_id}/roles — List roles (Phase 129)
    POST   /api/v1/agents/{agent_id}/roles — Assign role (Phase 129)
    DELETE /api/v1/agents/{agent_id}/roles/{role_id} — Revoke role (Phase 129)
    GET    /api/v1/agents/{agent_id}/status — Get status (Phase 130)
    PATCH  /api/v1/agents/{agent_id}/status — Update status (Phase 130)
    POST   /api/v1/agents/{agent_id}/pause — Pause agent (Phase 130)
    POST   /api/v1/agents/{agent_id}/resume — Resume agent (Phase 130)
    GET    /api/v1/agents/{agent_id}/metadata — Get metadata (Phase 131)
    PATCH  /api/v1/agents/{agent_id}/metadata — Update metadata (Phase 131)
    GET    /api/v1/agents/{agent_id}/audit-events — List audit logs (Phase 132)
    GET    /api/v1/agents/{agent_id}/security-events — List security logs (Phase 133)
    GET    /api/v1/agents/{agent_id}/trust — Get trust posture (Phase 134)
    PATCH  /api/v1/agents/{agent_id}/trust — Update trust posture (Phase 134)
    GET    /api/v1/agents/{agent_id}/behaviour/deviation — Evaluate behaviour deviation (Phase 136)
    GET    /api/v1/agents/{agent_id}/velocity — Evaluate activity velocity (Phase 137)
    GET    /api/v1/agents/{agent_id}/merchant-behaviour — Analyze merchant interaction (Phase 138)
    GET    /api/v1/agents/{agent_id}/category-behaviour — Analyze category behaviour (Phase 139)
    POST   /api/v1/agents/{agent_id}/intent/extract — Extract & classify intent (Phase 140-142)
    POST   /api/v1/agents/{agent_id}/intent — Store intent (Phase 145)
    GET    /api/v1/agents/{agent_id}/intent/{intent_id} — Get stored intent (Phase 145)
    GET    /api/v1/agents/{agent_id}/intents — List stored intents (Phase 145)

Authorization & RBAC:
    - All routes enforced via require_permission(...) and tenant-scoped auth context
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.api.dependencies.authorization import require_permission
from app.application.services.agent_audit_service import AgentAuditService
from app.application.services.agent_authorization_service import (
    AgentAuthorizationService,
)
from app.application.services.agent_behaviour_deviation_service import (
    AgentBehaviourDeviationService,
)
from app.application.services.agent_category_behaviour_service import (
    AgentCategoryBehaviourService,
)
from app.application.services.agent_context_service import AgentContextService
from app.application.services.agent_credential_service import AgentCredentialService
from app.application.services.agent_execution_reliability_service import (
    AgentExecutionReliabilityService,
)
from app.application.services.agent_execution_service import AgentExecutionService
from app.application.services.agent_identity_verification_service import (
    AgentIdentityVerificationService,
)
from app.application.services.agent_lifecycle_service import AgentLifecycleService
from app.application.services.agent_memory_service import AgentMemoryService
from app.application.services.agent_merchant_behaviour_service import (
    AgentMerchantBehaviourService,
)
from app.application.services.agent_metadata_service import AgentMetadataService
from app.application.services.agent_orchestrator_service import AgentOrchestratorService
from app.application.services.agent_permission_evaluation_service import (
    AgentPermissionEvaluationService,
)
from app.application.services.agent_planning_service import AgentPlanningService
from app.application.services.agent_security_event_service import AgentSecurityEventService
from app.application.services.agent_service import AgentIdentityService, AgentService
from app.application.services.agent_session_service import AgentSessionService
from app.application.services.agent_state_service import AgentStateService
from app.application.services.agent_transaction_orchestrator_service import (
    AgentTransactionOrchestratorService,
)
from app.application.services.agent_trust_service import AgentTrustService
from app.application.services.agent_velocity_detection_service import (
    AgentVelocityDetectionService,
)
from app.application.services.authorization import AuthorizationService
from app.application.services.human_approval_workflow_service import (
    HumanApprovalWorkflowService,
)
from app.application.services.intent_classification_service import IntentClassificationService
from app.application.services.intent_extraction_service import IntentExtractionService
from app.application.services.intent_storage_service import IntentStorageService
from app.application.services.plan_generation_service import PlanGenerationService
from app.application.services.plan_validation_service import PlanValidationService
from app.application.services.policy_evaluation_service import PolicyEvaluationService
from app.application.services.short_term_memory_service import ShortTermMemoryService
from app.application.services.tool_execution_service import ToolExecutionService
from app.domain.authorization.permissions_registry import (
    AGENTS_ACTIVATE,
    AGENTS_APPROVAL_DECIDE,
    AGENTS_APPROVAL_REQUEST,
    AGENTS_AUDIT_READ,
    AGENTS_AUTHORIZATION_CHECK,
    AGENTS_BEHAVIOUR_READ,
    AGENTS_CATEGORY_BEHAVIOUR_READ,
    AGENTS_CONTEXT_ASSEMBLE,
    AGENTS_CREATE,
    AGENTS_CREDENTIAL_CREATE,
    AGENTS_CREDENTIAL_READ,
    AGENTS_EXECUTE,
    AGENTS_EXECUTION_CANCEL,
    AGENTS_EXECUTION_READ,
    AGENTS_IDENTITY_VERIFY,
    AGENTS_INTENT_CREATE,
    AGENTS_INTENT_READ,
    AGENTS_MEMORY_DELETE,
    AGENTS_MEMORY_READ,
    AGENTS_MEMORY_WRITE,
    AGENTS_MERCHANT_BEHAVIOUR_READ,
    AGENTS_METADATA_READ,
    AGENTS_METADATA_UPDATE,
    AGENTS_ORCHESTRATE,
    AGENTS_ORCHESTRATION_READ,
    AGENTS_PAUSE,
    AGENTS_PERMISSIONS_ASSIGN,
    AGENTS_PERMISSIONS_EVALUATE,
    AGENTS_PERMISSIONS_READ,
    AGENTS_PERMISSIONS_REVOKE,
    AGENTS_PLANS_CREATE,
    AGENTS_PLANS_READ,
    AGENTS_PLANS_VALIDATE,
    AGENTS_READ,
    AGENTS_RELIABILITY_RECOVER,
    AGENTS_RESUME,
    AGENTS_REVOKE,
    AGENTS_ROLES_ASSIGN,
    AGENTS_ROLES_READ,
    AGENTS_ROLES_REVOKE,
    AGENTS_SECURITY_EVENTS_READ,
    AGENTS_SESSIONS_CREATE,
    AGENTS_SESSIONS_READ,
    AGENTS_SESSIONS_REVOKE,
    AGENTS_STATE_READ,
    AGENTS_STATE_UPDATE,
    AGENTS_STATUS_READ,
    AGENTS_STATUS_UPDATE,
    AGENTS_SUSPEND,
    AGENTS_TRANSACTION_ORCHESTRATE,
    AGENTS_TRUST_READ,
    AGENTS_TRUST_UPDATE,
    AGENTS_VELOCITY_READ,
    POLICIES_EVALUATE,
)
from app.domain.exceptions.agent_exceptions import (
    AgentActivationError,
    AgentAlreadyActiveError,
    AgentAlreadyExistsError,
    AgentAlreadyRevokedError,
    AgentAlreadySuspendedError,
    AgentCredentialAlreadyExistsError,
    AgentCredentialNotFoundError,
    AgentIdentityNotFoundError,
    AgentNotFoundError,
    AgentPermissionAlreadyAssignedError,
    AgentPermissionAssignmentError,
    AgentPermissionNotFoundError,
    AgentRoleAlreadyAssignedError,
    AgentRoleAssignmentError,
    AgentRoleNotFoundError,
    AgentSessionAlreadyRevokedError,
    AgentSessionCreationError,
    AgentSessionNotFoundError,
    AgentStatusTransitionError,
    ApprovalExpiredError,
    CircuitBreakerOpenError,
    ContextBudgetExceededError,
    ExecutionBlockedError,
    ExecutionNotFoundError,
    ExecutionPolicyViolationError,
    ExecutionValidationError,
    HumanApprovalError,
    IntentNotFoundError,
    IntentValidationError,
    InvalidAgentLifecycleTransitionError,
    InvalidAgentTrustScoreError,
    MemoryNotFoundError,
    MemoryQuotaExceededError,
    NonRetryableExecutionError,
    OrchestrationNotFoundError,
    PlanGenerationError,
    PlanNotFoundError,
    PlanValidationError,
    ReconciliationRequiredError,
    SelfApprovalForbiddenError,
    ToolDisabledError,
    ToolExecutionError,
    ToolNotFoundError,
    ToolValidationError,
    WorkflowCancelledError,
    WorkflowExecutionError,
)
from app.infrastructure.database.models.purchase_intent import PurchaseIntent
from app.infrastructure.database.session import get_db_session
from app.schemas.agent_authorization import (
    AgentAuthorizationCheckRequest,
    AgentAuthorizationResponse,
)
from app.schemas.agent_identity_verification import (
    AgentIdentityVerificationRequest,
    AgentIdentityVerificationResult,
)
from app.schemas.agent_permission_evaluation import (
    PermissionEvaluationRequest,
    PermissionEvaluationResult,
)
from app.schemas.agents import (
    AgentActivationRequest,
    AgentActivationResponse,
    AgentAuditEventListCursor,
    AgentAuditEventListResponse,
    AgentAuditEventResponse,
    AgentBehaviourDeviationResponse,
    AgentBulkSessionRevokeResponse,
    AgentCategoryBehaviourResponse,
    AgentCreateRequest,
    AgentCredentialCreateRequest,
    AgentCredentialCreateResponse,
    AgentCredentialResponse,
    AgentIdentityResponse,
    AgentIntentCreateRequest,
    AgentIntentListCursor,
    AgentIntentListResponse,
    AgentIntentResponse,
    AgentLifecycleResponse,
    AgentListCursor,
    AgentListResponse,
    AgentMerchantBehaviourResponse,
    AgentMetadataResponse,
    AgentMetadataUpdateRequest,
    AgentPermissionAssignRequest,
    AgentPermissionListResponse,
    AgentPermissionResponse,
    AgentResponse,
    AgentRevocationRequest,
    AgentRevocationResponse,
    AgentRoleAssignRequest,
    AgentRoleListResponse,
    AgentRoleResponse,
    AgentSecurityEventListCursor,
    AgentSecurityEventListResponse,
    AgentSecurityEventResponse,
    AgentSessionCreateRequest,
    AgentSessionListCursor,
    AgentSessionListResponse,
    AgentSessionResponse,
    AgentSessionRevokeRequest,
    AgentStatusResponse,
    AgentStatusUpdateRequest,
    AgentSuspensionRequest,
    AgentSuspensionResponse,
    AgentTrustResponse,
    AgentTrustUpdateRequest,
    AgentVelocityDetectionResponse,
    IntentExtractionRequest,
    StructuredIntentResponse,
)
from app.schemas.context import (
    ContextAssemblyRequest,
    ContextAssemblyResponse,
)
from app.schemas.execution import (
    AgentExecutionCreateRequest,
    AgentExecutionResponse,
)
from app.schemas.execution_reliability import (
    ExecutionReconcileRequest,
    ExecutionReliabilityResponse,
    ExecutionRetryRequest,
)
from app.schemas.human_approval import (
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    ApprovalRequestCreate,
    ApprovalRequestResponse,
)
from app.schemas.memory import (
    AgentMemoryCreateRequest,
    AgentMemoryRecallRequest,
    AgentMemoryRecallResponse,
    AgentMemoryResponse,
    AgentMemoryUpdateRequest,
    ShortTermMemoryListResponse,
    ShortTermMemorySetRequest,
)
from app.schemas.orchestration import (
    AgentOrchestrationCreateRequest,
    AgentOrchestrationResponse,
)
from app.schemas.plans import (
    AgentPlan,
    AgentPlanCreateRequest,
    AgentPlanResponse,
    AgentPlanValidateRequest,
    PlanValidationResult,
)
from app.schemas.policy_evaluation import (
    PolicyEvaluationContext,
    PolicyEvaluationResult,
)
from app.schemas.state import (
    AgentStateResponse,
    AgentStateUpdateRequest,
)
from app.schemas.tool_calling import ToolCallRequest, ToolCallResponse
from app.schemas.transaction_orchestration import (
    WorkflowCancelRequest,
    WorkflowCreateRequest,
    WorkflowResponse,
)

agents_router = APIRouter(tags=["Agent Management"])


def get_agent_service() -> AgentService:
    """FastAPI dependency factory for AgentService."""
    return AgentService()


def get_agent_identity_service() -> AgentIdentityService:
    """FastAPI dependency factory for AgentIdentityService."""
    return AgentIdentityService()


def get_agent_credential_service() -> AgentCredentialService:
    """FastAPI dependency factory for AgentCredentialService."""
    return AgentCredentialService()


def get_agent_lifecycle_service() -> AgentLifecycleService:
    """FastAPI dependency factory for AgentLifecycleService."""
    return AgentLifecycleService()


def get_agent_session_service() -> AgentSessionService:
    """FastAPI dependency factory for AgentSessionService."""
    return AgentSessionService()


def get_authorization_service() -> AuthorizationService:
    """FastAPI dependency factory for AuthorizationService."""
    return AuthorizationService()


def get_agent_metadata_service() -> AgentMetadataService:
    """FastAPI dependency factory for AgentMetadataService."""
    return AgentMetadataService()


def get_agent_audit_service() -> AgentAuditService:
    """FastAPI dependency factory for AgentAuditService."""
    return AgentAuditService()


def get_agent_security_event_service() -> AgentSecurityEventService:
    """FastAPI dependency factory for AgentSecurityEventService."""
    return AgentSecurityEventService()


def get_agent_trust_service() -> AgentTrustService:
    """FastAPI dependency factory for AgentTrustService."""
    return AgentTrustService()


def get_agent_behaviour_deviation_service() -> AgentBehaviourDeviationService:
    """FastAPI dependency factory for AgentBehaviourDeviationService."""
    return AgentBehaviourDeviationService()


def get_agent_velocity_detection_service() -> AgentVelocityDetectionService:
    """FastAPI dependency factory for AgentVelocityDetectionService."""
    return AgentVelocityDetectionService()


def get_agent_merchant_behaviour_service() -> AgentMerchantBehaviourService:
    """FastAPI dependency factory for AgentMerchantBehaviourService."""
    return AgentMerchantBehaviourService()


def get_agent_category_behaviour_service() -> AgentCategoryBehaviourService:
    """FastAPI dependency factory for AgentCategoryBehaviourService."""
    return AgentCategoryBehaviourService()


def get_intent_extraction_service() -> IntentExtractionService:
    """FastAPI dependency factory for IntentExtractionService."""
    return IntentExtractionService()


def get_intent_classification_service() -> IntentClassificationService:
    """FastAPI dependency factory for IntentClassificationService."""
    return IntentClassificationService()


def get_intent_storage_service() -> IntentStorageService:
    """FastAPI dependency factory for IntentStorageService."""
    return IntentStorageService()


def get_plan_generation_service() -> PlanGenerationService:
    """FastAPI dependency factory for PlanGenerationService."""
    return PlanGenerationService()


def get_plan_validation_service() -> PlanValidationService:
    """FastAPI dependency factory for PlanValidationService."""
    return PlanValidationService()


def get_agent_planning_service(
    gen_service: Annotated[PlanGenerationService, Depends(get_plan_generation_service)],
    val_service: Annotated[PlanValidationService, Depends(get_plan_validation_service)],
    intent_storage_service: Annotated[IntentStorageService, Depends(get_intent_storage_service)],
) -> AgentPlanningService:
    """FastAPI dependency factory for AgentPlanningService."""
    return AgentPlanningService(
        generation_service=gen_service,
        validation_service=val_service,
        intent_storage_service=intent_storage_service,
    )


def get_agent_orchestrator_service() -> AgentOrchestratorService:
    """FastAPI dependency factory for AgentOrchestratorService."""
    return AgentOrchestratorService()


def get_agent_state_service() -> AgentStateService:
    """FastAPI dependency factory for AgentStateService."""
    return AgentStateService()


def get_agent_execution_service() -> AgentExecutionService:
    """FastAPI dependency factory for AgentExecutionService."""
    return AgentExecutionService()


def get_agent_context_service() -> AgentContextService:
    """FastAPI dependency factory for AgentContextService."""
    return AgentContextService()


def get_agent_memory_service() -> AgentMemoryService:
    """FastAPI dependency factory for AgentMemoryService."""
    return AgentMemoryService()


def get_short_term_memory_service() -> ShortTermMemoryService:
    """FastAPI dependency factory for ShortTermMemoryService."""
    return ShortTermMemoryService()


# ---------------------------------------------------------------------------
# Phase 119 — Registry & Discovery Routes
# ---------------------------------------------------------------------------


@agents_router.get(
    "/agents",
    status_code=status.HTTP_200_OK,
    summary="List Agents",
    description="List agents belonging to the authenticated tenant using keyset pagination.",
    operation_id="list_agents",
)
async def list_agents(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AgentService, Depends(get_agent_service)],
    limit: Annotated[int, Query(ge=1, le=100, description="Page size limit")] = 20,
    cursor_created_at: Annotated[
        datetime | None,
        Query(description="Keyset cursor: created_at timestamp of last item"),
    ] = None,
    cursor_id: Annotated[
        uuid.UUID | None,
        Query(description="Keyset cursor: user/agent ID of last item"),
    ] = None,
    search: Annotated[
        str | None,
        Query(description="Optional search term matching agent name or slug"),
    ] = None,
    agent_type: Annotated[
        str | None,
        Query(description="Optional filter by agent_type (e.g. 'autonomous')"),
    ] = None,
    agent_status: Annotated[
        str | None,
        Query(alias="status", description="Optional filter by status (e.g. 'active')"),
    ] = None,
) -> AgentListResponse:
    """List tenant agents with keyset pagination and search filters."""
    agents, has_more = await service.list_agents(
        db,
        current_user.tenant_id,
        cursor_created_at=cursor_created_at,
        cursor_id=cursor_id,
        limit=limit,
        search=search,
        agent_type=agent_type,
        status=agent_status,
    )
    cursor = AgentListCursor(
        next_created_at=agents[-1].created_at if (has_more and agents) else None,
        next_id=agents[-1].id if (has_more and agents) else None,
    )
    return AgentListResponse(
        agents=[AgentResponse.model_validate(a) for a in agents],
        count=len(agents),
        cursor=cursor,
    )


# ---------------------------------------------------------------------------
# Phase 120 — Agent Creation Route
# ---------------------------------------------------------------------------


@agents_router.post(
    "/agents",
    status_code=status.HTTP_201_CREATED,
    summary="Create Agent",
    description="Create a new agent and its default identity profile within the tenant.",
    operation_id="create_agent",
)
async def create_agent(
    body: AgentCreateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_CREATE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AgentService, Depends(get_agent_service)],
) -> AgentResponse:
    """Execute production-grade atomic agent and identity creation."""
    try:
        agent = await service.create_agent(db, current_user.tenant_id, body)
    except AgentAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return AgentResponse.model_validate(agent)


# ---------------------------------------------------------------------------
# Agent Retrieval Routes
# ---------------------------------------------------------------------------


@agents_router.get(
    "/agents/{agent_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Agent",
    description="Retrieve an individual agent by ID within the authenticated tenant.",
    operation_id="get_agent",
)
async def get_agent(
    agent_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AgentService, Depends(get_agent_service)],
) -> AgentResponse:
    """Retrieve agent by ID (tenant-scoped, IDOR-protected)."""
    try:
        agent = await service.get_agent(db, current_user.tenant_id, agent_id)
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AgentResponse.model_validate(agent)


# ---------------------------------------------------------------------------
# Phase 121 — Agent Identity Route
# ---------------------------------------------------------------------------


@agents_router.get(
    "/agents/{agent_id}/identity",
    status_code=status.HTTP_200_OK,
    summary="Get Agent Identity",
    description="Retrieve non-secret identity profile metadata for an agent.",
    operation_id="get_agent_identity",
)
async def get_agent_identity(
    agent_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    identity_service: Annotated[AgentIdentityService, Depends(get_agent_identity_service)],
) -> AgentIdentityResponse:
    """Retrieve non-secret agent identity (tenant-scoped)."""
    try:
        identity = await identity_service.get_agent_identity(db, current_user.tenant_id, agent_id)
    except AgentIdentityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AgentIdentityResponse.model_validate(identity)


# ---------------------------------------------------------------------------
# Phase 122 — Agent Credential Routes
# ---------------------------------------------------------------------------


@agents_router.post(
    "/agents/{agent_id}/credentials",
    status_code=status.HTTP_201_CREATED,
    summary="Issue Agent Credential",
    description="Issue a new credential for an agent. Raw secret returned ONLY ONCE.",
    operation_id="issue_agent_credential",
)
async def issue_agent_credential(
    agent_id: uuid.UUID,
    body: AgentCredentialCreateRequest,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_CREDENTIAL_CREATE))
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cred_service: Annotated[AgentCredentialService, Depends(get_agent_credential_service)],
) -> AgentCredentialCreateResponse:
    """Issue a new agent credential. The raw secret is returned ONLY ONCE."""
    try:
        cred, raw_secret = await cred_service.create_credential(
            db, current_user.tenant_id, agent_id, body
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AgentCredentialAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return AgentCredentialCreateResponse(
        id=cred.id,
        tenant_id=cred.tenant_id,
        agent_id=cred.agent_id,
        credential_type=cred.credential_type,
        credential_identifier=cred.credential_identifier,
        raw_secret=raw_secret,
        status=cred.status,
        created_at=cred.created_at,
        expires_at=cred.expires_at,
    )


@agents_router.get(
    "/agents/{agent_id}/credentials",
    status_code=status.HTTP_200_OK,
    summary="List Agent Credentials Metadata",
    description="List safe metadata for credentials issued to an agent (NO secret material).",
    operation_id="list_agent_credentials",
)
async def list_agent_credentials(
    agent_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_CREDENTIAL_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cred_service: Annotated[AgentCredentialService, Depends(get_agent_credential_service)],
) -> list[AgentCredentialResponse]:
    """List safe credential metadata records for an agent (tenant-scoped)."""
    creds = await cred_service.list_credentials(db, current_user.tenant_id, agent_id)
    return [AgentCredentialResponse.model_validate(c) for c in creds]


@agents_router.get(
    "/agents/{agent_id}/credentials/{credential_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Agent Credential Metadata",
    description="Retrieve safe metadata for a specific agent credential (NO secret material).",
    operation_id="get_agent_credential",
)
async def get_agent_credential(
    agent_id: uuid.UUID,
    credential_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_CREDENTIAL_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cred_service: Annotated[AgentCredentialService, Depends(get_agent_credential_service)],
) -> AgentCredentialResponse:
    """Retrieve safe credential metadata by ID (tenant-scoped)."""
    try:
        cred = await cred_service.get_credential(
            db, current_user.tenant_id, agent_id, credential_id
        )
    except AgentCredentialNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AgentCredentialResponse.model_validate(cred)


# ---------------------------------------------------------------------------
# Phase 124 — Agent Activation Route
# ---------------------------------------------------------------------------


@agents_router.post(
    "/agents/{agent_id}/activate",
    status_code=status.HTTP_200_OK,
    summary="Activate Agent",
    description="Transition an agent from 'provisioning' to 'active' status atomically.",
    operation_id="activate_agent",
)
async def activate_agent(
    agent_id: uuid.UUID,
    body: AgentActivationRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_ACTIVATE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    lifecycle_service: Annotated[AgentLifecycleService, Depends(get_agent_lifecycle_service)],
) -> AgentActivationResponse:
    """Execute production-grade agent activation (Phase 124)."""
    try:
        agent, lifecycle = await lifecycle_service.activate_agent(
            db,
            current_user.tenant_id,
            agent_id,
            reason=body.reason,
            actor_id=current_user.user.id,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AgentAlreadyActiveError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (InvalidAgentLifecycleTransitionError, AgentActivationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AgentActivationResponse(
        agent_id=agent.id,
        tenant_id=agent.tenant_id,
        status=agent.status,
        activated_at=lifecycle.activated_at or datetime.now(),
        message=f"Agent '{agent.name}' activated successfully.",
        lifecycle=AgentLifecycleResponse.model_validate(lifecycle),
    )


# ---------------------------------------------------------------------------
# Phase 125 — Agent Suspension Route
# ---------------------------------------------------------------------------


@agents_router.post(
    "/agents/{agent_id}/suspend",
    status_code=status.HTTP_200_OK,
    summary="Suspend Agent",
    description="Suspend an active agent while preserving historical data.",
    operation_id="suspend_agent",
)
async def suspend_agent(
    agent_id: uuid.UUID,
    body: AgentSuspensionRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_SUSPEND))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    lifecycle_service: Annotated[AgentLifecycleService, Depends(get_agent_lifecycle_service)],
) -> AgentSuspensionResponse:
    """Execute production-grade agent suspension (Phase 125)."""
    try:
        agent, lifecycle, revoked_count = await lifecycle_service.suspend_agent(
            db,
            current_user.tenant_id,
            agent_id,
            reason=body.reason,
            actor_id=current_user.user.id,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AgentAlreadySuspendedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except InvalidAgentLifecycleTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AgentSuspensionResponse(
        agent_id=agent.id,
        tenant_id=agent.tenant_id,
        status=agent.status,
        suspended_at=lifecycle.suspended_at or datetime.now(),
        message=f"Agent '{agent.name}' suspended successfully.",
        revoked_sessions_count=revoked_count,
        lifecycle=AgentLifecycleResponse.model_validate(lifecycle),
    )


# ---------------------------------------------------------------------------
# Phase 126 — Agent Revocation Route
# ---------------------------------------------------------------------------


@agents_router.post(
    "/agents/{agent_id}/revoke",
    status_code=status.HTTP_200_OK,
    summary="Revoke Agent",
    description="Permanently deactivate an agent from further operation.",
    operation_id="revoke_agent",
)
async def revoke_agent(
    agent_id: uuid.UUID,
    body: AgentRevocationRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_REVOKE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    lifecycle_service: Annotated[AgentLifecycleService, Depends(get_agent_lifecycle_service)],
) -> AgentRevocationResponse:
    """Execute production-grade agent revocation/deactivation (Phase 126)."""
    try:
        (
            agent,
            lifecycle,
            rev_sessions,
            rev_creds,
        ) = await lifecycle_service.revoke_agent(
            db,
            current_user.tenant_id,
            agent_id,
            reason=body.reason,
            actor_id=current_user.user.id,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AgentAlreadyRevokedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except InvalidAgentLifecycleTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AgentRevocationResponse(
        agent_id=agent.id,
        tenant_id=agent.tenant_id,
        status=agent.status,
        deactivated_at=lifecycle.deactivated_at or datetime.now(),
        message=f"Agent '{agent.name}' revoked and deactivated permanently.",
        revoked_sessions_count=rev_sessions,
        revoked_credentials_count=rev_creds,
        lifecycle=AgentLifecycleResponse.model_validate(lifecycle),
    )


# ---------------------------------------------------------------------------
# Phase 127 — Agent Session Routes
# ---------------------------------------------------------------------------


@agents_router.post(
    "/agents/{agent_id}/sessions",
    status_code=status.HTTP_201_CREATED,
    summary="Create Agent Session",
    description="Issue a new runtime session context for an active agent.",
    operation_id="create_agent_session",
)
async def create_agent_session(
    agent_id: uuid.UUID,
    body: AgentSessionCreateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_SESSIONS_CREATE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    session_service: Annotated[AgentSessionService, Depends(get_agent_session_service)],
) -> AgentSessionResponse:
    """Issue a new agent session context."""
    try:
        sess = await session_service.create_session(db, current_user.tenant_id, agent_id, body)
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AgentSessionCreationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return AgentSessionResponse.model_validate(sess)


@agents_router.get(
    "/agents/{agent_id}/sessions",
    status_code=status.HTTP_200_OK,
    summary="List Agent Sessions",
    description="List active and historical sessions for an agent using keyset pagination.",
    operation_id="list_agent_sessions",
)
async def list_agent_sessions(
    agent_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_SESSIONS_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    session_service: Annotated[AgentSessionService, Depends(get_agent_session_service)],
    limit: Annotated[int, Query(ge=1, le=100, description="Page size limit")] = 20,
    cursor_created_at: Annotated[
        datetime | None,
        Query(description="Keyset cursor: created_at timestamp of last item"),
    ] = None,
    cursor_id: Annotated[
        uuid.UUID | None,
        Query(description="Keyset cursor: session ID of last item"),
    ] = None,
    session_status: Annotated[
        str | None,
        Query(alias="status", description="Filter by status (e.g. 'active')"),
    ] = None,
) -> AgentSessionListResponse:
    """List agent sessions with keyset pagination."""
    try:
        sessions, has_more = await session_service.list_sessions(
            db,
            current_user.tenant_id,
            agent_id,
            cursor_created_at=cursor_created_at,
            cursor_id=cursor_id,
            limit=limit,
            status_filter=session_status,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    cursor = AgentSessionListCursor(
        next_created_at=sessions[-1].created_at if (has_more and sessions) else None,
        next_id=sessions[-1].id if (has_more and sessions) else None,
    )
    return AgentSessionListResponse(
        sessions=[AgentSessionResponse.model_validate(s) for s in sessions],
        count=len(sessions),
        cursor=cursor,
    )


@agents_router.get(
    "/agents/{agent_id}/sessions/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Agent Session Metadata",
    description="Retrieve safe metadata for a specific agent session.",
    operation_id="get_agent_session",
)
async def get_agent_session(
    agent_id: uuid.UUID,
    session_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_SESSIONS_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    session_service: Annotated[AgentSessionService, Depends(get_agent_session_service)],
) -> AgentSessionResponse:
    """Retrieve agent session metadata by ID (tenant-scoped)."""
    try:
        sess = await session_service.get_session(db, current_user.tenant_id, agent_id, session_id)
    except AgentSessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AgentSessionResponse.model_validate(sess)


@agents_router.post(
    "/agents/{agent_id}/sessions/{session_id}/revoke",
    status_code=status.HTTP_200_OK,
    summary="Revoke Agent Session",
    description="Revoke a specific active agent runtime session.",
    operation_id="revoke_agent_session",
)
async def revoke_agent_session(
    agent_id: uuid.UUID,
    session_id: uuid.UUID,
    body: AgentSessionRevokeRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_SESSIONS_REVOKE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    session_service: Annotated[AgentSessionService, Depends(get_agent_session_service)],
) -> AgentSessionResponse:
    """Revoke a specific agent session."""
    try:
        sess = await session_service.revoke_session(
            db, current_user.tenant_id, agent_id, session_id, reason=body.reason
        )
    except AgentSessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AgentSessionAlreadyRevokedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return AgentSessionResponse.model_validate(sess)


@agents_router.post(
    "/agents/{agent_id}/sessions/revoke-all",
    status_code=status.HTTP_200_OK,
    summary="Bulk Revoke Agent Sessions",
    description="Revoke all active sessions belonging to an agent.",
    operation_id="revoke_all_agent_sessions",
)
async def revoke_all_agent_sessions(
    agent_id: uuid.UUID,
    body: AgentSessionRevokeRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_SESSIONS_REVOKE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    session_service: Annotated[AgentSessionService, Depends(get_agent_session_service)],
) -> AgentBulkSessionRevokeResponse:
    """Bulk revoke all active sessions for an agent."""
    try:
        count = await session_service.revoke_all_sessions(
            db, current_user.tenant_id, agent_id, reason=body.reason
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return AgentBulkSessionRevokeResponse(
        agent_id=agent_id,
        tenant_id=current_user.tenant_id,
        revoked_count=count,
        message=f"Revoked {count} active sessions for agent.",
    )


# ---------------------------------------------------------------------------
# Phase 128 — Agent Permission Routes
# ---------------------------------------------------------------------------


@agents_router.get(
    "/agents/{agent_id}/permissions",
    status_code=status.HTTP_200_OK,
    summary="List Agent Permissions",
    description="List direct permissions assigned to an agent within tenant scope.",
    operation_id="list_agent_permissions",
)
async def list_agent_permissions(
    agent_id: uuid.UUID,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_PERMISSIONS_READ))
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    auth_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> AgentPermissionListResponse:
    """List permissions assigned directly to an agent."""
    try:
        perms = await auth_service.list_agent_permissions(db, current_user.tenant_id, agent_id)
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    res_list: list[AgentPermissionResponse] = []
    for p in perms:
        res_list.append(
            AgentPermissionResponse(
                id=p.id,
                tenant_id=p.tenant_id,
                agent_id=p.agent_id,
                permission_id=p.permission_id,
                permission_name=p.permission.name if p.permission else None,
                created_at=p.created_at,
            )
        )

    return AgentPermissionListResponse(
        permissions=res_list,
        count=len(res_list),
    )


@agents_router.post(
    "/agents/{agent_id}/permissions",
    status_code=status.HTTP_201_CREATED,
    summary="Assign Permission to Agent",
    description="Assign a canonical permission to an agent within tenant scope.",
    operation_id="assign_agent_permission",
)
async def assign_agent_permission(
    agent_id: uuid.UUID,
    body: AgentPermissionAssignRequest,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_PERMISSIONS_ASSIGN))
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    auth_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> AgentPermissionResponse:
    """Assign a direct permission to an agent."""
    try:
        ap = await auth_service.assign_permission_to_agent(
            db, current_user.tenant_id, agent_id, body.permission_id
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AgentPermissionAlreadyAssignedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except AgentPermissionAssignmentError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AgentPermissionResponse(
        id=ap.id,
        tenant_id=ap.tenant_id,
        agent_id=ap.agent_id,
        permission_id=ap.permission_id,
        permission_name=ap.permission.name if ap.permission else None,
        created_at=ap.created_at,
    )


@agents_router.delete(
    "/agents/{agent_id}/permissions/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
    summary="Revoke Permission from Agent",
    description="Revoke a direct permission assignment from an agent.",
    operation_id="revoke_agent_permission",
)
async def revoke_agent_permission(
    agent_id: uuid.UUID,
    permission_id: uuid.UUID,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_PERMISSIONS_REVOKE))
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    auth_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> None:
    """Revoke a direct permission assignment from an agent."""
    try:
        await auth_service.revoke_permission_from_agent(
            db, current_user.tenant_id, agent_id, permission_id
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AgentPermissionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Phase 129 — Agent Role Routes
# ---------------------------------------------------------------------------


@agents_router.get(
    "/agents/{agent_id}/roles",
    status_code=status.HTTP_200_OK,
    summary="List Agent Roles",
    description="List roles assigned to an agent within tenant scope.",
    operation_id="list_agent_roles",
)
async def list_agent_roles(
    agent_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_ROLES_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    auth_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> AgentRoleListResponse:
    """List roles assigned to an agent."""
    try:
        roles = await auth_service.list_agent_roles(db, current_user.tenant_id, agent_id)
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    res_list: list[AgentRoleResponse] = []
    for r in roles:
        res_list.append(
            AgentRoleResponse(
                id=r.id,
                tenant_id=r.tenant_id,
                agent_id=r.agent_id,
                role_id=r.role_id,
                role_name=r.role.name if r.role else None,
                is_system=r.role.is_system if r.role else False,
                created_at=r.created_at,
            )
        )

    return AgentRoleListResponse(
        roles=res_list,
        count=len(res_list),
    )


@agents_router.post(
    "/agents/{agent_id}/roles",
    status_code=status.HTTP_201_CREATED,
    summary="Assign Role to Agent",
    description="Assign a tenant or system role to an agent.",
    operation_id="assign_agent_role",
)
async def assign_agent_role(
    agent_id: uuid.UUID,
    body: AgentRoleAssignRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_ROLES_ASSIGN))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    auth_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> AgentRoleResponse:
    """Assign a role to an agent."""
    try:
        ar = await auth_service.assign_role_to_agent(
            db, current_user.tenant_id, agent_id, body.role_id
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AgentRoleAlreadyAssignedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except AgentRoleAssignmentError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return AgentRoleResponse(
        id=ar.id,
        tenant_id=ar.tenant_id,
        agent_id=ar.agent_id,
        role_id=ar.role_id,
        role_name=ar.role.name if ar.role else None,
        is_system=ar.role.is_system if ar.role else False,
        created_at=ar.created_at,
    )


@agents_router.delete(
    "/agents/{agent_id}/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
    summary="Revoke Role from Agent",
    description="Revoke a role assignment from an agent.",
    operation_id="revoke_agent_role",
)
async def revoke_agent_role(
    agent_id: uuid.UUID,
    role_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_ROLES_REVOKE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    auth_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> None:
    """Revoke a role assignment from an agent."""
    try:
        await auth_service.remove_role_from_agent(db, current_user.tenant_id, agent_id, role_id)
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AgentRoleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Phase 130 — Agent Status Management Routes
# ---------------------------------------------------------------------------


@agents_router.get(
    "/agents/{agent_id}/status",
    status_code=status.HTTP_200_OK,
    summary="Get Agent Operational Status",
    description="Retrieve current operational status and lifecycle timestamps for an agent.",
    operation_id="get_agent_status",
)
async def get_agent_status(
    agent_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_STATUS_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    lifecycle_service: Annotated[AgentLifecycleService, Depends(get_agent_lifecycle_service)],
) -> AgentStatusResponse:
    """Retrieve agent operational status and lifecycle metadata."""
    try:
        lifecycle = await lifecycle_service.get_agent_lifecycle(
            db, current_user.tenant_id, agent_id
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return AgentStatusResponse(
        agent_id=lifecycle.agent_id,
        tenant_id=lifecycle.tenant_id,
        status=lifecycle.status,
        status_reason=lifecycle.status_reason,
        activated_at=lifecycle.activated_at,
        suspended_at=lifecycle.suspended_at,
        deactivated_at=lifecycle.deactivated_at,
        last_transition_at=lifecycle.last_transition_at,
    )


@agents_router.patch(
    "/agents/{agent_id}/status",
    status_code=status.HTTP_200_OK,
    summary="Update Agent Status",
    description="Request a controlled operational status transition for an agent.",
    operation_id="update_agent_status",
)
async def update_agent_status(
    agent_id: uuid.UUID,
    body: AgentStatusUpdateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_STATUS_UPDATE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    lifecycle_service: Annotated[AgentLifecycleService, Depends(get_agent_lifecycle_service)],
) -> AgentStatusResponse:
    """Execute controlled agent status transition delegating strictly to lifecycle service."""
    try:
        _, lifecycle, _ = await lifecycle_service.update_agent_status(
            db,
            current_user.tenant_id,
            agent_id,
            body.status,
            reason=body.reason,
            actor_id=current_user.user.id,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (AgentAlreadyActiveError, AgentAlreadySuspendedError, AgentAlreadyRevokedError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (
        InvalidAgentLifecycleTransitionError,
        AgentStatusTransitionError,
        AgentActivationError,
    ) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AgentStatusResponse(
        agent_id=lifecycle.agent_id,
        tenant_id=lifecycle.tenant_id,
        status=lifecycle.status,
        status_reason=lifecycle.status_reason,
        activated_at=lifecycle.activated_at,
        suspended_at=lifecycle.suspended_at,
        deactivated_at=lifecycle.deactivated_at,
        last_transition_at=lifecycle.last_transition_at,
    )


@agents_router.post(
    "/agents/{agent_id}/pause",
    status_code=status.HTTP_200_OK,
    summary="Pause Agent",
    description="Temporarily pause an active agent and revoke active runtime sessions.",
    operation_id="pause_agent",
)
async def pause_agent(
    agent_id: uuid.UUID,
    body: AgentStatusUpdateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_PAUSE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    lifecycle_service: Annotated[AgentLifecycleService, Depends(get_agent_lifecycle_service)],
) -> AgentStatusResponse:
    """Pause an active agent."""
    try:
        _, lifecycle, _ = await lifecycle_service.pause_agent(
            db,
            current_user.tenant_id,
            agent_id,
            reason=body.reason,
            actor_id=current_user.user.id,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (InvalidAgentLifecycleTransitionError, AgentStatusTransitionError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AgentStatusResponse(
        agent_id=lifecycle.agent_id,
        tenant_id=lifecycle.tenant_id,
        status=lifecycle.status,
        status_reason=lifecycle.status_reason,
        activated_at=lifecycle.activated_at,
        suspended_at=lifecycle.suspended_at,
        deactivated_at=lifecycle.deactivated_at,
        last_transition_at=lifecycle.last_transition_at,
    )


@agents_router.post(
    "/agents/{agent_id}/resume",
    status_code=status.HTTP_200_OK,
    summary="Resume Agent",
    description="Resume a paused agent back to active operational status.",
    operation_id="resume_agent",
)
async def resume_agent(
    agent_id: uuid.UUID,
    body: AgentStatusUpdateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_RESUME))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    lifecycle_service: Annotated[AgentLifecycleService, Depends(get_agent_lifecycle_service)],
) -> AgentStatusResponse:
    """Resume a paused agent."""
    try:
        _, lifecycle = await lifecycle_service.resume_agent(
            db,
            current_user.tenant_id,
            agent_id,
            reason=body.reason,
            actor_id=current_user.user.id,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AgentAlreadyActiveError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (InvalidAgentLifecycleTransitionError, AgentActivationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AgentStatusResponse(
        agent_id=lifecycle.agent_id,
        tenant_id=lifecycle.tenant_id,
        status=lifecycle.status,
        status_reason=lifecycle.status_reason,
        activated_at=lifecycle.activated_at,
        suspended_at=lifecycle.suspended_at,
        deactivated_at=lifecycle.deactivated_at,
        last_transition_at=lifecycle.last_transition_at,
    )


# ---------------------------------------------------------------------------
# Phase 131 — Agent Metadata Routes
# ---------------------------------------------------------------------------


@agents_router.get(
    "/agents/{agent_id}/metadata",
    status_code=status.HTTP_200_OK,
    summary="Get Agent Metadata",
    description="Retrieve non-sensitive JSONB metadata payload for an agent.",
    operation_id="get_agent_metadata",
)
async def get_agent_metadata(
    agent_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_METADATA_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    metadata_service: Annotated[AgentMetadataService, Depends(get_agent_metadata_service)],
) -> AgentMetadataResponse:
    """Retrieve non-sensitive metadata for an agent."""
    try:
        meta = await metadata_service.get_agent_metadata(db, current_user.tenant_id, agent_id)
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AgentMetadataResponse.model_validate(meta)


@agents_router.patch(
    "/agents/{agent_id}/metadata",
    status_code=status.HTTP_200_OK,
    summary="Update Agent Metadata",
    description="Merge non-sensitive key-value pairs into an agent's metadata profile.",
    operation_id="update_agent_metadata",
)
async def update_agent_metadata(
    agent_id: uuid.UUID,
    body: AgentMetadataUpdateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_METADATA_UPDATE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    metadata_service: Annotated[AgentMetadataService, Depends(get_agent_metadata_service)],
    audit_service: Annotated[AgentAuditService, Depends(get_agent_audit_service)],
) -> AgentMetadataResponse:
    """Update/merge custom metadata for an agent."""
    try:
        meta = await metadata_service.update_agent_metadata(
            db, current_user.tenant_id, agent_id, body.metadata_payload
        )
        await audit_service.record_audit_event(
            db,
            current_user.tenant_id,
            agent_id,
            current_user.user.id,
            event_type="metadata_updated",
            event_action="update_agent_metadata",
            event_result="success",
            event_metadata={"updated_keys": list(body.metadata_payload.keys())},
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AgentMetadataResponse.model_validate(meta)


# ---------------------------------------------------------------------------
# Phase 132 — Agent Audit Event Routes
# ---------------------------------------------------------------------------


@agents_router.get(
    "/agents/{agent_id}/audit-events",
    status_code=status.HTTP_200_OK,
    summary="List Agent Audit Events",
    description="List immutable audit logs for an agent using keyset pagination.",
    operation_id="list_agent_audit_events",
)
async def list_agent_audit_events(
    agent_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_AUDIT_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    audit_service: Annotated[AgentAuditService, Depends(get_agent_audit_service)],
    limit: Annotated[int, Query(ge=1, le=100, description="Page size limit")] = 20,
    cursor_occurred_at: Annotated[
        datetime | None,
        Query(description="Keyset cursor: occurred_at timestamp of last item"),
    ] = None,
    cursor_id: Annotated[
        uuid.UUID | None,
        Query(description="Keyset cursor: audit event ID of last item"),
    ] = None,
    event_type: Annotated[
        str | None,
        Query(description="Optional filter by event_type (e.g. 'agent_activated')"),
    ] = None,
) -> AgentAuditEventListResponse:
    """List tenant-scoped audit logs for an agent."""
    try:
        events, has_more = await audit_service.list_agent_audit_events(
            db,
            current_user.tenant_id,
            agent_id,
            cursor_occurred_at=cursor_occurred_at,
            cursor_id=cursor_id,
            limit=limit,
            event_type=event_type,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    cursor = AgentAuditEventListCursor(
        next_occurred_at=events[-1].occurred_at if (has_more and events) else None,
        next_id=events[-1].id if (has_more and events) else None,
    )
    return AgentAuditEventListResponse(
        events=[AgentAuditEventResponse.model_validate(e) for e in events],
        count=len(events),
        cursor=cursor,
    )


# ---------------------------------------------------------------------------
# Phase 133 — Agent Security Event Routes
# ---------------------------------------------------------------------------


@agents_router.get(
    "/agents/{agent_id}/security-events",
    status_code=status.HTTP_200_OK,
    summary="List Agent Security Events",
    description="List security logs for an agent using keyset pagination.",
    operation_id="list_agent_security_events",
)
async def list_agent_security_events(
    agent_id: uuid.UUID,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_SECURITY_EVENTS_READ))
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    security_event_service: Annotated[
        AgentSecurityEventService, Depends(get_agent_security_event_service)
    ],
    limit: Annotated[int, Query(ge=1, le=100, description="Page size limit")] = 20,
    cursor_occurred_at: Annotated[
        datetime | None,
        Query(description="Keyset cursor: occurred_at timestamp of last item"),
    ] = None,
    cursor_id: Annotated[
        uuid.UUID | None,
        Query(description="Keyset cursor: security event ID of last item"),
    ] = None,
    severity: Annotated[
        str | None,
        Query(description="Optional filter by severity (e.g. 'high', 'critical')"),
    ] = None,
    event_type: Annotated[
        str | None,
        Query(description="Optional filter by event_type (e.g. 'credential')"),
    ] = None,
) -> AgentSecurityEventListResponse:
    """List tenant-scoped security events for an agent."""
    try:
        events, has_more = await security_event_service.list_agent_security_events(
            db,
            current_user.tenant_id,
            agent_id,
            cursor_occurred_at=cursor_occurred_at,
            cursor_id=cursor_id,
            limit=limit,
            severity=severity,
            event_type=event_type,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    cursor = AgentSecurityEventListCursor(
        next_occurred_at=events[-1].occurred_at if (has_more and events) else None,
        next_id=events[-1].id if (has_more and events) else None,
    )
    return AgentSecurityEventListResponse(
        events=[AgentSecurityEventResponse.model_validate(e) for e in events],
        count=len(events),
        cursor=cursor,
    )


# ---------------------------------------------------------------------------
# Phase 134 — Agent Trust Data Routes
# ---------------------------------------------------------------------------


@agents_router.get(
    "/agents/{agent_id}/trust",
    status_code=status.HTTP_200_OK,
    summary="Get Agent Trust Posture",
    description="Retrieve trust status, score, and posture metadata for an agent.",
    operation_id="get_agent_trust",
)
async def get_agent_trust(
    agent_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_TRUST_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    trust_service: Annotated[AgentTrustService, Depends(get_agent_trust_service)],
) -> AgentTrustResponse:
    """Retrieve trust posture data for an agent."""
    try:
        trust = await trust_service.get_agent_trust(db, current_user.tenant_id, agent_id)
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AgentTrustResponse.model_validate(trust)


@agents_router.patch(
    "/agents/{agent_id}/trust",
    status_code=status.HTTP_200_OK,
    summary="Update Agent Trust Posture",
    description="Controlled administrative update of an agent's trust status and numerical score.",
    operation_id="update_agent_trust",
)
async def update_agent_trust(
    agent_id: uuid.UUID,
    body: AgentTrustUpdateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_TRUST_UPDATE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    trust_service: Annotated[AgentTrustService, Depends(get_agent_trust_service)],
    audit_service: Annotated[AgentAuditService, Depends(get_agent_audit_service)],
    security_event_service: Annotated[
        AgentSecurityEventService, Depends(get_agent_security_event_service)
    ],
) -> AgentTrustResponse:
    """Controlled administrative update of agent trust posture."""
    try:
        trust = await trust_service.update_agent_trust(
            db,
            current_user.tenant_id,
            agent_id,
            trust_status=body.trust_status,
            trust_score=body.trust_score,
            trust_reason=body.trust_reason,
            trust_metadata=body.trust_metadata,
        )

        # Audit and Security events for trust posture changes
        await audit_service.record_audit_event(
            db,
            current_user.tenant_id,
            agent_id,
            current_user.user.id,
            event_type="trust_updated",
            event_action="update_agent_trust",
            event_result="success",
            event_metadata={
                "trust_status": trust.trust_status,
                "trust_score": str(trust.trust_score) if trust.trust_score else None,
                "reason": body.trust_reason,
            },
        )
        await security_event_service.record_security_event(
            db,
            current_user.tenant_id,
            agent_id=agent_id,
            actor_id=current_user.user.id,
            event_type="security_control",
            event_action="security_control_triggered",
            event_result="success",
            severity="medium",
            event_payload={
                "trust_status": trust.trust_status,
                "trust_score": str(trust.trust_score) if trust.trust_score else None,
            },
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidAgentTrustScoreError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AgentTrustResponse.model_validate(trust)


# ---------------------------------------------------------------------------
# Phase 136 — Agent Behaviour Deviation Route
# ---------------------------------------------------------------------------


@agents_router.get(
    "/agents/{agent_id}/behaviour/deviation",
    status_code=status.HTTP_200_OK,
    summary="Evaluate Agent Behaviour Deviation",
    description="Evaluate deterministic behavioural deviation against historical baseline.",
    operation_id="get_agent_behaviour_deviation",
)
async def get_agent_behaviour_deviation(
    agent_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_BEHAVIOUR_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    dev_service: Annotated[
        AgentBehaviourDeviationService,
        Depends(get_agent_behaviour_deviation_service),
    ],
) -> AgentBehaviourDeviationResponse:
    """Evaluate agent behaviour deviation within tenant scope."""
    try:
        res = await dev_service.calculate_deviation(db, current_user.tenant_id, agent_id)
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return res


# ---------------------------------------------------------------------------
# Phase 137 — Agent Velocity Detection Route
# ---------------------------------------------------------------------------


@agents_router.get(
    "/agents/{agent_id}/velocity",
    status_code=status.HTTP_200_OK,
    summary="Evaluate Agent Activity Velocity",
    description="Evaluate transaction activity velocity within bounded time window.",
    operation_id="get_agent_velocity",
)
async def get_agent_velocity(
    agent_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_VELOCITY_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    vel_service: Annotated[
        AgentVelocityDetectionService, Depends(get_agent_velocity_detection_service)
    ],
    window: Annotated[
        str,
        Query(description="Time window to evaluate ('1h', '24h', '7d')"),
    ] = "24h",
    custom_threshold_count: Annotated[
        int | None,
        Query(ge=1, le=10000, description="Optional custom count threshold"),
    ] = None,
    custom_threshold_amount: Annotated[
        Decimal | None,
        Query(ge=0, description="Optional custom amount threshold"),
    ] = None,
) -> AgentVelocityDetectionResponse:
    """Evaluate agent activity velocity."""
    try:
        res = await vel_service.detect_velocity(
            db,
            current_user.tenant_id,
            agent_id,
            window=window,
            custom_threshold_count=custom_threshold_count,
            custom_threshold_amount=custom_threshold_amount,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return res


# ---------------------------------------------------------------------------
# Phase 138 — Merchant Behaviour Analysis Route
# ---------------------------------------------------------------------------


@agents_router.get(
    "/agents/{agent_id}/merchant-behaviour",
    status_code=status.HTTP_200_OK,
    summary="Analyze Merchant Interaction Behaviour",
    description="Analyze merchant concentration, new merchant addition, and pattern deviation.",
    operation_id="get_agent_merchant_behaviour",
)
async def get_agent_merchant_behaviour(
    agent_id: uuid.UUID,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_MERCHANT_BEHAVIOUR_READ))
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    mb_service: Annotated[
        AgentMerchantBehaviourService,
        Depends(get_agent_merchant_behaviour_service),
    ],
) -> AgentMerchantBehaviourResponse:
    """Analyze merchant interaction patterns for an agent."""
    try:
        res = await mb_service.analyze_merchant_behaviour(db, current_user.tenant_id, agent_id)
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return res


# ---------------------------------------------------------------------------
# Phase 139 — Category Behaviour Analysis Route
# ---------------------------------------------------------------------------


@agents_router.get(
    "/agents/{agent_id}/category-behaviour",
    status_code=status.HTTP_200_OK,
    summary="Analyze Category Interaction Behaviour",
    description="Analyze category-level distribution and concentration risk.",
    operation_id="get_agent_category_behaviour",
)
async def get_agent_category_behaviour(
    agent_id: uuid.UUID,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_CATEGORY_BEHAVIOUR_READ))
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cb_service: Annotated[
        AgentCategoryBehaviourService,
        Depends(get_agent_category_behaviour_service),
    ],
) -> AgentCategoryBehaviourResponse:
    """Analyze category interaction patterns for an agent."""
    try:
        res = await cb_service.analyze_category_behaviour(db, current_user.tenant_id, agent_id)
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return res


# ---------------------------------------------------------------------------
# Phase 140–142 — Intent Extraction & Classification Route
# ---------------------------------------------------------------------------


@agents_router.post(
    "/agents/{agent_id}/intent/extract",
    status_code=status.HTTP_200_OK,
    summary="Extract and Classify Semantic Intent",
    description="Extract structured intent and deterministic classification from request text.",
    operation_id="extract_and_classify_agent_intent",
)
async def extract_and_classify_agent_intent(
    agent_id: uuid.UUID,
    body: IntentExtractionRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    extraction_service: Annotated[IntentExtractionService, Depends(get_intent_extraction_service)],
    classification_service: Annotated[
        IntentClassificationService, Depends(get_intent_classification_service)
    ],
) -> StructuredIntentResponse:
    """Extract semantic intent and classify it deterministically within verified tenant scope."""
    try:
        ext_res = await extraction_service.extract_intent(
            db,
            current_user.tenant_id,
            agent_id,
            body.request_text,
            body.context_metadata,
        )
        class_res = await classification_service.classify_intent(
            db,
            current_user.tenant_id,
            agent_id,
            ext_res.extracted_intent,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return class_res


# ---------------------------------------------------------------------------
# Phase 145 — Intent Storage Routes
# ---------------------------------------------------------------------------


def to_agent_intent_response(pi: PurchaseIntent) -> AgentIntentResponse:
    """Map PurchaseIntent persistence model to AgentIntentResponse schema."""
    meta = pi.intent_metadata or {}
    return AgentIntentResponse(
        id=pi.id,
        tenant_id=pi.tenant_id,
        agent_id=pi.agent_id,
        intent_type=str(meta.get("intent_type", "UNKNOWN")),
        status=str(meta.get("status", "stored")),
        confidence=Decimal(str(meta.get("confidence", "1.0000"))),
        raw_text=meta.get("raw_text"),
        normalized_payload=meta.get("normalized_payload", {}),
        validation_metadata=meta.get("validation_metadata", {}),
        created_at=pi.created_at,
    )


@agents_router.post(
    "/agents/{agent_id}/intent",
    status_code=status.HTTP_201_CREATED,
    summary="Process and Store Agent Intent",
    description="Extract, classify, validate, normalize and store agent intent. ZERO execution.",
    operation_id="process_and_store_agent_intent",
)
async def process_and_store_agent_intent(
    agent_id: uuid.UUID,
    body: AgentIntentCreateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_INTENT_CREATE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    storage_service: Annotated[IntentStorageService, Depends(get_intent_storage_service)],
) -> AgentIntentResponse:
    """Process intent pipeline and persist normalized result inside tenant context (Phase 145)."""
    try:
        stored_intent = await storage_service.process_and_store_intent(
            db,
            tenant_id=current_user.tenant_id,
            agent_id=agent_id,
            user_id=current_user.user.id,
            request_text=body.request_text,
            context_metadata=body.context_metadata,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except IntentValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return to_agent_intent_response(stored_intent)


@agents_router.get(
    "/agents/{agent_id}/intent/{intent_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Stored Agent Intent",
    description="Retrieve a stored agent intent by ID within tenant scope.",
    operation_id="get_stored_agent_intent",
)
async def get_stored_agent_intent(
    agent_id: uuid.UUID,
    intent_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_INTENT_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    storage_service: Annotated[IntentStorageService, Depends(get_intent_storage_service)],
) -> AgentIntentResponse:
    """Retrieve stored agent intent by ID (tenant-scoped)."""
    try:
        stored_intent = await storage_service.get_intent(
            db, current_user.tenant_id, agent_id, intent_id
        )
    except (AgentNotFoundError, IntentNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return to_agent_intent_response(stored_intent)


@agents_router.get(
    "/agents/{agent_id}/intents",
    status_code=status.HTTP_200_OK,
    summary="List Stored Agent Intents",
    description="List stored intents for an agent using keyset pagination.",
    operation_id="list_stored_agent_intents",
)
async def list_stored_agent_intents(
    agent_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_INTENT_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    storage_service: Annotated[IntentStorageService, Depends(get_intent_storage_service)],
    limit: Annotated[int, Query(ge=1, le=100, description="Page size limit")] = 20,
    cursor_created_at: Annotated[
        datetime | None,
        Query(description="Keyset cursor: created_at timestamp of last item"),
    ] = None,
    cursor_id: Annotated[
        uuid.UUID | None,
        Query(description="Keyset cursor: intent ID of last item"),
    ] = None,
) -> AgentIntentListResponse:
    """List stored agent intents with keyset pagination."""
    try:
        items, has_more = await storage_service.list_intents(
            db,
            current_user.tenant_id,
            agent_id,
            cursor_created_at=cursor_created_at,
            cursor_id=cursor_id,
            limit=limit,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    cursor = AgentIntentListCursor(
        next_created_at=items[-1].created_at if (has_more and items) else None,
        next_id=items[-1].id if (has_more and items) else None,
    )
    return AgentIntentListResponse(
        intents=[to_agent_intent_response(i) for i in items],
        count=len(items),
        cursor=cursor,
    )


# ---------------------------------------------------------------------------
# Phase 146-148 — Agent Planning Engine, Generation & Validation Routes
# ---------------------------------------------------------------------------


def to_agent_plan_response(plan: AgentPlan) -> AgentPlanResponse:
    """Map AgentPlan domain model to AgentPlanResponse schema."""
    return AgentPlanResponse(
        plan_id=plan.plan_id,
        tenant_id=plan.tenant_id,
        agent_id=plan.agent_id,
        intent_id=plan.intent_id,
        intent_type=plan.intent_type,
        version=plan.version,
        status=plan.status,
        steps=plan.steps,
        constraints=plan.constraints,
        metadata=plan.metadata,
        created_at=plan.created_at,
    )


@agents_router.post(
    "/agents/{agent_id}/plans",
    status_code=status.HTTP_201_CREATED,
    summary="Create Agent Plan",
    description="Generate and validate a deterministic agent plan representation. ZERO execution.",
    operation_id="create_agent_plan",
)
async def create_agent_plan(
    agent_id: uuid.UUID,
    body: AgentPlanCreateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_PLANS_CREATE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    planning_service: Annotated[AgentPlanningService, Depends(get_agent_planning_service)],
) -> AgentPlanResponse:
    """Generate and validate a plan representation (Phase 146-147)."""
    try:
        plan, _ = await planning_service.create_and_validate_plan(
            db,
            tenant_id=current_user.tenant_id,
            agent_id=agent_id,
            user_id=current_user.user.id,
            intent_id=body.intent_id,
            request_text=body.request_text,
            context_metadata=body.context_metadata,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (PlanGenerationError, PlanValidationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return to_agent_plan_response(plan)


@agents_router.get(
    "/agents/{agent_id}/plans/{plan_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Agent Plan",
    description="Retrieve a stored agent plan representation by ID within tenant scope.",
    operation_id="get_agent_plan",
)
async def get_agent_plan(
    agent_id: uuid.UUID,
    plan_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_PLANS_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    planning_service: Annotated[AgentPlanningService, Depends(get_agent_planning_service)],
) -> AgentPlanResponse:
    """Retrieve stored agent plan by ID (tenant-scoped)."""
    try:
        plan = await planning_service.get_plan(db, current_user.tenant_id, agent_id, plan_id)
    except (AgentNotFoundError, PlanNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return to_agent_plan_response(plan)


@agents_router.post(
    "/agents/{agent_id}/plans/{plan_id}/validate",
    status_code=status.HTTP_200_OK,
    summary="Validate Agent Plan",
    description="Perform fail-closed validation on an agent plan representation.",
    operation_id="validate_agent_plan",
)
async def validate_agent_plan(
    agent_id: uuid.UUID,
    plan_id: uuid.UUID,
    body: AgentPlanValidateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_PLANS_VALIDATE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    planning_service: Annotated[AgentPlanningService, Depends(get_agent_planning_service)],
) -> PlanValidationResult:
    """Validate an existing agent plan representation fail-closed (Phase 148)."""
    try:
        # If plan_id doesn't match body plan_id, reject ID mismatch
        if body.plan.plan_id != plan_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"URL plan_id '{plan_id}' mismatches body plan_id '{body.plan.plan_id}'.",
            )
        val_result = await planning_service.validate_existing_plan(
            db, current_user.tenant_id, agent_id, body.plan
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return val_result


# ---------------------------------------------------------------------------
# Phase 149 — Agent Orchestrator Routes
# ---------------------------------------------------------------------------


@agents_router.post(
    "/agents/{agent_id}/orchestrate",
    status_code=status.HTTP_201_CREATED,
    summary="Orchestrate Agent",
    description="Create orchestration decision from intent and plan. ZERO execution.",
    operation_id="orchestrate_agent",
)
async def orchestrate_agent(
    agent_id: uuid.UUID,
    body: AgentOrchestrationCreateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_ORCHESTRATE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    orchestrator_service: Annotated[
        AgentOrchestratorService, Depends(get_agent_orchestrator_service)
    ],
) -> AgentOrchestrationResponse:
    """Create a deterministic orchestration decision for an agent (Phase 149)."""
    try:
        orch_res = await orchestrator_service.orchestrate_agent(
            db,
            tenant_id=current_user.tenant_id,
            agent_id=agent_id,
            user_id=current_user.user.id,
            intent_id=body.intent_id,
            plan_id=body.plan_id,
            context_metadata=body.context_metadata,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return orch_res


@agents_router.get(
    "/agents/{agent_id}/orchestrations/{orchestration_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Agent Orchestration",
    description="Retrieve an orchestration decision record by ID within tenant scope.",
    operation_id="get_agent_orchestration",
)
async def get_agent_orchestration(
    agent_id: uuid.UUID,
    orchestration_id: uuid.UUID,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_ORCHESTRATION_READ))
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    orchestrator_service: Annotated[
        AgentOrchestratorService, Depends(get_agent_orchestrator_service)
    ],
) -> AgentOrchestrationResponse:
    """Retrieve stored orchestration record by ID (tenant-scoped)."""
    try:
        orch_res = await orchestrator_service.get_orchestration(
            db, current_user.tenant_id, agent_id, orchestration_id
        )
    except (AgentNotFoundError, OrchestrationNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return orch_res


# ---------------------------------------------------------------------------
# Phase 150 — Agent State Management Routes
# ---------------------------------------------------------------------------


@agents_router.get(
    "/agents/{agent_id}/state",
    status_code=status.HTTP_200_OK,
    summary="Get Agent Runtime State",
    description="Retrieve current agent runtime state within tenant scope.",
    operation_id="get_agent_state",
)
async def get_agent_state(
    agent_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_STATE_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    state_service: Annotated[AgentStateService, Depends(get_agent_state_service)],
) -> AgentStateResponse:
    """Fetch agent runtime state representation (Phase 150)."""
    try:
        state_res = await state_service.get_agent_state(db, current_user.tenant_id, agent_id)
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return state_res


@agents_router.patch(
    "/agents/{agent_id}/state",
    status_code=status.HTTP_200_OK,
    summary="Update Agent Runtime State",
    description="Transition agent runtime state according to canonical state rules.",
    operation_id="update_agent_state",
)
async def update_agent_state(
    agent_id: uuid.UUID,
    body: AgentStateUpdateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_STATE_UPDATE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    state_service: Annotated[AgentStateService, Depends(get_agent_state_service)],
) -> AgentStateResponse:
    """Transition agent runtime state fail-closed (Phase 150)."""
    try:
        state_res = await state_service.update_agent_state(
            db,
            tenant_id=current_user.tenant_id,
            agent_id=agent_id,
            user_id=current_user.user.id,
            requested_transition=body.requested_transition,
            reason=body.reason,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return state_res


# ---------------------------------------------------------------------------
# Phase 151 — Agent Execution Loop Routes
# ---------------------------------------------------------------------------


@agents_router.post(
    "/agents/{agent_id}/executions",
    status_code=status.HTTP_201_CREATED,
    summary="Create Agent Execution",
    description="Run controlled agent execution loop for a validated plan (Phase 151).",
    operation_id="create_agent_execution",
)
async def create_agent_execution(
    agent_id: uuid.UUID,
    body: AgentExecutionCreateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_EXECUTE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    execution_service: Annotated[AgentExecutionService, Depends(get_agent_execution_service)],
) -> AgentExecutionResponse:
    """Create and run controlled step-by-step agent execution loop (Phase 151)."""
    try:
        exec_res = await execution_service.create_and_run_execution(
            db,
            tenant_id=current_user.tenant_id,
            agent_id=agent_id,
            user_id=current_user.user.id,
            plan_id=body.plan_id,
            orchestration_id=body.orchestration_id,
            retry_policy=body.retry_policy,
        )
    except (AgentNotFoundError, ExecutionNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ExecutionValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ExecutionBlockedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ExecutionPolicyViolationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return exec_res


@agents_router.get(
    "/agents/{agent_id}/executions/{execution_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Agent Execution",
    description="Retrieve execution loop status by ID within tenant scope (Phase 151).",
    operation_id="get_agent_execution",
)
async def get_agent_execution(
    agent_id: uuid.UUID,
    execution_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_EXECUTION_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    execution_service: Annotated[AgentExecutionService, Depends(get_agent_execution_service)],
) -> AgentExecutionResponse:
    """Retrieve execution loop representation by ID (tenant-scoped)."""
    try:
        exec_res = await execution_service.get_execution(
            db, current_user.tenant_id, agent_id, execution_id
        )
    except (AgentNotFoundError, ExecutionNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return exec_res


@agents_router.post(
    "/agents/{agent_id}/executions/{execution_id}/cancel",
    status_code=status.HTTP_200_OK,
    summary="Cancel Agent Execution",
    description="Cancel an ongoing agent execution loop within tenant scope (Phase 151).",
    operation_id="cancel_agent_execution",
)
async def cancel_agent_execution(
    agent_id: uuid.UUID,
    execution_id: uuid.UUID,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_EXECUTION_CANCEL))
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    execution_service: Annotated[AgentExecutionService, Depends(get_agent_execution_service)],
) -> AgentExecutionResponse:
    """Cancel an active agent execution loop safely (Phase 151)."""
    try:
        exec_res = await execution_service.cancel_execution(
            db,
            tenant_id=current_user.tenant_id,
            agent_id=agent_id,
            user_id=current_user.user.id,
            execution_id=execution_id,
        )
    except (AgentNotFoundError, ExecutionNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return exec_res


# ---------------------------------------------------------------------------
# Phase 152 — Agent Context Management Routes
# ---------------------------------------------------------------------------


@agents_router.post(
    "/agents/{agent_id}/context/assemble",
    status_code=status.HTTP_200_OK,
    summary="Assemble Agent Context",
    description="Assemble, prioritize, limit, and sanitize agent context (Phase 152).",
    operation_id="assemble_agent_context",
)
async def assemble_agent_context(
    agent_id: uuid.UUID,
    body: ContextAssemblyRequest,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_CONTEXT_ASSEMBLE))
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    context_service: Annotated[AgentContextService, Depends(get_agent_context_service)],
) -> ContextAssemblyResponse:
    """Assemble prioritized context representation (Phase 152)."""
    try:
        ctx_res = await context_service.assemble_agent_context(
            db, current_user.tenant_id, agent_id, body
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ContextBudgetExceededError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ctx_res


# ---------------------------------------------------------------------------
# Phase 153 — Agent Unified Memory Routes
# ---------------------------------------------------------------------------


@agents_router.post(
    "/agents/{agent_id}/memories",
    status_code=status.HTTP_201_CREATED,
    summary="Create Agent Memory Record",
    description="Create or update a unified agent memory record (Phase 153).",
    operation_id="create_agent_memory",
)
async def create_agent_memory(
    agent_id: uuid.UUID,
    body: AgentMemoryCreateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_MEMORY_WRITE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    memory_service: Annotated[AgentMemoryService, Depends(get_agent_memory_service)],
) -> AgentMemoryResponse:
    """Create or update unified agent memory record (Phase 153)."""
    try:
        mem_res = await memory_service.create_memory(
            db, current_user.tenant_id, agent_id, current_user.user.id, body
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return mem_res


@agents_router.get(
    "/agents/{agent_id}/memories",
    status_code=status.HTTP_200_OK,
    summary="List Agent Memories",
    description="List active agent memory records within tenant scope (Phase 153).",
    operation_id="list_agent_memories",
)
async def list_agent_memories(
    agent_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_MEMORY_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    memory_service: Annotated[AgentMemoryService, Depends(get_agent_memory_service)],
    namespace: str | None = None,
    memory_type: str | None = None,
    session_id: uuid.UUID | None = None,
    task_id: uuid.UUID | None = None,
) -> list[AgentMemoryResponse]:
    """List agent memory records within tenant scope."""
    try:
        memories = await memory_service.list_memories(
            db,
            current_user.tenant_id,
            agent_id,
            namespace=namespace,
            memory_type=memory_type,
            session_id=session_id,
            task_id=task_id,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return memories


@agents_router.get(
    "/agents/{agent_id}/memories/{memory_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Agent Memory Record",
    description="Retrieve a specific memory record by ID (Phase 153).",
    operation_id="get_agent_memory",
)
async def get_agent_memory(
    agent_id: uuid.UUID,
    memory_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_MEMORY_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    memory_service: Annotated[AgentMemoryService, Depends(get_agent_memory_service)],
) -> AgentMemoryResponse:
    """Retrieve memory record by ID within tenant scope."""
    try:
        mem_res = await memory_service.get_memory(db, current_user.tenant_id, agent_id, memory_id)
    except (AgentNotFoundError, MemoryNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return mem_res


@agents_router.patch(
    "/agents/{agent_id}/memories/{memory_id}",
    status_code=status.HTTP_200_OK,
    summary="Update Agent Memory Record",
    description="Update an existing agent memory record (Phase 153).",
    operation_id="update_agent_memory",
)
async def update_agent_memory(
    agent_id: uuid.UUID,
    memory_id: uuid.UUID,
    body: AgentMemoryUpdateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_MEMORY_WRITE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    memory_service: Annotated[AgentMemoryService, Depends(get_agent_memory_service)],
) -> AgentMemoryResponse:
    """Update memory record within tenant scope."""
    try:
        mem_res = await memory_service.update_memory(
            db, current_user.tenant_id, agent_id, current_user.user.id, memory_id, body
        )
    except (AgentNotFoundError, MemoryNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return mem_res


@agents_router.delete(
    "/agents/{agent_id}/memories/{memory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete Agent Memory Record",
    description="Soft-delete a memory record within tenant scope (Phase 153).",
    operation_id="delete_agent_memory",
)
async def delete_agent_memory(
    agent_id: uuid.UUID,
    memory_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_MEMORY_DELETE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    memory_service: Annotated[AgentMemoryService, Depends(get_agent_memory_service)],
) -> Response:
    """Soft-delete memory record within tenant scope."""
    try:
        await memory_service.delete_memory(
            db, current_user.tenant_id, agent_id, current_user.user.id, memory_id
        )
    except (AgentNotFoundError, MemoryNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Phase 154 — Short-Term Working Memory Routes
# ---------------------------------------------------------------------------


@agents_router.post(
    "/agents/{agent_id}/sessions/{session_id}/memory",
    status_code=status.HTTP_201_CREATED,
    summary="Set Short-Term Working Memory Variable",
    description="Store session/task working memory variable (Phase 154).",
    operation_id="set_short_term_memory_variable",
)
async def set_short_term_memory_variable(
    agent_id: uuid.UUID,
    session_id: uuid.UUID,
    body: ShortTermMemorySetRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_MEMORY_WRITE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    short_term_service: Annotated[ShortTermMemoryService, Depends(get_short_term_memory_service)],
) -> AgentMemoryResponse:
    """Set short-term working memory variable for active session/task."""
    try:
        mem_res = await short_term_service.set_variable(
            db, current_user.tenant_id, agent_id, current_user.user.id, session_id, body
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except MemoryQuotaExceededError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return mem_res


@agents_router.get(
    "/agents/{agent_id}/sessions/{session_id}/memory",
    status_code=status.HTTP_200_OK,
    summary="Get Short-Term Working Memory",
    description="Fetch working memory variables for session/task (Phase 154).",
    operation_id="get_short_term_working_memory",
)
async def get_short_term_working_memory(
    agent_id: uuid.UUID,
    session_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_MEMORY_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    short_term_service: Annotated[ShortTermMemoryService, Depends(get_short_term_memory_service)],
    task_id: uuid.UUID | None = None,
) -> ShortTermMemoryListResponse:
    """Fetch working memory variables for session/task."""
    try:
        mem_res = await short_term_service.get_working_memory(
            db, current_user.tenant_id, agent_id, session_id=session_id, task_id=task_id
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return mem_res


@agents_router.delete(
    "/agents/{agent_id}/sessions/{session_id}/memory",
    status_code=status.HTTP_200_OK,
    summary="Clear Short-Term Working Memory",
    description="Clear working memory variables for session/task (Phase 154).",
    operation_id="clear_short_term_working_memory",
)
async def clear_short_term_working_memory(
    agent_id: uuid.UUID,
    session_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_MEMORY_DELETE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    short_term_service: Annotated[ShortTermMemoryService, Depends(get_short_term_memory_service)],
    task_id: uuid.UUID | None = None,
) -> dict[str, Any]:
    """Clear session/task working memory variables."""
    try:
        cleared = await short_term_service.clear_working_memory(
            db,
            current_user.tenant_id,
            agent_id,
            current_user.user.id,
            session_id=session_id,
            task_id=task_id,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return {"status": "success", "cleared_count": cleared}


# ---------------------------------------------------------------------------
# Phase 161 — Phase 163 Dependency Factories & Services
# ---------------------------------------------------------------------------


def get_agent_transaction_orchestrator_service() -> AgentTransactionOrchestratorService:
    """Dependency factory for AgentTransactionOrchestratorService."""
    return AgentTransactionOrchestratorService()


def get_human_approval_workflow_service() -> HumanApprovalWorkflowService:
    """Dependency factory for HumanApprovalWorkflowService."""
    return HumanApprovalWorkflowService()


def get_agent_execution_reliability_service() -> AgentExecutionReliabilityService:
    """Dependency factory for AgentExecutionReliabilityService."""
    return AgentExecutionReliabilityService()


def get_agent_identity_verification_service() -> AgentIdentityVerificationService:
    """Dependency factory for AgentIdentityVerificationService."""
    return AgentIdentityVerificationService()


def get_agent_authorization_service() -> AgentAuthorizationService:
    """Dependency factory for AgentAuthorizationService."""
    return AgentAuthorizationService()


def get_agent_permission_evaluation_service() -> AgentPermissionEvaluationService:
    """Dependency factory for AgentPermissionEvaluationService."""
    return AgentPermissionEvaluationService()


def get_policy_evaluation_service() -> PolicyEvaluationService:
    """Dependency factory for PolicyEvaluationService."""
    return PolicyEvaluationService()


# ---------------------------------------------------------------------------
# Phase 161 — Agent Transaction Orchestration Routes
# ---------------------------------------------------------------------------


@agents_router.post(
    "/agents/{agent_id}/workflows",
    status_code=status.HTTP_201_CREATED,
    summary="Create Transaction Workflow",
    description="Orchestrate multi-step transaction workflow (Phase 161).",
    operation_id="create_transaction_workflow",
)
async def create_transaction_workflow(
    agent_id: uuid.UUID,
    body: WorkflowCreateRequest,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_TRANSACTION_ORCHESTRATE))
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    orchestrator_service: Annotated[
        AgentTransactionOrchestratorService, Depends(get_agent_transaction_orchestrator_service)
    ],
) -> WorkflowResponse:
    """Create and start an orchestrated transaction workflow."""
    try:
        res = await orchestrator_service.create_and_start_workflow(
            db, current_user.tenant_id, agent_id, body, user_id=current_user.user.id
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return res


@agents_router.get(
    "/agents/{agent_id}/workflows/{workflow_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Transaction Workflow Status",
    description="Retrieve status of an orchestrated transaction workflow (Phase 161).",
    operation_id="get_transaction_workflow",
)
async def get_transaction_workflow(
    agent_id: uuid.UUID,
    workflow_id: uuid.UUID,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_TRANSACTION_ORCHESTRATE))
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    orchestrator_service: Annotated[
        AgentTransactionOrchestratorService, Depends(get_agent_transaction_orchestrator_service)
    ],
) -> WorkflowResponse:
    """Get workflow status by ID."""
    try:
        res = await orchestrator_service.get_workflow_status(
            db, current_user.tenant_id, agent_id, workflow_id
        )
    except WorkflowExecutionError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return res


@agents_router.post(
    "/agents/{agent_id}/workflows/{workflow_id}/cancel",
    status_code=status.HTTP_200_OK,
    summary="Cancel Transaction Workflow",
    description="Cancel an active transaction workflow (Phase 161).",
    operation_id="cancel_transaction_workflow",
)
async def cancel_transaction_workflow(
    agent_id: uuid.UUID,
    workflow_id: uuid.UUID,
    body: WorkflowCancelRequest,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_TRANSACTION_ORCHESTRATE))
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    orchestrator_service: Annotated[
        AgentTransactionOrchestratorService, Depends(get_agent_transaction_orchestrator_service)
    ],
) -> WorkflowResponse:
    """Cancel active workflow."""
    try:
        res = await orchestrator_service.cancel_workflow(
            db, current_user.tenant_id, agent_id, workflow_id, body
        )
    except WorkflowExecutionError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except WorkflowCancelledError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return res


# ---------------------------------------------------------------------------
# Phase 162 — Human Approval & Authorization Workflow Routes
# ---------------------------------------------------------------------------


@agents_router.post(
    "/agents/{agent_id}/approvals",
    status_code=status.HTTP_201_CREATED,
    summary="Create Human Approval Request",
    description="Create human-in-the-loop approval request for sensitive action (Phase 162).",
    operation_id="create_human_approval_request",
)
async def create_human_approval_request(
    agent_id: uuid.UUID,
    body: ApprovalRequestCreate,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_APPROVAL_REQUEST))
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    approval_service: Annotated[
        HumanApprovalWorkflowService, Depends(get_human_approval_workflow_service)
    ],
) -> ApprovalRequestResponse:
    """Create human approval request."""
    return await approval_service.create_approval_request(
        db, current_user.tenant_id, agent_id, body, requesting_user_id=current_user.user.id
    )


@agents_router.post(
    "/agents/{agent_id}/approvals/{approval_id}/decide",
    status_code=status.HTTP_200_OK,
    summary="Record Approval Decision",
    description="Record decision action with self-approval security enforcement (Phase 162).",
    operation_id="record_approval_decision",
)
async def record_approval_decision(
    agent_id: uuid.UUID,
    approval_id: uuid.UUID,
    body: ApprovalDecisionRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_APPROVAL_DECIDE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    approval_service: Annotated[
        HumanApprovalWorkflowService, Depends(get_human_approval_workflow_service)
    ],
) -> ApprovalDecisionResponse:
    """Record reviewer decision action."""
    try:
        res = await approval_service.record_approval_decision(
            db,
            current_user.tenant_id,
            approval_id,
            body,
            reviewer_id=current_user.user.id,
            reviewer_email=current_user.user.email,
        )
    except SelfApprovalForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ApprovalExpiredError as exc:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=str(exc)) from exc
    except HumanApprovalError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return res


@agents_router.get(
    "/agents/{agent_id}/approvals/{approval_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Human Approval Request Status",
    description="Fetch human approval request state by ID (Phase 162).",
    operation_id="get_human_approval_request",
)
async def get_human_approval_request(
    agent_id: uuid.UUID,
    approval_id: uuid.UUID,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_APPROVAL_REQUEST))
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    approval_service: Annotated[
        HumanApprovalWorkflowService, Depends(get_human_approval_workflow_service)
    ],
) -> ApprovalRequestResponse:
    """Get approval request by ID."""
    try:
        res = await approval_service.get_approval_request(db, current_user.tenant_id, approval_id)
    except HumanApprovalError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return res


# ---------------------------------------------------------------------------
# Phase 163 — Agent Execution Reliability Routes
# ---------------------------------------------------------------------------


@agents_router.post(
    "/agents/{agent_id}/reliability/retry",
    status_code=status.HTTP_200_OK,
    summary="Safe Execution Retry",
    description="Attempt safe execution retry with exponential backoff and idempotency protection (Phase 163).",  # noqa: E501
    operation_id="attempt_safe_execution_retry",
)
async def attempt_safe_execution_retry(
    agent_id: uuid.UUID,
    body: ExecutionRetryRequest,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_RELIABILITY_RECOVER))
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    reliability_service: Annotated[
        AgentExecutionReliabilityService, Depends(get_agent_execution_reliability_service)
    ],
) -> ExecutionReliabilityResponse:
    """Attempt safe retry of failed execution step."""
    try:
        res = await reliability_service.attempt_safe_execution_retry(
            db, current_user.tenant_id, agent_id, body
        )
    except CircuitBreakerOpenError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    except NonRetryableExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except ReconciliationRequiredError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return res


@agents_router.post(
    "/agents/{agent_id}/reliability/reconcile",
    status_code=status.HTTP_200_OK,
    summary="Reconcile Execution State",
    description="Reconcile ambiguous or partial financial transaction execution (Phase 163).",
    operation_id="reconcile_execution_state",
)
async def reconcile_execution_state(
    agent_id: uuid.UUID,
    body: ExecutionReconcileRequest,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_RELIABILITY_RECOVER))
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    reliability_service: Annotated[
        AgentExecutionReliabilityService, Depends(get_agent_execution_reliability_service)
    ],
) -> ExecutionReliabilityResponse:
    """Reconcile ambiguous execution state."""
    return await reliability_service.reconcile_execution_state(
        db, current_user.tenant_id, agent_id, body
    )


def get_tool_execution_service() -> ToolExecutionService:
    """Dependency factory for ToolExecutionService."""
    return ToolExecutionService()


@agents_router.post(
    "/agents/{agent_id}/memories/{memory_id}/archive",
    response_model=AgentMemoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Archive Long-Term Memory",
    description="Archive a specific long-term memory record (Phase 155).",
    operation_id="archive_agent_memory",
)
async def archive_agent_memory(
    agent_id: uuid.UUID,
    memory_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_MEMORY_WRITE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    memory_service: Annotated[AgentMemoryService, Depends(get_agent_memory_service)],
) -> AgentMemoryResponse:
    """Archive a long-term memory record."""
    try:
        return await memory_service.archive_memory(
            db, current_user.tenant_id, agent_id, current_user.user.id, memory_id
        )
    except (AgentNotFoundError, MemoryNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@agents_router.post(
    "/agents/{agent_id}/memories/{memory_id}/restore",
    response_model=AgentMemoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Restore Archived Memory",
    description="Restore an archived long-term memory record (Phase 155).",
    operation_id="restore_agent_memory",
)
async def restore_agent_memory(
    agent_id: uuid.UUID,
    memory_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_MEMORY_WRITE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    memory_service: Annotated[AgentMemoryService, Depends(get_agent_memory_service)],
) -> AgentMemoryResponse:
    """Restore an archived long-term memory record."""
    try:
        return await memory_service.restore_memory(
            db, current_user.tenant_id, agent_id, current_user.user.id, memory_id
        )
    except (AgentNotFoundError, MemoryNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@agents_router.post(
    "/agents/{agent_id}/memories/recall",
    response_model=AgentMemoryRecallResponse,
    status_code=status.HTTP_200_OK,
    summary="Recall Agent Memories",
    description="Perform multi-factor weighted memory recall and relevance ranking (Phase 155).",
    operation_id="recall_agent_memories",
)
async def recall_agent_memories(
    agent_id: uuid.UUID,
    request: AgentMemoryRecallRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_MEMORY_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    memory_service: Annotated[AgentMemoryService, Depends(get_agent_memory_service)],
) -> AgentMemoryRecallResponse:
    """Perform multi-factor memory recall."""
    try:
        return await memory_service.recall_memories(db, current_user.tenant_id, agent_id, request)
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@agents_router.post(
    "/agents/{agent_id}/tools/execute",
    response_model=ToolCallResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Agent Tool",
    description="Safely execute a registered tool request on behalf of an agent (Phase 156).",  # noqa: E501
    operation_id="execute_agent_tool",
)
async def execute_agent_tool(
    agent_id: uuid.UUID,
    request: ToolCallRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_EXECUTE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    tool_service: Annotated[ToolExecutionService, Depends(get_tool_execution_service)],
) -> ToolCallResponse:
    """Execute a registered tool request."""
    try:
        return await tool_service.execute_tool(
            db,
            tenant_id=current_user.tenant_id,
            agent_id=agent_id,
            request=request,
            user_id=current_user.user.id,
        )
    except ToolNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ToolDisabledError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ToolValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc  # noqa: E501
    except ToolExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc  # noqa: E501


# ---------------------------------------------------------------------------
# AGENTGUARD Security Foundation — Phase 182–184 Routes
# ---------------------------------------------------------------------------


@agents_router.post(
    "/agents/{agent_id}/identity/verify",
    response_model=AgentIdentityVerificationResult,
    status_code=status.HTTP_200_OK,
    summary="Verify Agent Identity",
    description="Verify agent existence, status, and tenant boundary fail-closed (Phase 182).",
    operation_id="verify_agent_identity",
)
async def verify_agent_identity_endpoint(
    agent_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(AGENTS_IDENTITY_VERIFY))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    identity_service: Annotated[
        AgentIdentityVerificationService, Depends(get_agent_identity_verification_service)
    ],
    payload: AgentIdentityVerificationRequest | None = None,
) -> AgentIdentityVerificationResult:
    """Verify agent identity and operational status."""
    try:
        p_id = payload.principal_id if payload else current_user.user.id
        return await identity_service.verify_agent_identity(
            db, tenant_id=current_user.tenant_id, agent_id=agent_id, principal_id=p_id
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@agents_router.post(
    "/agents/{agent_id}/authorization/check",
    response_model=AgentAuthorizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Check Agent Authorization",
    description="Check whether principal is authorized to perform action on behalf of agent (Phase 183).",  # noqa: E501
    operation_id="check_agent_authorization",
)
async def check_agent_authorization_endpoint(
    agent_id: uuid.UUID,
    request: AgentAuthorizationCheckRequest,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_AUTHORIZATION_CHECK))
    ],  # noqa: E501
    db: Annotated[AsyncSession, Depends(get_db_session)],
    authz_service: Annotated[AgentAuthorizationService, Depends(get_agent_authorization_service)],
) -> AgentAuthorizationResponse:
    """Check agent authorization decision."""
    try:
        return await authz_service.authorize_agent_action(
            db,
            tenant_id=current_user.tenant_id,
            agent_id=agent_id,
            principal_id=current_user.user.id,
            action=request.action,
            required_permissions=request.required_permissions,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@agents_router.post(
    "/agents/{agent_id}/permissions/evaluate",
    response_model=PermissionEvaluationResult,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Agent Permissions",
    description="Deterministically evaluate requested permissions against effective agent grants (Phase 184).",  # noqa: E501
    operation_id="evaluate_agent_permissions",
)
async def evaluate_agent_permissions_endpoint(
    agent_id: uuid.UUID,
    request: PermissionEvaluationRequest,
    current_user: Annotated[
        AuthenticatedUser, Depends(require_permission(AGENTS_PERMISSIONS_EVALUATE))
    ],  # noqa: E501
    db: Annotated[AsyncSession, Depends(get_db_session)],
    eval_service: Annotated[
        AgentPermissionEvaluationService, Depends(get_agent_permission_evaluation_service)
    ],
) -> PermissionEvaluationResult:
    """Evaluate requested permissions for an agent."""
    try:
        p_id = request.principal_id or current_user.user.id
        return await eval_service.evaluate_agent_permissions(
            db,
            tenant_id=current_user.tenant_id,
            agent_id=agent_id,
            requested_permissions=request.requested_permissions,
            principal_id=p_id,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@agents_router.get(
    "/agents/{agent_id}/permissions/effective",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
    summary="Get Agent Effective Permissions",
    description="Retrieve all effective permission names granted to an agent (Phase 184).",
    operation_id="get_agent_effective_permissions",
    dependencies=[Depends(require_permission(AGENTS_PERMISSIONS_READ))],
)
async def get_agent_effective_permissions_endpoint(
    agent_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    eval_service: Annotated[
        AgentPermissionEvaluationService, Depends(get_agent_permission_evaluation_service)
    ],
) -> list[str]:
    """Get all effective permission names for an agent."""
    try:
        return await eval_service.get_effective_agent_permissions(
            db, tenant_id=current_user.tenant_id, agent_id=agent_id
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@agents_router.post(
    "/agents/{agent_id}/policies/evaluate",
    response_model=PolicyEvaluationResult,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Agent Policies",
    description="Deterministically evaluate applicable security policies for an agent context (Phase 187).",  # noqa: E501
    operation_id="evaluate_agent_policies",
    dependencies=[Depends(require_permission(POLICIES_EVALUATE))],
)
async def evaluate_agent_policies_endpoint(
    agent_id: uuid.UUID,
    context: PolicyEvaluationContext,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    eval_service: Annotated[PolicyEvaluationService, Depends(get_policy_evaluation_service)],
) -> PolicyEvaluationResult:
    """Evaluate applicable security policies for an agent context."""
    try:
        if context.agent_id is None:
            context = PolicyEvaluationContext(
                tenant_id=current_user.tenant_id,
                agent_id=agent_id,
                principal_id=current_user.user.id,
                transaction_id=context.transaction_id,
                merchant_id=context.merchant_id,
                category=context.category,
                amount=context.amount,
                currency=context.currency,
                requested_action=context.requested_action,
                tool_name=context.tool_name,
                metadata=context.metadata,
            )
        return await eval_service.evaluate_policies(
            db, tenant_id=current_user.tenant_id, agent_id=agent_id, context=context
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
