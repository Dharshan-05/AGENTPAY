"""Pydantic Transport & Domain Schemas for Policy Priority System (Phase 196)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class PolicyPriorityValidationRequest(BaseModel):
    """Payload contract for policy priority validation (Phase 196)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    policy_id: uuid.UUID = Field(..., description="Target SecurityPolicy UUID")
    priority: int = Field(..., description="Proposed policy priority integer")


class PolicyPriorityValidationResult(BaseModel):
    """Structured outcome of policy priority validation (Phase 196)."""

    model_config = ConfigDict(extra="forbid")

    is_valid: bool = Field(..., description="True if priority integer is within valid bounds")
    priority: int = Field(..., description="Validated priority integer")
    reason_code: str = Field(..., description="Structured reason code identifier")
    explanation: str = Field(..., description="Human-readable decision explanation")
    validated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Validation completion timestamp"
    )
