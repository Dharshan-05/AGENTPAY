"""ATIM Governance Policy, Rate Limiting, Quotas, and Abuse Domain Models (Group 9)."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
import uuid

from pydantic import BaseModel, Field


class GovernancePolicyType(str, Enum):
    """Supported governance policy categories."""

    ATIM_SECURITY_POLICY = "ATIM_SECURITY_POLICY"
    ATIM_MODEL_ROUTING_POLICY = "ATIM_MODEL_ROUTING_POLICY"
    ATIM_RISK_POLICY = "ATIM_RISK_POLICY"
    ATIM_CONTEXT_POLICY = "ATIM_CONTEXT_POLICY"
    ATIM_RATE_LIMIT_POLICY = "ATIM_RATE_LIMIT_POLICY"
    ATIM_QUOTA_POLICY = "ATIM_QUOTA_POLICY"
    ATIM_PROVIDER_POLICY = "ATIM_PROVIDER_POLICY"
    ATIM_OBSERVABILITY_POLICY = "ATIM_OBSERVABILITY_POLICY"


class GovernancePolicyStatus(str, Enum):
    """Supported governance policy lifecycle states."""

    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    RETIRED = "RETIRED"
    REJECTED = "REJECTED"


class GovernancePolicyRecord(BaseModel):
    """Domain model representing a strongly typed governance policy."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    policy_type: GovernancePolicyType
    version: int = 1
    status: GovernancePolicyStatus = GovernancePolicyStatus.DRAFT
    configuration: dict[str, Any] = Field(default_factory=dict)
    created_by: uuid.UUID
    approved_by: Optional[uuid.UUID] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    retired_at: Optional[datetime] = None
    reason: str = "Initial draft creation"
    previous_version_id: Optional[uuid.UUID] = None
    signature: Optional[str] = None


class RateLimitAlgorithm(str, Enum):
    """Supported rate limit algorithms."""

    SLIDING_WINDOW = "SLIDING_WINDOW"
    TOKEN_BUCKET = "TOKEN_BUCKET"
    FIXED_WINDOW = "FIXED_WINDOW"


class RateLimitRecord(BaseModel):
    """Domain model representing a rate limit check result."""

    allowed: bool
    tenant_id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    limit: int
    remaining: int
    retry_after_seconds: int = 0
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.SLIDING_WINDOW


class QuotaRecord(BaseModel):
    """Domain model for tenant and agent quota consumption."""

    tenant_id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    max_requests_per_minute: int = 120
    max_requests_per_day: int = 10000
    max_tokens_per_day: int = 1000000
    max_cost_per_day_usd: Decimal = Field(default=Decimal("50.000000"))
    current_daily_requests: int = 0
    current_daily_tokens: int = 0
    current_daily_cost_usd: Decimal = Field(default=Decimal("0.000000"))


class AbuseSeverity(str, Enum):
    """Abuse severity levels."""

    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AbuseAction(str, Enum):
    """Deterministic abuse escalation actions."""

    ALLOW = "ALLOW"
    THROTTLE = "THROTTLE"
    TEMPORARY_BLOCK = "TEMPORARY_BLOCK"
    REQUIRE_REAUTH = "REQUIRE_REAUTH"
    REQUIRE_HITL = "REQUIRE_HITL"
    TENANT_REVIEW = "TENANT_REVIEW"
    PERMANENT_SECURITY_BLOCK = "PERMANENT_SECURITY_BLOCK"


class AbuseEventRecord(BaseModel):
    """Domain model representing a detected abuse event."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    abuse_type: str  # e.g., "REPEATED_INJECTION", "QUOTA_EXHAUSTION"
    severity: AbuseSeverity
    escalation_action: AbuseAction
    details: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
