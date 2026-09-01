"""ApprovalDecision ORM model module for AGENTPAY (Phase 070)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.approval_request import ApprovalRequest
    from app.infrastructure.database.models.user import User


class ApprovalDecision(Base):
    """ApprovalDecision ORM entity representing individual reviewer decision actions in AGENTPAY."""

    __tablename__ = "approval_decisions"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "decision_reference",
            name="uq_approval_decisions_tenant_id_decision_reference",
        ),
        CheckConstraint(
            "decision IN ('approved', 'rejected', 'abstained', 'cancelled')",
            name="decision",
        ),
        Index("ix_approval_decisions_tenant_id", "tenant_id"),
        Index("ix_approval_decisions_approval_request_id", "approval_request_id"),
        Index("ix_approval_decisions_reviewer_id", "reviewer_id"),
        Index("ix_approval_decisions_decision_reference", "decision_reference"),
        Index("ix_approval_decisions_decision", "decision"),
        Index("ix_approval_decisions_request_id", "request_id"),
        Index("ix_approval_decisions_decided_at", "decided_at"),
    )

    # Primary Key (UUIDv7)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Multi-tenancy isolation key
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # Parent Approval Request (FK -> approval_requests.id, ON DELETE RESTRICT)
    approval_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "approval_requests.id",
            name="fk_short_14556869",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # Reviewer Identity (FK -> users.id, ON DELETE RESTRICT)
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_approval_decisions_reviewer_id_users",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # Decision Identity & Action
    decision_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    decision: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Correlation & Non-secret Context Metadata
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    decision_context: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )

    # Timestamps
    decided_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ORM Relationships
    approval_request: Mapped["ApprovalRequest"] = relationship("ApprovalRequest")
    reviewer: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        """Return safe string representation REDACTING decision_context and secrets."""
        return (
            f"<ApprovalDecision id={self.id} tenant_id={self.tenant_id} "
            f"request_id={self.approval_request_id} reviewer_id={self.reviewer_id} "
            f"decision='{self.decision}'>"
        )
