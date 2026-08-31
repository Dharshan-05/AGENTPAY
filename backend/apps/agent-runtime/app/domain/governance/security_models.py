"""ATIM Security Hardening, Audit Lock, and Release Audit Domain Models (Group 8)."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
import uuid

from pydantic import BaseModel, Field


class ThreatIntelSeverity(str, Enum):
    """Threat severity levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ThreatIntelCategory(str, Enum):
    """Threat attack categories."""

    PROMPT_INJECTION = "PROMPT_INJECTION"
    MEMORY_POISONING = "MEMORY_POISONING"
    CREDENTIAL_EXTRACTION = "CREDENTIAL_EXTRACTION"
    AUTHORIZATION_BYPASS = "AUTHORIZATION_BYPASS"


class ThreatIntelRecord(BaseModel):
    """Domain model for a detected threat intelligence event."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    category: ThreatIntelCategory
    severity: ThreatIntelSeverity
    threat_score: Decimal = Field(default=Decimal("0.9000"))
    details: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditSignatureRecord(BaseModel):
    """Domain model for a SHA-256 HMAC cryptographic audit signature record."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    request_id: uuid.UUID
    record_type: str  # e.g., "TELEMETRY", "GOVERNANCE_DECISION", "EXECUTION_PROPOSAL"
    payload_hash: str
    signature: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditVerificationResult(BaseModel):
    """Domain model for cryptographic audit signature verification result."""

    is_valid: bool
    status: str  # "VALID" or "TAMPER_DETECTED"
    request_id: uuid.UUID
    signature: str
    verified_at: datetime = Field(default_factory=datetime.utcnow)


class InvariantAuditStatus(BaseModel):
    """Audit status for a single security invariant."""

    invariant_id: str
    title: str
    is_compliant: bool
    details: str


class SystemAuditScorecard(BaseModel):
    """Scorecard report for 100% automated release engineering audit."""

    audit_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    status: str  # "PASSED" or "FAILED"
    total_invariants_checked: int
    compliant_invariants_count: int
    invariants: list[InvariantAuditStatus]
    tenant_isolation_verified: bool
    audit_lock_verified: bool
    verified_at: datetime = Field(default_factory=datetime.utcnow)
