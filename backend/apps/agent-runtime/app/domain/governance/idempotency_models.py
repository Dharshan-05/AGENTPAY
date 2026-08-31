"""ATIM Idempotency, Transactional Outbox, and Recovery Domain Models (Group 11)."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid

from pydantic import BaseModel, Field


class IdempotencyState(str, Enum):
    """Deterministic idempotency lifecycle states."""

    RECEIVED = "RECEIVED"
    PROCESSING = "PROCESSING"
    AUTHORIZED = "AUTHORIZED"
    EXECUTING = "EXECUTING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"


class IdempotencyRecord(BaseModel):
    """Domain model representing an idempotency key execution record."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    operation: str
    idempotency_key: str
    payload_hash: str
    state: IdempotencyState = IdempotencyState.PROCESSING
    response_code: Optional[int] = None
    response_body: Optional[dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime


class OutboxEventRecord(BaseModel):
    """Domain model representing a transactional outbox event."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    processed: bool = False
    retry_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None


class RecoveryJobRecord(BaseModel):
    """Summary model for crash recovery job execution."""

    job_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    reconciled_count: int = 0
    failed_count: int = 0
    status: str = "COMPLETED"
    executed_at: datetime = Field(default_factory=datetime.utcnow)
