"""ATIM Security Context, Permissions, Compliance Evidence & Forensic Domain Models (Group 10)."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid

from pydantic import BaseModel, Field


class SecurityPermission(str, Enum):
    """Fine-grained administrative & security permissions for ATIM."""

    ATIM_POLICY_READ = "ATIM_POLICY_READ"
    ATIM_POLICY_CREATE = "ATIM_POLICY_CREATE"
    ATIM_POLICY_SUBMIT = "ATIM_POLICY_SUBMIT"
    ATIM_POLICY_APPROVE = "ATIM_POLICY_APPROVE"
    ATIM_POLICY_ACTIVATE = "ATIM_POLICY_ACTIVATE"
    ATIM_POLICY_SUSPEND = "ATIM_POLICY_SUSPEND"
    ATIM_POLICY_RETIRE = "ATIM_POLICY_RETIRE"
    ATIM_POLICY_AUDIT = "ATIM_POLICY_AUDIT"
    ATIM_SYSTEM_ADMIN = "ATIM_SYSTEM_ADMIN"


class ATIMSecurityContext(BaseModel):
    """Authenticated principal security context."""

    user_id: uuid.UUID
    tenant_id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    permissions: list[SecurityPermission] = Field(default_factory=list)
    authenticated_at: datetime = Field(default_factory=datetime.utcnow)


class ComplianceEventCategory(str, Enum):
    """Supported compliance event categories."""

    AUTH_FAILURE = "AUTH_FAILURE"
    AUTHORIZATION_DENIAL = "AUTHORIZATION_DENIAL"
    CROSS_TENANT_ATTEMPT = "CROSS_TENANT_ATTEMPT"
    POLICY_TRANSITION = "POLICY_TRANSITION"
    SECURITY_BLOCK = "SECURITY_BLOCK"
    RATE_LIMIT_VIOLATION = "RATE_LIMIT_VIOLATION"
    QUOTA_VIOLATION = "QUOTA_VIOLATION"
    ABUSE_ESCALATION = "ABUSE_ESCALATION"
    EXECUTION_PROPOSAL = "EXECUTION_PROPOSAL"


class ComplianceEvidenceRecord(BaseModel):
    """Domain model representing an append-only cryptographic compliance evidence entry."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    actor_id: uuid.UUID
    category: ComplianceEventCategory
    correlation_id: str
    decision_precedence: str = "SECURITY BLOCK > PLAN INVALID > AGENTGUARD DENY > FRAUDGUARD BLOCK > HITL REQUIRED > ALLOW"
    details: dict[str, Any] = Field(default_factory=dict)
    signature: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ForensicEvidenceSummary(BaseModel):
    """Summary representation for forensic evidence audits."""

    tenant_id: uuid.UUID
    total_evidence_records: int
    categories_breakdown: dict[str, int]
    integrity_verified: bool
    oldest_record_time: Optional[datetime] = None
    newest_record_time: Optional[datetime] = None
