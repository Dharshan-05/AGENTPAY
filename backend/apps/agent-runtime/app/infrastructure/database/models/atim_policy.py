"""SQLAlchemy ORM Entities for ATIM Policy Governance and Quota Usage (Group 9)."""

from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, Index, Integer, Numeric, PrimaryKeyConstraint, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.infrastructure.database.base import Base


class ATIMGovernancePolicy(Base):
    """Immutable Governance Policy Entity."""

    __tablename__ = "atim_governance_policies"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_atim_governance_policies"),
        Index("ix_atim_gov_policies_tenant_type_version", "tenant_id", "policy_type", "version", unique=True),
        Index("ix_atim_gov_policies_status", "status"),
        Index("ix_atim_gov_policies_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    policy_type = Column(String(64), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    status = Column(String(32), nullable=False, default="DRAFT")
    configuration = Column(JSONB, nullable=False, default=dict)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    retired_at = Column(DateTime(timezone=True), nullable=True)
    reason = Column(Text, nullable=False, default="Initial draft creation")
    previous_version_id = Column(UUID(as_uuid=True), nullable=True)
    signature = Column(String(128), nullable=True)


class ATIMQuotaUsage(Base):
    """Tenant and Agent Quota Consumption Entity."""

    __tablename__ = "atim_quota_usages"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_atim_quota_usages"),
        Index("ix_atim_quota_usages_tenant_agent", "tenant_id", "agent_id"),
        Index("ix_atim_quota_usages_updated_at", "updated_at"),
    )

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    agent_id = Column(UUID(as_uuid=True), nullable=True)
    current_daily_requests = Column(Integer, nullable=False, default=0)
    current_daily_tokens = Column(Integer, nullable=False, default=0)
    current_daily_cost_usd = Column(Numeric(18, 6), nullable=False, default=0.0)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
