"""Pydantic Transport Schemas for Agent Context Management (Phase 152)."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.requests import StrictRequestModel


class ContextScope(StrEnum):
    """Canonical context scopes in priority order (Phase 152)."""

    SYSTEM = "SYSTEM"
    AGENT_IDENTITY = "AGENT_IDENTITY"
    USER = "USER"
    CONVERSATION = "CONVERSATION"
    TASK = "TASK"
    TOOL = "TOOL"
    RUNTIME = "RUNTIME"


class ContextItem(BaseModel):
    """Individual unit of structured context (Phase 152)."""

    model_config = ConfigDict(extra="forbid")

    item_id: str = Field(..., description="Unique context item identifier")
    scope: ContextScope = Field(..., description="Context scope category")
    priority: int = Field(
        default=50, ge=1, le=100, description="Priority weight (1 to 100, higher is prioritized)"
    )
    content: str = Field(..., description="Context textual or structured representation")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Sanitized context metadata")
    estimated_tokens: int = Field(default=0, ge=0, description="Estimated token size")
    relevance_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Context relevance score"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Context item creation timestamp"
    )
    expires_at: datetime | None = Field(
        default=None, description="Context item expiration timestamp"
    )


class ContextBudget(BaseModel):
    """Context token and size limits specification (Phase 152)."""

    model_config = ConfigDict(extra="forbid")

    max_tokens: int = Field(
        default=4096, ge=256, le=128000, description="Maximum allowed token budget"
    )
    max_items: int = Field(
        default=100, ge=1, le=1000, description="Maximum allowed total context items"
    )
    preserve_scopes: list[ContextScope] = Field(
        default_factory=lambda: [ContextScope.SYSTEM, ContextScope.AGENT_IDENTITY],
        description="Scopes exempt from truncation when budget is exceeded",
    )


class ContextAssemblyRequest(StrictRequestModel):
    """Request contract for assembling deterministic agent context (Phase 152)."""

    session_id: uuid.UUID | None = Field(default=None, description="Optional active session UUID")
    task_id: uuid.UUID | None = Field(default=None, description="Optional active task UUID")
    user_prompt: str | None = Field(default=None, description="Current user input prompt")
    custom_items: list[ContextItem] = Field(
        default_factory=list, description="Custom supplied context items to include"
    )
    budget: ContextBudget = Field(
        default_factory=ContextBudget, description="Context token and size budget limits"
    )


class ContextAssemblyResponse(BaseModel):
    """Response contract returning assembled prioritized context representation (Phase 152)."""

    model_config = ConfigDict(extra="forbid")

    assembly_id: uuid.UUID = Field(..., description="Unique assembly execution UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Agent UUIDv7")
    session_id: uuid.UUID | None = Field(default=None, description="Session UUID")
    task_id: uuid.UUID | None = Field(default=None, description="Task UUID")
    total_tokens: int = Field(..., description="Assembled total token count")
    total_items: int = Field(..., description="Count of included context items")
    truncated_items_count: int = Field(
        default=0, description="Count of lower-priority items truncated due to budget"
    )
    items: list[ContextItem] = Field(
        default_factory=list, description="Ordered prioritized context items"
    )
    assembled_at: datetime = Field(..., description="Assembly completion timestamp")
