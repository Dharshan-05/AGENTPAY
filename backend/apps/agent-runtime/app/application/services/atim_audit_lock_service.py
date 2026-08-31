"""ATIM Cryptographic Audit Lock & Forensic Signature Service (Phase 15 / Group 8)."""

import hashlib
import hmac
import json
import logging
import os
from typing import Any
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.governance.security_models import AuditSignatureRecord, AuditVerificationResult
from app.infrastructure.database.models.atim_audit_lock import ATIMAuditSignature

logger = logging.getLogger("agentpay.atim.audit_lock")

# System secret key for HMAC audit signing
ATIM_AUDIT_SIGNING_KEY = os.getenv("ATIM_AUDIT_SIGNING_KEY", "atim_default_secret_audit_lock_key_2026").encode("utf-8")


class ATIMAuditLockService:
    """Service producing SHA-256 HMAC cryptographic signatures over ATIM telemetry and decisions."""

    @staticmethod
    def _compute_payload_hash(payload: dict[str, Any]) -> str:
        """Compute deterministic SHA-256 hash of canonicalized JSON payload."""
        canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    @staticmethod
    def _compute_hmac_signature(payload_hash: str) -> str:
        """Compute SHA-256 HMAC signature from payload hash."""
        return hmac.new(ATIM_AUDIT_SIGNING_KEY, payload_hash.encode("utf-8"), hashlib.sha256).hexdigest()

    def generate_audit_signature(
        self,
        tenant_id: uuid.UUID,
        request_id: uuid.UUID,
        record_type: str,
        payload: dict[str, Any],
    ) -> AuditSignatureRecord:
        """Generate tamper-proof cryptographic audit signature record."""
        payload_hash = self._compute_payload_hash(payload)
        signature = self._compute_hmac_signature(payload_hash)

        record = AuditSignatureRecord(
            tenant_id=tenant_id,
            request_id=request_id,
            record_type=record_type,
            payload_hash=payload_hash,
            signature=signature,
        )
        logger.info("Generated cryptographic audit signature for Request %s (Tenant %s)", request_id, tenant_id)
        return record

    def verify_audit_signature(
        self,
        request_id: uuid.UUID,
        payload: dict[str, Any],
        expected_signature: str,
    ) -> AuditVerificationResult:
        """Verify authenticity and tamper-freedom of audit payload signature."""
        computed_hash = self._compute_payload_hash(payload)
        computed_signature = self._compute_hmac_signature(computed_hash)

        is_valid = hmac.compare_digest(computed_signature, expected_signature)
        status = "VALID" if is_valid else "TAMPER_DETECTED"

        if not is_valid:
            logger.error("TAMPER DETECTED for Request %s: Signature mismatch!", request_id)

        return AuditVerificationResult(
            is_valid=is_valid,
            status=status,
            request_id=request_id,
            signature=expected_signature,
        )

    async def persist_audit_signature(
        self,
        db: AsyncSession | Any,
        record: AuditSignatureRecord,
    ) -> None:
        """Persist audit signature entity to database."""
        entity = ATIMAuditSignature(
            id=record.id,
            tenant_id=record.tenant_id,
            request_id=record.request_id,
            record_type=record.record_type,
            payload_hash=record.payload_hash,
            signature=record.signature,
            created_at=record.created_at,
        )
        db.add(entity)
        await db.commit()
