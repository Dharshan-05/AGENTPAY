"""Pydantic Transport Schemas for Agent Memory Architecture (Phase 153/154)."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.requests import StrictRequestModel


class MemoryType(StrEnum):
    """Canonical memory type categories (Phase 153/154/155)."""

    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    DECLARATIVE = "declarative"
    EPISODIC = "episodic"
    PROCEDURAL = "procedural"
    SEMANTIC = "semantic"


class MemoryStatus(StrEnum):
    """Memory lifecycle states (Phase 155)."""

    ACTIVE = "active"
    STALE = "stale"
    ARCHIVED = "archived"
    DELETED = "deleted"


class AgentMemoryCreateRequest(StrictRequestModel):
    """Request payload to create a new agent memory record (Phase 153).

    Rejects server-controlled identity fields (`tenant_id`, `agent_id`, `created_at`).
    """

    key: str = Field(..., max_length=255, description="Memory lookup key")
    value: dict[str, Any] = Field(..., description="Structured memory payload")
    namespace: str = Field(
        default="default", max_length=100, description="Logical memory namespace"
    )
    memory_type: MemoryType = Field(
        default=MemoryType.SHORT_TERM, description="Memory storage tier type"
    )
    session_id: uuid.UUID | None = Field(default=None, description="Optional active session UUID")
    task_id: uuid.UUID | None = Field(default=None, description="Optional active task UUID")
    importance: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Memory importance score (0.0 to 1.0)"
    )
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Memory confidence score (0.0 to 1.0)"
    )
    ttl_seconds: int | None = Field(
        default=None, ge=1, le=2592000, description="Optional TTL expiration in seconds"
    )


class AgentMemoryUpdateRequest(StrictRequestModel):
    """Request payload to update an existing agent memory record (Phase 153)."""

    value: dict[str, Any] | None = Field(default=None, description="Updated memory payload")
    importance: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Updated importance score"
    )
    confidence: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Updated confidence score"
    )
    ttl_seconds: int | None = Field(
        default=None, ge=1, le=2592000, description="Updated TTL expiration in seconds"
    )


class AgentMemoryResponse(BaseModel):
    """Response contract returning structured memory record representation (Phase 153/154)."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID = Field(..., description="Unique memory record UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Agent UUIDv7")
    session_id: uuid.UUID | None = Field(default=None, description="Session UUID if session-scoped")
    task_id: uuid.UUID | None = Field(default=None, description="Task UUID if task-scoped")
    memory_type: str = Field(..., description="Memory type tier ('short_term', 'long_term')")
    namespace: str = Field(..., description="Logical memory namespace")
    key: str = Field(..., description="Memory key")
    value: dict[str, Any] = Field(..., description="Memory payload")
    importance: float = Field(..., description="Importance weight score")
    confidence: float = Field(..., description="Confidence weight score")
    version: int = Field(..., description="Record version counter")
    expires_at: datetime | None = Field(default=None, description="Expiration timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ShortTermMemorySetRequest(StrictRequestModel):
    """Request contract for setting session/task working memory variable (Phase 154)."""

    key: str = Field(..., max_length=255, description="Working memory key")
    value: dict[str, Any] = Field(..., description="Working memory variable value")
    task_id: uuid.UUID | None = Field(default=None, description="Optional task-scoped context UUID")
    ttl_seconds: int | None = Field(
        default=3600, ge=1, le=86400, description="Working memory TTL in seconds (default 1 hour)"
    )


class ShortTermMemoryListResponse(BaseModel):
    """Response model for short-term working memory list operations (Phase 154)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Agent UUIDv7")
    session_id: uuid.UUID | None = Field(default=None, description="Active session UUID")
    task_id: uuid.UUID | None = Field(default=None, description="Active task UUID")
    total_keys: int = Field(..., description="Count of active working memory variables")
    memories: list[AgentMemoryResponse] = Field(
        default_factory=list, description="Working memory records"
    )


class MemoryRecallWeights(BaseModel):
    """Configurable weights for multi-factor memory recall ranking (Phase 155)."""

    model_config = ConfigDict(extra="forbid")

    importance_weight: float = Field(default=0.35, ge=0.0, le=1.0)
    confidence_weight: float = Field(default=0.20, ge=0.0, le=1.0)
    recency_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    decay_weight: float = Field(default=0.20, ge=0.0, le=1.0)


class AgentMemoryRecallRequest(StrictRequestModel):
    """Request contract for memory recall operations (Phase 155)."""

    query: str | None = Field(
        default=None, max_length=500, description="Optional search query or topic"
    )  # noqa: E501
    namespace: str | None = Field(default=None, max_length=100, description="Filter by namespace")
    memory_types: list[str] | None = Field(default=None, description="Filter by memory types")
    min_relevance: float = Field(
        default=0.1, ge=0.0, le=1.0, description="Minimum relevance threshold"
    )  # noqa: E501
    top_k: int = Field(default=10, ge=1, le=100, description="Top-K records to return")
    weights: MemoryRecallWeights | None = Field(
        default=None, description="Optional scoring weights"
    )  # noqa: E501


class AgentMemoryRecallItem(BaseModel):
    """Single recalled memory item with relevance score (Phase 155)."""

    model_config = ConfigDict(extra="forbid")

    memory: AgentMemoryResponse = Field(..., description="Recalled memory record")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Calculated relevance score")


class AgentMemoryRecallResponse(BaseModel):
    """Response contract for memory recall operations (Phase 155)."""

    model_config = ConfigDict(extra="forbid")

    query: str | None = Field(default=None, description="Original search query")
    total_recalled: int = Field(..., description="Number of memories recalled")
    results: list[AgentMemoryRecallItem] = Field(
        default_factory=list, description="Recalled memory results"
    )  # noqa: E501
