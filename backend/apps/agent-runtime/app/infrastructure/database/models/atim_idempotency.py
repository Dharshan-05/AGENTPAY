"""SQLAlchemy ORM Entities for ATIM Idempotency and Transactional Outbox (Group 11)."""

from datetime import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, PrimaryKeyConstraint, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.infrastructure.database.base import Base


class ATIMIdempotencyRecord(Base):
    """Immutable & Authoritative Idempotency Record Entity."""

    __tablename__ = "atim_idempotency_records"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_atim_idempotency_records"),
        Index("ix_atim_idempotency_scoped_key", "tenant_id", "agent_id", "operation", "idempotency_key", unique=True),
        Index("ix_atim_idempotency_expires_at", "expires_at"),
    )

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    agent_id = Column(UUID(as_uuid=True), nullable=True)
    operation = Column(String(64), nullable=False)
    idempotency_key = Column(String(128), nullable=False)
    payload_hash = Column(String(64), nullable=False)
    state = Column(String(32), nullable=False, default="PROCESSING")
    response_code = Column(Integer, nullable=True)
    response_body = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)


class ATIMTransactionalOutbox(Base):
    """Transactional Outbox Entity for Atomic Compliance Event Dispatch."""

    __tablename__ = "atim_transactional_outbox"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_atim_transactional_outbox"),
        Index("ix_atim_outbox_tenant_processed", "tenant_id", "processed"),
        Index("ix_atim_outbox_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    event_type = Column(String(64), nullable=False)
    payload = Column(JSONB, nullable=False, default=dict)
    processed = Column(Boolean, nullable=False, default=False)
    retry_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
