"""Pydantic schemas for LLM Request and Response metadata."""

from __future__ import annotations

import uuid
from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)


class LLMTokenUsage(BaseModel):
    """Token accounting metadata."""

    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)
    estimated_cost_usd: float = Field(default=0.0, ge=0.0)


class LLMRequest(BaseModel):
    """Normalized payload sent to LLM providers."""

    prompt: str = Field(description="User or augmented prompt content")
    system_prompt: str | None = Field(default=None, description="System instruction boundary")
    correlation_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID | None = Field(default=None)
    agent_id: uuid.UUID | None = Field(default=None)
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)
    max_tokens: int | None = Field(default=1024, ge=1)
    timeout_seconds: float = Field(default=10.0, ge=0.1)


class LLMResponse(BaseModel):
    """Raw text response metadata returned by LLM providers."""

    correlation_id: uuid.UUID
    provider: str
    model: str
    content: str
    latency_ms: float
    usage: LLMTokenUsage = Field(default_factory=LLMTokenUsage)
    finish_reason: str = Field(default="stop")
    validation_status: str = Field(default="RAW_TEXT")


class StructuredLLMResponse(BaseModel, Generic[T]):
    """Type-safe structured response wrapping a validated Pydantic model instance."""

    correlation_id: uuid.UUID
    provider: str
    model: str
    data: T
    raw_content: str
    latency_ms: float
    usage: LLMTokenUsage = Field(default_factory=LLMTokenUsage)
    retry_count: int = Field(default=0, ge=0)
    validation_status: str = Field(default="VALIDATED")
