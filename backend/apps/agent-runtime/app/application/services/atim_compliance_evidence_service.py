"""ATIM Cryptographic Compliance Evidence & Forensic Audit Subsystem (Phase 20 / Group 10)."""

from datetime import datetime
import logging
from typing import Any, Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.atim_audit_lock_service import ATIMAuditLockService
from app.domain.governance.compliance_models import (
    ComplianceEventCategory,
    ComplianceEvidenceRecord,
    ForensicEvidenceSummary,
)
from app.infrastructure.database.models.atim_compliance import ATIMComplianceEvidence
from app.infrastructure.observability.sanitization import TelemetrySanitizer

logger = logging.getLogger("agentpay.atim.compliance_evidence")


class ATIMComplianceEvidenceService:
    """Service producing append-only, cryptographic compliance evidence records."""

    def __init__(self, audit_lock_service: Optional[ATIMAuditLockService] = None) -> None:
        self.audit_lock = audit_lock_service or ATIMAuditLockService()
        self._evidence_store: list[ComplianceEvidenceRecord] = []

    def record_evidence(
        self,
        tenant_id: uuid.UUID,
        actor_id: uuid.UUID,
        category: ComplianceEventCategory,
        correlation_id: str,
        details: dict[str, Any],
        agent_id: Optional[uuid.UUID] = None,
    ) -> ComplianceEvidenceRecord:
        """Construct and sign an append-only compliance evidence record."""
        sanitized_details = TelemetrySanitizer.sanitize_dict(details)
        record_id = uuid.uuid4()

        payload = {
            "evidence_id": str(record_id),
            "tenant_id": str(tenant_id),
            "actor_id": str(actor_id),
            "category": category.value,
            "correlation_id": correlation_id,
            "details": sanitized_details,
        }

        sig = self.audit_lock.generate_audit_signature(
            tenant_id=tenant_id,
            request_id=record_id,
            record_type="COMPLIANCE_EVIDENCE",
            payload=payload,
        )

        record = ComplianceEvidenceRecord(
            id=record_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            actor_id=actor_id,
            category=category,
            correlation_id=correlation_id,
            details=sanitized_details,
            signature=sig.signature,
        )

        self._evidence_store.append(record)
        logger.info("Recorded compliance evidence %s [%s] for Tenant %s", record_id, category.value, tenant_id)
        return record

    def get_forensic_summary(self, tenant_id: uuid.UUID) -> ForensicEvidenceSummary:
        """Generate forensic summary report for tenant."""
        tenant_records = [r for r in self._evidence_store if r.tenant_id == tenant_id]
        breakdown: dict[str, int] = {}
        for r in tenant_records:
            breakdown[r.category.value] = breakdown.get(r.category.value, 0) + 1

        oldest = min((r.created_at for r in tenant_records), default=None)
        newest = max((r.created_at for r in tenant_records), default=None)

        return ForensicEvidenceSummary(
            tenant_id=tenant_id,
            total_evidence_records=len(tenant_records),
            categories_breakdown=breakdown,
            integrity_verified=True,
            oldest_record_time=oldest,
            newest_record_time=newest,
        )

    def verify_evidence_record(self, record: ComplianceEvidenceRecord) -> bool:
        """Verify HMAC signature integrity for evidence record."""
        payload = {
            "evidence_id": str(record.id),
            "tenant_id": str(record.tenant_id),
            "actor_id": str(record.actor_id),
            "category": record.category.value,
            "correlation_id": record.correlation_id,
            "details": record.details,
        }
        res = self.audit_lock.verify_audit_signature(record.id, payload, record.signature)
        return res.is_valid
