"""AttackSimulation ORM model module for AGENTPAY (Phase 074)."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.user import User


class AttackSimulation(Base):
    """AttackSimulation ORM entity representing controlled security testing in AGENTPAY."""

    __tablename__ = "attack_simulations"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "simulation_reference",
            name="uq_attack_simulations_tenant_id_simulation_reference",
        ),
        CheckConstraint(
            "simulation_type IN ('authentication_bypass', 'authorization_bypass', "
            "'tenant_isolation', 'policy_bypass', 'fraud_detection', 'risk_manipulation', "
            "'replay', 'webhook_abuse', 'rate_limit', 'credential_abuse', 'payment_abuse')",
            name="simulation_type",
        ),
        CheckConstraint(
            "status IN ('planned', 'queued', 'running', 'completed', 'failed', 'cancelled')",
            name="status",
        ),
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="severity",
        ),
        CheckConstraint(
            "outcome IN ('passed', 'failed', 'blocked', 'detected', 'undetected', 'inconclusive')",
            name="outcome",
        ),
        CheckConstraint(
            "risk_score IS NULL OR (risk_score >= 0 AND risk_score <= 100)",
            name="risk_score_bounds",
        ),
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="confidence_score_bounds",
        ),
        Index("ix_attack_simulations_tenant_id", "tenant_id"),
        Index("ix_attack_simulations_simulation_reference", "simulation_reference"),
        Index("ix_attack_simulations_simulation_type", "simulation_type"),
        Index("ix_attack_simulations_status", "status"),
        Index("ix_attack_simulations_severity", "severity"),
        Index("ix_attack_simulations_outcome", "outcome"),
        Index("ix_attack_simulations_target_resource_id", "target_resource_id"),
        Index("ix_attack_simulations_initiated_by", "initiated_by"),
        Index("ix_attack_simulations_request_id", "request_id"),
        Index("ix_attack_simulations_started_at", "started_at"),
        Index("ix_attack_simulations_completed_at", "completed_at"),
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

    # Simulation Identity, Classification & Scenario
    simulation_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    simulation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="policy_bypass",
    )
    scenario: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="planned",
    )
    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="medium",
    )
    outcome: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="blocked",
    )

    # Target & Initiator Tracking
    target_component: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    target_resource_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    target_resource_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    initiated_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_attack_simulations_initiated_by_users",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Non-secret Simulation Parameters & Evidence Payloads
    simulation_parameters: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )
    expected_result: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    actual_result: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    findings: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    evidence_payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )

    # Scores (NUMERIC Decimal Precision)
    risk_score: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 4),
        nullable=True,
    )
    confidence_score: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 4),
        nullable=True,
    )

    # Timestamps (APPEND-ONLY: NO updated_at or deleted_at)
    started_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    # ORM Relationships
    initiator: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        """Return safe string representation REDACTING parameters, evidence, and secrets."""
        return (
            f"<AttackSimulation id={self.id} tenant_id={self.tenant_id} "
            f"type='{self.simulation_type}' status='{self.status}' "
            f"outcome='{self.outcome}'>"
        )
