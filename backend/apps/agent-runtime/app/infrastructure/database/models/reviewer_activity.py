"""ReviewerActivity ORM model module for AGENTPAY (Phase 071)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.approval_decision import ApprovalDecision
    from app.infrastructure.database.models.approval_request import ApprovalRequest
    from app.infrastructure.database.models.review_queue import ReviewQueue
    from app.infrastructure.database.models.user import User


class ReviewerActivity(Base):
    """ReviewerActivity ORM entity representing immutable reviewer activity history in AGENTPAY."""

    __tablename__ = "reviewer_activity"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "activity_reference",
            name="uq_reviewer_activity_tenant_id_activity_reference",
        ),
        CheckConstraint(
            "activity_type IN ('review', 'approval', 'decision', 'comment', "
            "'assignment', 'escalation', 'claim')",
            name="activity_type",
        ),
        CheckConstraint(
            "activity_action IN ('assigned', 'viewed', 'opened', 'claimed', 'commented', "
            "'approved', 'rejected', 'escalated', 'reassigned', 'requested_information', "
            "'released', 'skipped', 'expired')",
            name="activity_action",
        ),
        Index("ix_reviewer_activity_tenant_id", "tenant_id"),
        Index("ix_reviewer_activity_reviewer_id", "reviewer_id"),
        Index("ix_reviewer_activity_review_queue_id", "review_queue_id"),
        Index("ix_reviewer_activity_approval_request_id", "approval_request_id"),
        Index("ix_reviewer_activity_approval_decision_id", "approval_decision_id"),
        Index("ix_reviewer_activity_activity_reference", "activity_reference"),
        Index("ix_reviewer_activity_activity_type", "activity_type"),
        Index("ix_reviewer_activity_activity_action", "activity_action"),
        Index("ix_reviewer_activity_request_id", "request_id"),
        Index("ix_reviewer_activity_actor_id", "actor_id"),
        Index("ix_reviewer_activity_occurred_at", "occurred_at"),
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

    # Reviewer Identity (FK -> users.id, ON DELETE RESTRICT)
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_reviewer_activity_reviewer_id_users",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # Workflow Context References (FKs -> ON DELETE RESTRICT)
    review_queue_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "review_queue.id",
            name="fk_reviewer_activity_review_queue_id_review_queue",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    approval_request_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "approval_requests.id",
            name="fk_reviewer_activity_approval_request_id_approval_requests",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    approval_decision_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "approval_decisions.id",
            name="fk_reviewer_activity_approval_decision_id_approval_decisions",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Activity Identity, Classification & Action
    activity_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    activity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="review",
    )
    activity_action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="viewed",
    )

    # Actor Tracking
    actor_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="user",
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Correlation & Non-secret Activity Payload
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    activity_payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )

    # Timestamps (APPEND-ONLY: NO updated_at or deleted_at)
    occurred_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    # ORM Relationships
    reviewer: Mapped["User"] = relationship("User")
    review_queue: Mapped[Optional["ReviewQueue"]] = relationship("ReviewQueue")
    approval_request: Mapped[Optional["ApprovalRequest"]] = relationship("ApprovalRequest")
    approval_decision: Mapped[Optional["ApprovalDecision"]] = relationship("ApprovalDecision")

    def __repr__(self) -> str:
        """Return safe string representation REDACTING activity_payload and secrets."""
        return (
            f"<ReviewerActivity id={self.id} tenant_id={self.tenant_id} "
            f"reviewer_id={self.reviewer_id} type='{self.activity_type}' "
            f"action='{self.activity_action}'>"
        )
