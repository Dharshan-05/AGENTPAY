"""SQLAlchemy ORM Entity for Cryptographic Compliance Evidence (Group 10)."""

from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, Index, PrimaryKeyConstraint, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.infrastructure.database.base import Base


class ATIMComplianceEvidence(Base):
    """Immutable Append-Only Compliance Evidence Entity."""

    __tablename__ = "atim_compliance_evidence"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_atim_compliance_evidence"),
        Index("ix_atim_comp_evidence_tenant_cat", "tenant_id", "category"),
        Index("ix_atim_comp_evidence_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    agent_id = Column(UUID(as_uuid=True), nullable=True)
    actor_id = Column(UUID(as_uuid=True), nullable=False)
    category = Column(String(64), nullable=False)
    correlation_id = Column(String(64), nullable=False)
    decision_precedence = Column(String(128), nullable=False)
    details = Column(JSONB, nullable=False, default=dict)
    signature = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
