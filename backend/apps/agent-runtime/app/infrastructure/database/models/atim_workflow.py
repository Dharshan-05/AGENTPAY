"""SQLAlchemy ORM Entities for ATIM Durable Workflow Orchestration (Phase 23 / Group 12)."""

from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, Index, Integer, PrimaryKeyConstraint, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.infrastructure.database.base import Base


class ATIMWorkflowInstance(Base):
    """Durable Workflow Instance Entity."""

    __tablename__ = "atim_workflow_instances"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_atim_workflow_instances"),
        Index("ix_atim_workflow_inst_tenant_state", "tenant_id", "state"),
        Index("ix_atim_workflow_inst_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    agent_id = Column(UUID(as_uuid=True), nullable=True)
    workflow_type = Column(String(64), nullable=False)
    state = Column(String(32), nullable=False, default="INITIATED")
    current_step_index = Column(Integer, nullable=False, default=0)
    total_steps = Column(Integer, nullable=False, default=1)
    correlation_id = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    signature = Column(String(128), nullable=True)


class ATIMWorkflowStepExecution(Base):
    """Workflow Step Execution History Entity."""

    __tablename__ = "atim_workflow_step_executions"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_atim_workflow_step_executions"),
        Index("ix_atim_workflow_step_unique", "workflow_id", "step_index", unique=True),
        Index("ix_atim_workflow_step_created_at", "started_at"),
    )

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    workflow_id = Column(UUID(as_uuid=True), nullable=False)
    step_index = Column(Integer, nullable=False)
    step_type = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default="COMPLETED")
    payload_hash = Column(String(64), nullable=False)
    input_params = Column(JSONB, nullable=False, default=dict)
    output_result = Column(JSONB, nullable=True)
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
