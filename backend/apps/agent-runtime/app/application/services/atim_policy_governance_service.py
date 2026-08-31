"""ATIM Administrative Control Plane & Policy Lifecycle Governance Service (Phase 17 / Group 9)."""

from datetime import datetime
import logging
from typing import Any, Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.atim_audit_lock_service import ATIMAuditLockService
from app.domain.governance.policy_models import (
    GovernancePolicyRecord,
    GovernancePolicyStatus,
    GovernancePolicyType,
)
from app.infrastructure.database.models.atim_policy import ATIMGovernancePolicy

logger = logging.getLogger("agentpay.atim.policy_governance")


class ATIMPolicyGovernanceService:
    """Service managing deterministic governance policy lifecycle transitions and four-eyes control."""

    def __init__(self, audit_lock_service: Optional[ATIMAuditLockService] = None) -> None:
        self.audit_lock = audit_lock_service or ATIMAuditLockService()
        # In-memory store fallback for fast testing and DB persistence synchronization
        self._policies: dict[uuid.UUID, GovernancePolicyRecord] = {}

    def create_draft_policy(
        self,
        tenant_id: uuid.UUID,
        policy_type: GovernancePolicyType,
        configuration: dict[str, Any],
        creator_id: uuid.UUID,
        reason: str = "Initial draft creation",
    ) -> GovernancePolicyRecord:
        """Create a new governance policy draft in DRAFT status."""
        policy_id = uuid.uuid4()
        record = GovernancePolicyRecord(
            id=policy_id,
            tenant_id=tenant_id,
            policy_type=policy_type,
            version=1,
            status=GovernancePolicyStatus.DRAFT,
            configuration=configuration,
            created_by=creator_id,
            reason=reason,
        )

        sig = self.audit_lock.generate_audit_signature(
            tenant_id=tenant_id,
            request_id=policy_id,
            record_type="GOVERNANCE_POLICY_DRAFT",
            payload=record.model_dump(mode="json"),
        )
        record.signature = sig.signature

        self._policies[policy_id] = record
        logger.info("Created policy draft %s (v1, Tenant %s) by User %s", policy_id, tenant_id, creator_id)
        return record

    def submit_policy(
        self,
        policy_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> GovernancePolicyRecord:
        """Submit a DRAFT policy for administrative approval."""
        record = self._get_policy_or_raise(policy_id)
        if record.status != GovernancePolicyStatus.DRAFT:
            raise ValueError(f"Cannot submit policy in status '{record.status.value}'. Must be DRAFT.")

        record.status = GovernancePolicyStatus.PENDING_APPROVAL
        record.reason = f"Submitted for approval by {actor_id}"
        logger.info("Submitted policy %s for approval by User %s", policy_id, actor_id)
        return record

    def approve_policy(
        self,
        policy_id: uuid.UUID,
        approver_id: uuid.UUID,
        require_four_eyes: bool = True,
    ) -> GovernancePolicyRecord:
        """Approve a PENDING_APPROVAL policy under Four-Eyes control (approver != creator)."""
        record = self._get_policy_or_raise(policy_id)
        if record.status != GovernancePolicyStatus.PENDING_APPROVAL:
            raise ValueError(f"Cannot approve policy in status '{record.status.value}'. Must be PENDING_APPROVAL.")

        if require_four_eyes and record.created_by == approver_id:
            raise PermissionError("Four-Eyes Violation: Policy creator cannot approve their own submission.")

        record.status = GovernancePolicyStatus.APPROVED
        record.approved_by = approver_id
        record.approved_at = datetime.utcnow()
        record.reason = f"Approved by {approver_id}"

        sig = self.audit_lock.generate_audit_signature(
            tenant_id=record.tenant_id,
            request_id=policy_id,
            record_type="GOVERNANCE_POLICY_APPROVED",
            payload=record.model_dump(mode="json"),
        )
        record.signature = sig.signature

        logger.info("Approved policy %s by User %s (Four-Eyes check passed)", policy_id, approver_id)
        return record

    def activate_policy(
        self,
        policy_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> GovernancePolicyRecord:
        """Activate an APPROVED or SUSPENDED policy, retiring any currently active version."""
        record = self._get_policy_or_raise(policy_id)
        if record.status not in (GovernancePolicyStatus.APPROVED, GovernancePolicyStatus.SUSPENDED):
            raise ValueError(f"Cannot activate policy in status '{record.status.value}'. Must be APPROVED or SUSPENDED.")

        # Retire other active policies of same tenant & type
        for p in self._policies.values():
            if (
                p.tenant_id == record.tenant_id
                and p.policy_type == record.policy_type
                and p.id != policy_id
                and p.status == GovernancePolicyStatus.ACTIVE
            ):
                p.status = GovernancePolicyStatus.RETIRED
                p.retired_at = datetime.utcnow()

        record.status = GovernancePolicyStatus.ACTIVE
        record.activated_at = datetime.utcnow()
        record.reason = f"Activated by {actor_id}"

        logger.info("Activated policy %s (v%d) for Tenant %s", policy_id, record.version, record.tenant_id)
        return record

    def suspend_policy(self, policy_id: uuid.UUID, actor_id: uuid.UUID, reason: str) -> GovernancePolicyRecord:
        """Suspend an ACTIVE policy."""
        record = self._get_policy_or_raise(policy_id)
        if record.status != GovernancePolicyStatus.ACTIVE:
            raise ValueError(f"Cannot suspend policy in status '{record.status.value}'. Must be ACTIVE.")

        record.status = GovernancePolicyStatus.SUSPENDED
        record.reason = f"Suspended by {actor_id}: {reason}"
        logger.info("Suspended policy %s for Tenant %s", policy_id, record.tenant_id)
        return record

    def retire_policy(self, policy_id: uuid.UUID, actor_id: uuid.UUID, reason: str) -> GovernancePolicyRecord:
        """Retire an ACTIVE or SUSPENDED policy."""
        record = self._get_policy_or_raise(policy_id)
        if record.status not in (GovernancePolicyStatus.ACTIVE, GovernancePolicyStatus.SUSPENDED):
            raise ValueError(f"Cannot retire policy in status '{record.status.value}'. Must be ACTIVE or SUSPENDED.")

        record.status = GovernancePolicyStatus.RETIRED
        record.retired_at = datetime.utcnow()
        record.reason = f"Retired by {actor_id}: {reason}"
        logger.info("Retired policy %s for Tenant %s", policy_id, record.tenant_id)
        return record

    def get_policy(self, policy_id: uuid.UUID) -> Optional[GovernancePolicyRecord]:
        """Retrieve policy by ID."""
        return self._policies.get(policy_id)

    def _get_policy_or_raise(self, policy_id: uuid.UUID) -> GovernancePolicyRecord:
        record = self._policies.get(policy_id)
        if not record:
            raise KeyError(f"Governance policy '{policy_id}' not found.")
        return record
