"""Agent transport Pydantic schemas for AGENTPAY (Phase 119–135).

Schemas:
    AgentIdentityResponse          — Non-secret identity metadata
    AgentResponse                  — Safe agent representation
    AgentListCursor                — Keyset pagination cursor
    AgentListResponse              — Paginated list of agents
    AgentCreateRequest             — Strict request for agent creation
    AgentCredentialCreateRequest   — Request to issue credential
    AgentCredentialCreateResponse  — Response on credential issue (raw_secret ONCE)
    AgentCredentialResponse        — Safe credential metadata
    AgentLifecycleResponse         — Safe agent lifecycle state
    AgentActivationRequest         — Request for agent activation
    AgentActivationResponse        — Response for agent activation
    AgentSuspensionRequest         — Request for agent suspension
    AgentSuspensionResponse        — Response for agent suspension
    AgentRevocationRequest         — Request for agent revocation
    AgentRevocationResponse        — Response for agent revocation
    AgentSessionCreateRequest      — Request to create session
    AgentSessionResponse           — Safe agent session metadata
    AgentSessionListCursor         — Keyset cursor for session listing
    AgentSessionListResponse       — Paginated session list
    AgentSessionRevokeRequest      — Request for session revocation
    AgentBulkSessionRevokeResponse — Response for bulk session revocation
    AgentPermissionResponse        — Safe representation of assigned permission (Phase 128)
    AgentPermissionAssignRequest   — Request for permission assignment
    AgentPermissionListResponse    — List of assigned permissions for an agent
    AgentRoleResponse              — Safe representation of assigned role (Phase 129)
    AgentRoleAssignRequest         — Request for role assignment
    AgentRoleListResponse          — List of assigned roles for an agent
    AgentStatusResponse            — Safe operational status response (Phase 130)
    AgentStatusUpdateRequest       — Request for status transition
    AgentMetadataResponse          — Safe agent metadata payload (Phase 131)
    AgentMetadataUpdateRequest     — Request payload for updating agent metadata
    AgentAuditEventResponse        — Immutable agent audit trail record (Phase 132)
    AgentAuditEventListCursor      — Keyset cursor for audit log listing
    AgentAuditEventListResponse    — Paginated audit event list
    AgentSecurityEventResponse     — Safe agent security event record (Phase 133)
    AgentSecurityEventListCursor   — Keyset cursor for security event listing
    AgentSecurityEventListResponse — Paginated security event list
    AgentTrustResponse             — Safe agent trust posture data (Phase 134)
    AgentTrustUpdateRequest        — Request for controlled trust score update

Security invariants:
    - Never expose raw credentials or secret hashes in standard GET/list responses
    - All request schemas enforce extra='forbid' to prevent mass assignment
    - Tenant ID and internal metadata cannot be injected via request body
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# Agent Identity Schema (Phase 121)
# ---------------------------------------------------------------------------


class AgentIdentityResponse(BaseModel):
    """Safe agent identity representation — zero credentials or secret material."""

    id: uuid.UUID = Field(..., description="Identity UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Associated agent UUID")
    display_name: str | None = Field(default=None, description="Human-readable display name")
    identity_type: str = Field(..., description="Type classification (e.g. 'standard')")
    external_reference: str | None = Field(default=None, description="External reference ID")
    description: str | None = Field(default=None, description="Identity description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Agent Response Schemas (Phase 119)
# ---------------------------------------------------------------------------


class AgentResponse(BaseModel):
    """Safe agent representation for registry discovery — zero credentials."""

    id: uuid.UUID = Field(..., description="Agent UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    name: str = Field(..., description="Agent display name")
    slug: str = Field(..., description="Tenant-unique URL slug")
    agent_type: str = Field(..., description="Agent type (e.g. 'autonomous')")
    status: str = Field(..., description="Lifecycle status (e.g. 'active')")
    description: str | None = Field(default=None, description="Agent description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    identity: AgentIdentityResponse | None = Field(default=None, description="Associated identity")

    model_config = ConfigDict(from_attributes=True)


class AgentListCursor(BaseModel):
    """Keyset pagination cursor for agent listing."""

    next_created_at: datetime | None = Field(
        default=None, description="Cursor: created_at timestamp of last item"
    )
    next_id: uuid.UUID | None = Field(
        default=None, description="Cursor: id of last item for tie-breaking"
    )


class AgentListResponse(BaseModel):
    """Paginated agent list response with keyset cursor."""

    agents: list[AgentResponse] = Field(..., description="Page of agents")
    count: int = Field(..., description="Number of items in current page")
    cursor: AgentListCursor = Field(..., description="Pagination cursor for next page")

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Agent Creation Request Schema (Phase 120)
# ---------------------------------------------------------------------------


class AgentCreateRequest(BaseModel):
    """Strict request schema for creating a new agent."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Human-readable agent name",
    )
    slug: str | None = Field(
        default=None,
        max_length=255,
        description="Optional URL-safe slug. Auto-generated from name if omitted.",
    )
    agent_type: str = Field(
        default="autonomous",
        max_length=50,
        description="Agent operational type (default: 'autonomous')",
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional agent description",
    )
    display_name: str | None = Field(
        default=None,
        max_length=255,
        description="Optional display name for agent identity profile",
    )
    identity_type: str = Field(
        default="standard",
        max_length=50,
        description="Identity type classification (default: 'standard')",
    )
    external_reference: str | None = Field(
        default=None,
        max_length=255,
        description="Optional external identifier reference",
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    @field_validator("slug")
    @classmethod
    def validate_slug_format(cls, v: str | None) -> str | None:
        """Validate custom slug format."""
        if v is None or v == "":
            return None
        cleaned = v.strip().lower()
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", cleaned):
            raise ValueError(
                "slug must contain only lowercase letters, numbers, and single hyphens"
            )
        return cleaned


# ---------------------------------------------------------------------------
# Agent Credential Schemas (Phase 122)
# ---------------------------------------------------------------------------


class AgentCredentialCreateRequest(BaseModel):
    """Request schema for issuing a new agent credential."""

    credential_type: str = Field(
        default="api_key",
        max_length=50,
        description="Credential type classification (default: 'api_key')",
    )
    credential_identifier: str | None = Field(
        default=None,
        max_length=255,
        description="Optional custom credential lookup identifier",
    )
    expires_in_days: int | None = Field(
        default=None,
        ge=1,
        le=3650,
        description="Optional credential validity duration in days (max 10 years)",
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class AgentCredentialCreateResponse(BaseModel):
    """Response schema returned ONLY ONCE upon credential creation."""

    id: uuid.UUID = Field(..., description="Credential UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Associated agent UUID")
    credential_type: str = Field(..., description="Credential type")
    credential_identifier: str | None = Field(default=None, description="Public lookup identifier")
    raw_secret: str = Field(
        ..., description="Raw secret string — DISPLAYED ONLY ONCE AT CREATION TIME"
    )
    status: str = Field(..., description="Credential status")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: datetime | None = Field(default=None, description="Expiration timestamp")

    model_config = ConfigDict(from_attributes=True)


class AgentCredentialResponse(BaseModel):
    """Safe metadata schema for retrieving credential records."""

    id: uuid.UUID = Field(..., description="Credential UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Associated agent UUID")
    credential_type: str = Field(..., description="Credential type")
    credential_identifier: str | None = Field(default=None, description="Public lookup identifier")
    status: str = Field(..., description="Credential status")
    expires_at: datetime | None = Field(default=None, description="Expiration timestamp")
    revoked_at: datetime | None = Field(default=None, description="Revocation timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Agent Lifecycle & Activation Schemas (Phase 123 & 124)
# ---------------------------------------------------------------------------


class AgentLifecycleResponse(BaseModel):
    """Safe response representation of agent runtime operational state."""

    id: uuid.UUID = Field(..., description="Lifecycle record UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Associated agent UUID")
    status: str = Field(..., description="Operational status")
    status_reason: str | None = Field(default=None, description="Transition status reason")
    activated_at: datetime | None = Field(default=None, description="Activation timestamp")
    suspended_at: datetime | None = Field(default=None, description="Suspension timestamp")
    deactivated_at: datetime | None = Field(default=None, description="Deactivation timestamp")
    last_transition_at: datetime | None = Field(
        default=None, description="Timestamp of last state transition"
    )
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record update timestamp")

    model_config = ConfigDict(from_attributes=True)


class AgentActivationRequest(BaseModel):
    """Request schema for agent activation operation."""

    reason: str | None = Field(
        default=None,
        max_length=255,
        description="Optional reason for activation",
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class AgentActivationResponse(BaseModel):
    """Response payload for successful agent activation."""

    agent_id: uuid.UUID = Field(..., description="Activated agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    status: str = Field(..., description="New agent operational status ('active')")
    activated_at: datetime = Field(..., description="Activation timestamp")
    message: str = Field(..., description="Human-readable activation summary")
    lifecycle: AgentLifecycleResponse | None = Field(
        default=None, description="Updated lifecycle record"
    )

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Phase 125 — Agent Suspension Schemas
# ---------------------------------------------------------------------------


class AgentSuspensionRequest(BaseModel):
    """Request schema for suspending an active agent."""

    reason: str | None = Field(
        default=None,
        max_length=255,
        description="Optional reason for agent suspension",
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class AgentSuspensionResponse(BaseModel):
    """Response payload for successful agent suspension."""

    agent_id: uuid.UUID = Field(..., description="Suspended agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    status: str = Field(..., description="New agent operational status ('suspended')")
    suspended_at: datetime = Field(..., description="Suspension timestamp")
    message: str = Field(..., description="Human-readable suspension summary")
    revoked_sessions_count: int = Field(
        ..., description="Number of active agent sessions revoked upon suspension"
    )
    lifecycle: AgentLifecycleResponse | None = Field(
        default=None, description="Updated lifecycle record"
    )

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Phase 126 — Agent Revocation Schemas
# ---------------------------------------------------------------------------


class AgentRevocationRequest(BaseModel):
    """Request schema for revoking/deactivating an agent permanently."""

    reason: str | None = Field(
        default=None,
        max_length=255,
        description="Optional reason for agent revocation/deactivation",
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class AgentRevocationResponse(BaseModel):
    """Response payload for successful agent revocation/deactivation."""

    agent_id: uuid.UUID = Field(..., description="Deactivated agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    status: str = Field(..., description="New agent operational status ('deactivated')")
    deactivated_at: datetime = Field(..., description="Deactivation timestamp")
    message: str = Field(..., description="Human-readable revocation summary")
    revoked_sessions_count: int = Field(
        ..., description="Number of active agent sessions revoked upon deactivation"
    )
    revoked_credentials_count: int = Field(
        ..., description="Number of active credentials invalidated upon deactivation"
    )
    lifecycle: AgentLifecycleResponse | None = Field(
        default=None, description="Updated lifecycle record"
    )

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Phase 127 — Agent Session Schemas
# ---------------------------------------------------------------------------


class AgentSessionCreateRequest(BaseModel):
    """Request payload for issuing a new agent runtime session."""

    credential_id: uuid.UUID | None = Field(
        default=None,
        description="Optional credential UUID used to authenticate and create session",
    )
    device_id: str | None = Field(
        default=None,
        max_length=255,
        description="Optional client device identifier",
    )
    ip_address: str | None = Field(
        default=None,
        max_length=45,
        description="Optional client IP address",
    )
    user_agent: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional client User-Agent string",
    )
    expires_in_hours: int = Field(
        default=24,
        ge=1,
        le=8760,
        description="Requested session duration in hours (default: 24h, max: 1 year)",
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class AgentSessionResponse(BaseModel):
    """Safe metadata schema for agent runtime session representation."""

    id: uuid.UUID = Field(..., description="Session UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Associated agent UUID")
    credential_id: uuid.UUID | None = Field(default=None, description="Associated credential UUID")
    status: str = Field(..., description="Session status ('active', 'revoked', 'expired')")
    device_id: str | None = Field(default=None, description="Client device identifier")
    ip_address: str | None = Field(default=None, description="Client IP address")
    user_agent: str | None = Field(default=None, description="Client User-Agent string")
    session_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Safe metadata context"
    )
    last_activity_at: datetime | None = Field(
        default=None, description="Timestamp of last activity"
    )
    expires_at: datetime = Field(..., description="Session expiration timestamp")
    revoked_at: datetime | None = Field(default=None, description="Revocation timestamp")
    revocation_reason: str | None = Field(
        default=None, description="Human-readable revocation reason"
    )
    created_at: datetime = Field(..., description="Session creation timestamp")
    updated_at: datetime = Field(..., description="Session last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class AgentSessionListCursor(BaseModel):
    """Keyset pagination cursor for agent session listing."""

    next_created_at: datetime | None = Field(
        default=None, description="Cursor: created_at timestamp of last item"
    )
    next_id: uuid.UUID | None = Field(
        default=None, description="Cursor: id of last session for tie-breaking"
    )


class AgentSessionListResponse(BaseModel):
    """Paginated agent session list response with keyset cursor."""

    sessions: list[AgentSessionResponse] = Field(..., description="Page of session records")
    count: int = Field(..., description="Number of items in current page")
    cursor: AgentSessionListCursor = Field(..., description="Pagination cursor for next page")

    model_config = ConfigDict(from_attributes=True)


class AgentSessionRevokeRequest(BaseModel):
    """Request payload for revoking a specific agent session."""

    reason: str | None = Field(
        default=None,
        max_length=255,
        description="Optional reason for session revocation",
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class AgentBulkSessionRevokeResponse(BaseModel):
    """Response payload for bulk session revocation operation."""

    agent_id: uuid.UUID = Field(..., description="Agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    revoked_count: int = Field(..., description="Number of active sessions revoked")
    message: str = Field(..., description="Human-readable bulk revocation summary")

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Phase 128 — Agent Permission Assignment Schemas
# ---------------------------------------------------------------------------


class AgentPermissionResponse(BaseModel):
    """Safe representation of an assigned agent permission."""

    id: uuid.UUID = Field(..., description="Assignment UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Associated agent UUID")
    permission_id: uuid.UUID = Field(..., description="Assigned permission UUID")
    permission_name: str | None = Field(
        default=None, description="Canonical permission name string"
    )
    created_at: datetime = Field(..., description="Assignment creation timestamp")

    model_config = ConfigDict(from_attributes=True)


class AgentPermissionAssignRequest(BaseModel):
    """Request payload for assigning a permission to an agent."""

    permission_id: uuid.UUID = Field(..., description="UUID of the canonical permission to assign")

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class AgentPermissionListResponse(BaseModel):
    """Response list of permissions assigned to an agent."""

    permissions: list[AgentPermissionResponse] = Field(
        ..., description="List of direct permission assignments"
    )
    count: int = Field(..., description="Number of direct permission assignments")

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Phase 129 — Agent Role Assignment Schemas
# ---------------------------------------------------------------------------


class AgentRoleResponse(BaseModel):
    """Safe representation of an assigned agent role."""

    id: uuid.UUID = Field(..., description="Assignment UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Associated agent UUID")
    role_id: uuid.UUID = Field(..., description="Assigned role UUID")
    role_name: str | None = Field(default=None, description="Assigned role name")
    is_system: bool = Field(default=False, description="System role indicator")
    created_at: datetime = Field(..., description="Assignment creation timestamp")

    model_config = ConfigDict(from_attributes=True)


class AgentRoleAssignRequest(BaseModel):
    """Request payload for assigning a role to an agent."""

    role_id: uuid.UUID = Field(..., description="UUID of the tenant or system role to assign")

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class AgentRoleListResponse(BaseModel):
    """Response list of roles assigned to an agent."""

    roles: list[AgentRoleResponse] = Field(..., description="List of role assignments")
    count: int = Field(..., description="Number of assigned roles")

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Phase 130 — Agent Status Management Schemas
# ---------------------------------------------------------------------------


class AgentStatusResponse(BaseModel):
    """Safe operational status metadata response for an agent."""

    agent_id: uuid.UUID = Field(..., description="Agent UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    status: str = Field(..., description="Operational status")
    status_reason: str | None = Field(
        default=None, description="Human-readable transition status reason"
    )
    activated_at: datetime | None = Field(default=None, description="Activation timestamp")
    suspended_at: datetime | None = Field(default=None, description="Suspension timestamp")
    deactivated_at: datetime | None = Field(default=None, description="Deactivation timestamp")
    last_transition_at: datetime | None = Field(
        default=None, description="Timestamp of last state transition"
    )

    model_config = ConfigDict(from_attributes=True)


class AgentStatusUpdateRequest(BaseModel):
    """Request payload for requesting a controlled agent status transition."""

    status: str = Field(
        ...,
        max_length=50,
        description="Target operational status ('active', 'paused', 'suspended', 'deactivated')",
    )
    reason: str | None = Field(
        default=None,
        max_length=255,
        description="Optional reason for status transition",
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


# ---------------------------------------------------------------------------
# Phase 131 — Agent Metadata Schemas
# ---------------------------------------------------------------------------


class AgentMetadataResponse(BaseModel):
    """Safe representation of an Agent's metadata profile payload."""

    id: uuid.UUID = Field(..., description="Metadata record UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Associated agent UUID")
    metadata_payload: dict[str, Any] = Field(
        default_factory=dict, description="Custom non-sensitive JSONB metadata"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class AgentMetadataUpdateRequest(BaseModel):
    """Request payload for updating or merging agent metadata.

    Security:
        - `extra='forbid'` prevents client injection of protected internal fields.
    """

    metadata_payload: dict[str, Any] = Field(
        ..., description="Dict of key-value metadata pairs to merge"
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


# ---------------------------------------------------------------------------
# Phase 132 — Agent Audit Event Schemas
# ---------------------------------------------------------------------------


class AgentAuditEventResponse(BaseModel):
    """Safe representation of an immutable Agent audit log record."""

    id: uuid.UUID = Field(..., description="Audit record UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Associated agent UUID")
    actor_type: str = Field(..., description="Actor classification ('user', 'system')")
    actor_id: uuid.UUID = Field(..., description="Actor UUID")
    event_type: str = Field(..., description="Categorized event name (e.g. 'agent_activated')")
    event_action: str = Field(..., description="Event action description")
    event_result: str = Field(..., description="Event outcome ('success', 'failure')")
    request_id: str | None = Field(default=None, description="Correlation request ID")
    ip_address: str | None = Field(default=None, description="Client IP address")
    user_agent: str | None = Field(default=None, description="Client User-Agent")
    event_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Sanitized event metadata"
    )
    occurred_at: datetime = Field(..., description="Event timestamp")
    created_at: datetime = Field(..., description="Record creation timestamp")

    model_config = ConfigDict(from_attributes=True)


class AgentAuditEventListCursor(BaseModel):
    """Keyset pagination cursor for audit event listing."""

    next_occurred_at: datetime | None = Field(
        default=None, description="Cursor: occurred_at timestamp of last item"
    )
    next_id: uuid.UUID | None = Field(
        default=None, description="Cursor: id of last event for tie-breaking"
    )


class AgentAuditEventListResponse(BaseModel):
    """Paginated agent audit log response with keyset cursor."""

    events: list[AgentAuditEventResponse] = Field(..., description="Page of audit records")
    count: int = Field(..., description="Number of audit items in current page")
    cursor: AgentAuditEventListCursor = Field(..., description="Pagination cursor for next page")

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Phase 133 — Agent Security Event Schemas
# ---------------------------------------------------------------------------


class AgentSecurityEventResponse(BaseModel):
    """Safe representation of an Agent security log record."""

    id: uuid.UUID = Field(..., description="Security event UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Associated agent UUID")
    event_reference: str = Field(..., description="Unique event reference ID")
    event_type: str = Field(..., description="Classification type (e.g. 'credential')")
    event_action: str = Field(..., description="Action name (e.g. 'credential_used')")
    event_result: str = Field(..., description="Result status ('success', 'failure')")
    severity: str = Field(..., description="Severity level ('low', 'medium', 'high', 'critical')")
    source: str = Field(..., description="Event source ('internal', 'agent', etc.)")
    actor_type: str = Field(..., description="Actor type ('user', 'system')")
    actor_id: uuid.UUID | None = Field(default=None, description="Actor UUID")
    request_id: str | None = Field(default=None, description="Correlation request ID")
    ip_address: str | None = Field(default=None, description="Client IP address")
    user_agent: str | None = Field(default=None, description="Client User-Agent")
    event_payload: dict[str, Any] | None = Field(
        default_factory=dict, description="Sanitized safe event context"
    )
    occurred_at: datetime = Field(..., description="Event timestamp")
    created_at: datetime = Field(..., description="Record creation timestamp")

    model_config = ConfigDict(from_attributes=True)


class AgentSecurityEventListCursor(BaseModel):
    """Keyset pagination cursor for security event listing."""

    next_occurred_at: datetime | None = Field(
        default=None, description="Cursor: occurred_at timestamp of last item"
    )
    next_id: uuid.UUID | None = Field(
        default=None, description="Cursor: id of last event for tie-breaking"
    )


class AgentSecurityEventListResponse(BaseModel):
    """Paginated security event list response with keyset cursor."""

    events: list[AgentSecurityEventResponse] = Field(..., description="Page of security events")
    count: int = Field(..., description="Number of security events in page")
    cursor: AgentSecurityEventListCursor = Field(..., description="Pagination cursor for next page")

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Phase 134 — Agent Trust Data Schemas
# ---------------------------------------------------------------------------


class AgentTrustResponse(BaseModel):
    """Safe representation of an Agent's trust posture record."""

    id: uuid.UUID = Field(..., description="Trust record UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Associated agent UUID")
    trust_status: str = Field(..., description="Trust level ('unknown', 'high', 'restricted')")
    trust_score: Decimal | None = Field(
        default=None, description="Trust score (numeric range 0.00 - 100.00)"
    )
    trust_reason: str | None = Field(default=None, description="Reason for current trust posture")
    trust_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Non-sensitive trust posture metadata"
    )
    evaluated_at: datetime | None = Field(
        default=None, description="Timestamp of last trust evaluation"
    )
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record update timestamp")

    model_config = ConfigDict(from_attributes=True)


class AgentTrustUpdateRequest(BaseModel):
    """Request payload for updating an agent's trust posture.

    Security:
        - `extra='forbid'` strictly rejects unexpected fields.
        - Controlled administrative action only (`agents:trust_update`).
    """

    trust_status: str | None = Field(
        default=None,
        max_length=50,
        description="Target trust status ('unknown', 'low', 'medium', 'high', 'restricted')",
    )
    trust_score: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Numeric trust score (0.00 - 100.00)",
    )
    trust_reason: str | None = Field(
        default=None,
        max_length=255,
        description="Optional reason for trust score modification",
    )
    trust_metadata: dict[str, Any] | None = Field(
        default=None,
        description="Optional metadata key-value dict to merge",
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


# ---------------------------------------------------------------------------
# Phase 136 — Agent Behaviour Deviation Schemas
# ---------------------------------------------------------------------------


class AgentBehaviourDeviationResponse(BaseModel):
    """Structured, explainable agent behaviour deviation analysis result."""

    agent_id: uuid.UUID = Field(..., description="Agent UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    baseline_reference: str = Field(..., description="Baseline reference description")
    observed_value: Decimal = Field(..., description="Observed current activity metric")
    expected_range: str = Field(..., description="Expected baseline range (min - max)")
    deviation_score: Decimal = Field(..., description="Normalized deviation score (0.00 to 100.00)")
    deviation_type: str = Field(..., description="Classification of deviation (e.g. 'frequency')")
    severity: str = Field(..., description="Severity classification ('low', 'medium', 'high')")
    reason: str = Field(..., description="Human-readable explanation of deviation")
    evaluated_at: datetime = Field(..., description="Evaluation timestamp")

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Phase 137 — Agent Velocity Detection Schemas
# ---------------------------------------------------------------------------


class AgentVelocityDetectionResponse(BaseModel):
    """Structured, explainable agent activity velocity result."""

    agent_id: uuid.UUID = Field(..., description="Agent UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    window: str = Field(..., description="Time window evaluated (e.g. '1h', '24h', '7d')")
    observed_count: int = Field(..., description="Observed event/transaction count in window")
    observed_amount: Decimal = Field(
        default=Decimal("0.00"), description="Observed transaction sum in window"
    )
    threshold_count: int = Field(..., description="Configured velocity count threshold")
    threshold_amount: Decimal = Field(
        default=Decimal("0.00"), description="Configured velocity amount threshold"
    )
    velocity_score: Decimal = Field(..., description="Calculated velocity score (0.00 to 100.00)")
    severity: str = Field(..., description="Severity level ('low', 'medium', 'high', 'critical')")
    detection_type: str = Field(..., description="Type classification ('transaction_velocity')")
    reason: str = Field(..., description="Human-readable velocity evaluation explanation")
    evaluated_at: datetime = Field(..., description="Evaluation timestamp")

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Phase 138 — Merchant Behaviour Analysis Schemas
# ---------------------------------------------------------------------------


class AgentMerchantBehaviourResponse(BaseModel):
    """Structured merchant interaction pattern analysis result."""

    agent_id: uuid.UUID = Field(..., description="Agent UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    unique_merchants_count: int = Field(..., description="Total unique merchants interacted with")
    top_merchant_concentration: Decimal = Field(
        ..., description="Concentration ratio of top merchant (0.00 to 1.00)"
    )
    new_merchants_last_7d: int = Field(
        ..., description="Number of new merchants added in last 7 days"
    )
    total_transactions_count: int = Field(..., description="Total merchant transactions evaluated")
    total_amount: Decimal = Field(..., description="Total monetary volume processed")
    deviation_score: Decimal = Field(
        ..., description="Calculated merchant pattern deviation score (0.00 to 100.00)"
    )
    risk_indicator: str = Field(
        ..., description="Risk indicator ('normal', 'unusual_concentration', 'new_merchant_burst')"
    )
    severity: str = Field(..., description="Severity classification ('low', 'medium', 'high')")
    reason: str = Field(..., description="Explainable analysis reason")
    evaluated_at: datetime = Field(..., description="Evaluation timestamp")

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Phase 139 — Category Behaviour Analysis Schemas
# ---------------------------------------------------------------------------


class CategoryMetric(BaseModel):
    """Specific category transaction & monetary distribution metric."""

    category_name: str = Field(..., description="Category identifier or name")
    transaction_count: int = Field(..., description="Number of transactions in category")
    transaction_ratio: Decimal = Field(
        ..., description="Ratio of total transactions (0.00 to 1.00)"
    )
    monetary_volume: Decimal = Field(..., description="Total monetary volume in category")
    volume_ratio: Decimal = Field(..., description="Ratio of total volume (0.00 to 1.00)")


class AgentCategoryBehaviourResponse(BaseModel):
    """Structured, explainable category-level behaviour analysis result."""

    agent_id: uuid.UUID = Field(..., description="Agent UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    total_transactions_count: int = Field(..., description="Total transactions analyzed")
    unique_categories_count: int = Field(..., description="Count of unique active categories")
    dominant_category: str = Field(..., description="Category with highest transaction volume")
    dominant_category_ratio: Decimal = Field(
        ..., description="Ratio of dominant category (0.00 to 1.00)"
    )
    categories: list[CategoryMetric] = Field(
        default_factory=list, description="Per-category metric breakdown"
    )
    risk_indicator: str = Field(
        ..., description="Indicator ('normal', 'unusual_concentration', 'category_shift')"
    )
    severity: str = Field(..., description="Severity level ('low', 'medium', 'high')")
    reason: str = Field(..., description="Human-readable explanation")
    analyzed_at: datetime = Field(..., description="Analysis timestamp")

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Phase 140–142 — Intent Extraction, Classification & Structured Schema
# ---------------------------------------------------------------------------


class ExtractedEntities(BaseModel):
    """Extracted semantic entities with strict monetary precision and typing."""

    amount: Decimal | None = Field(default=None, description="Extracted monetary amount")
    currency: str | None = Field(
        default=None, max_length=10, description="Explicit currency code (e.g. INR, USD)"
    )
    merchant: str | None = Field(default=None, description="Extracted merchant reference")
    target_id: str | None = Field(default=None, description="Extracted target object ID")
    recipient: str | None = Field(default=None, description="Extracted recipient identifier")
    custom_entities: dict[str, str] = Field(
        default_factory=dict, description="Non-sensitive custom key-value entity pairs"
    )

    model_config = ConfigDict(extra="forbid")


class StructuredIntent(BaseModel):
    """Canonical representation of extracted and classified semantic intent."""

    intent_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique intent UUIDv7")
    action: str = Field(..., description="Extracted requested action (e.g. 'payment')")
    target: str | None = Field(default=None, description="Action target object")
    entities: ExtractedEntities = Field(
        default_factory=ExtractedEntities, description="Parsed semantic entities"
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Extracted operation parameters"
    )
    constraints: dict[str, Any] = Field(
        default_factory=dict, description="Extracted operational constraints"
    )
    confidence: Decimal = Field(
        ..., ge=0, le=1, description="Extraction confidence score (0.00 to 1.00)"
    )
    source: str = Field(..., description="Extraction source identifier (e.g. 'rule_based')")
    extracted_at: datetime = Field(
        default_factory=datetime.utcnow, description="Extraction timestamp"
    )

    model_config = ConfigDict(extra="forbid")


class IntentExtractionRequest(BaseModel):
    """Request payload for extracting intent from natural language or text."""

    request_text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language request text to extract",
    )
    context_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Optional non-sensitive context metadata"
    )

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class IntentExtractionResponse(BaseModel):
    """Result of intent extraction containing extracted StructuredIntent."""

    agent_id: uuid.UUID = Field(..., description="Agent UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    extracted_intent: StructuredIntent = Field(
        ..., description="Extracted structured intent payload"
    )
    extraction_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Extraction metadata (e.g. provider name)"
    )

    model_config = ConfigDict(from_attributes=True)


class IntentClassificationResponse(BaseModel):
    """Deterministic intent classification result."""

    agent_id: uuid.UUID = Field(..., description="Agent UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    intent_category: str = Field(
        ...,
        description="Canonical intent category (e.g. 'PAYMENT', 'REFUND', 'UNKNOWN')",
    )
    confidence: Decimal = Field(
        ..., ge=0, le=1, description="Classification confidence (0.00 to 1.00)"
    )
    reason: str = Field(..., description="Explainable classification reason")
    classified_at: datetime = Field(..., description="Classification timestamp")

    model_config = ConfigDict(from_attributes=True)


class StructuredIntentResponse(BaseModel):
    """Safe server-populated response combining extracted intent and classification."""

    agent_id: uuid.UUID = Field(..., description="Server-controlled Agent UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Server-controlled Tenant UUID")
    intent: StructuredIntent = Field(..., description="Extracted structured intent contract")
    classification: IntentClassificationResponse = Field(
        ..., description="Deterministic intent classification"
    )

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Phase 145 — Intent Storage Schemas
# ---------------------------------------------------------------------------


class AgentIntentCreateRequest(BaseModel):
    """Request payload for creating and storing agent intent."""

    request_text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language or structured request text to process and store",
    )
    context_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Optional non-sensitive context metadata"
    )

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class AgentIntentResponse(BaseModel):
    """Persisted safe metadata representation of an agent intent."""

    id: uuid.UUID = Field(..., description="Stored intent UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Agent UUIDv7")
    intent_type: str = Field(..., description="Canonical intent category")
    status: str = Field(..., description="Processing status ('stored', 'validated', 'normalized')")
    confidence: Decimal = Field(..., description="Bounded confidence score")
    raw_text: str | None = Field(default=None, description="Sanitized request text (NO secrets)")
    normalized_payload: dict[str, Any] = Field(
        default_factory=dict, description="Canonical normalized StructuredIntent JSONB payload"
    )
    validation_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Validation result metadata"
    )
    created_at: datetime = Field(..., description="Persistence timestamp")

    model_config = ConfigDict(from_attributes=True)


class AgentIntentListCursor(BaseModel):
    """Keyset pagination cursor for stored intent records."""

    next_created_at: datetime | None = Field(
        default=None, description="Keyset cursor: created_at timestamp of last item"
    )
    next_id: uuid.UUID | None = Field(
        default=None, description="Keyset cursor: intent ID of last item"
    )

    model_config = ConfigDict(extra="forbid")


class AgentIntentListResponse(BaseModel):
    """Paginated list of stored agent intents."""

    intents: list[AgentIntentResponse] = Field(
        default_factory=list, description="Page of stored intents"
    )
    count: int = Field(..., description="Number of items returned in current page")
    cursor: AgentIntentListCursor = Field(..., description="Keyset pagination cursor")

    model_config = ConfigDict(from_attributes=True)
