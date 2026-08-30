"""PaymentIdempotencyKey ORM model module for AGENTPAY (Phase 067)."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class PaymentIdempotencyKey(Base):
    """PaymentIdempotencyKey ORM entity representing idempotency protection in AGENTPAY."""

    __tablename__ = "payment_idempotency_keys"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_payment_idempotency_keys_tenant_key",
        ),
        CheckConstraint(
            "operation_type IN ('create_order', 'authorize', 'capture', "
            "'refund', 'cancel', 'payment', 'retry', 'webhook')",
            name="operation_type",
        ),
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed', 'expired', 'conflict')",
            name="status",
        ),
        Index("ix_payment_idempotency_keys_tenant_id", "tenant_id"),
        Index("ix_payment_idempotency_keys_idempotency_key", "idempotency_key"),
        Index("ix_payment_idempotency_keys_operation_type", "operation_type"),
        Index("ix_payment_idempotency_keys_request_id", "request_id"),
        Index("ix_payment_idempotency_keys_status", "status"),
        Index("ix_payment_idempotency_keys_resource_id", "resource_id"),
        Index("ix_payment_idempotency_keys_expires_at", "expires_at"),
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

    # Idempotency Key & Operation Identity
    idempotency_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    operation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Correlation Context & Non-secret Fingerprint
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    resource_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    resource_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    request_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    # Status & Response Payload (NO SECRETS)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )
    response_code: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    response_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )

    # Timestamps
    first_seen_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
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

    def __repr__(self) -> str:
        """Return safe string representation REDACTING request_hash and response_metadata."""
        return (
            f"<PaymentIdempotencyKey id={self.id} tenant_id={self.tenant_id} "
            f"op='{self.operation_type}' status='{self.status}'>"
        )
