"""SQLAlchemy ORM Entities for Cryptographic Audit Locks and Threat Intelligence (Group 8)."""

from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, Index, Numeric, PrimaryKeyConstraint, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database.base import Base


class ATIMAuditSignature(Base):
    """Immutable Cryptographic Audit Signature Entity."""

    __tablename__ = "atim_audit_signatures"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_atim_audit_signatures"),
        Index("ix_atim_audit_signatures_tenant_request", "tenant_id", "request_id"),
        Index("ix_atim_audit_signatures_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    request_id = Column(UUID(as_uuid=True), nullable=False)
    record_type = Column(String(64), nullable=False)
    payload_hash = Column(String(64), nullable=False)
    signature = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class ATIMThreatIntelLog(Base):
    """Threat Intelligence Log Entity."""

    __tablename__ = "atim_threat_intel_logs"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_atim_threat_intel_logs"),
        Index("ix_atim_threat_intel_logs_tenant_id", "tenant_id"),
        Index("ix_atim_threat_intel_logs_category", "category"),
        Index("ix_atim_threat_intel_logs_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    agent_id = Column(UUID(as_uuid=True), nullable=True)
    category = Column(String(64), nullable=False)
    severity = Column(String(32), nullable=False)
    threat_score = Column(Numeric(5, 4), nullable=False)
    details = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
