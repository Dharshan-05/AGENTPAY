"""Production Approval Audit Subsystem (Phase 308)."""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import uuid
from datetime import UTC, datetime

from app.schemas.approval_audit import (
    ApprovalAuditActorType,
    ApprovalAuditEvent,
    ApprovalAuditEventType,
    ApprovalAuditQueryResult,
)
from app.schemas.approval_request import ApprovalRequestStatus

logger = logging.getLogger("agentpay.payment.approval.audit")

FORBIDDEN_METADATA_KEYS = {
    "key_secret",
    "webhook_secret",
    "authorization",
    "authorization_header",
    "bearer",
    "token",
    "password",
    "secret",
    "api_key",
}


class ApprovalAuditError(Exception):
    """Domain exception raised when an audit operation fails."""

    def __init__(self, message: str, error_code: str = "APPROVAL_AUDIT_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ApprovalAuditService:
    """Production Approval Audit Subsystem (Phase 308).

    Primary responsibility: Provide append-only, tamper-evident evidence recording
    for all payment approval lifecycle events.

    CRITICAL SECURITY & EXECUTION BOUNDARIES:
    - Immutable event logging with SHA-256 fingerprint tamper detection.
    - Append-only semantics: NO update or delete routines exposed.
    - Enforces tenant isolation on query endpoints.
    - Excludes secrets, credentials, or provider tokens from audit payloads.
    - Observational only: MUST NOT mutate approval request state or payment state.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._store_by_id: dict[uuid.UUID, ApprovalAuditEvent] = {}
        self._store_by_request: dict[tuple[uuid.UUID, uuid.UUID], list[ApprovalAuditEvent]] = {}

    def record_event(
        self,
        tenant_id: uuid.UUID,
        approval_request_id: uuid.UUID,
        transaction_id: str,
        agent_id: uuid.UUID,
        event_type: ApprovalAuditEventType,
        actor_type: ApprovalAuditActorType,
        approval_fingerprint: str,
        actor_id: uuid.UUID | None = None,
        previous_status: ApprovalRequestStatus | None = None,
        resulting_status: ApprovalRequestStatus | None = None,
        authorization_id: uuid.UUID | None = None,
        authorization_fingerprint: str | None = None,
        timestamp_utc: datetime | None = None,
        metadata: dict[str, str] | None = None,
    ) -> ApprovalAuditEvent:
        """Record an immutable, tamper-evident audit event (Phase 308)."""
        ts = timestamp_utc or datetime.now(UTC)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=UTC)

        safe_metadata = self._sanitize_metadata(metadata or {})

        # Compute SHA-256 Tamper-Evident Fingerprint
        event_fp = self._calculate_event_fingerprint(
            tenant_id=tenant_id,
            approval_request_id=approval_request_id,
            transaction_id=transaction_id,
            agent_id=agent_id,
            event_type=event_type,
            actor_type=actor_type,
            actor_id=actor_id,
            previous_status=previous_status,
            resulting_status=resulting_status,
            approval_fingerprint=approval_fingerprint,
            timestamp_utc=ts,
        )

        event = ApprovalAuditEvent(
            tenant_id=tenant_id,
            approval_request_id=approval_request_id,
            transaction_id=transaction_id,
            agent_id=agent_id,
            event_type=event_type,
            actor_type=actor_type,
            actor_id=actor_id,
            previous_status=previous_status,
            resulting_status=resulting_status,
            authorization_id=authorization_id,
            authorization_fingerprint=authorization_fingerprint,
            approval_fingerprint=approval_fingerprint,
            timestamp_utc=ts,
            event_fingerprint=event_fp,
            metadata=safe_metadata,
        )

        with self._lock:
            self._store_by_id[event.audit_event_id] = event
            key = (tenant_id, approval_request_id)
            if key not in self._store_by_request:
                self._store_by_request[key] = []
            self._store_by_request[key].append(event)

        logger.info(
            "ApprovalAuditService recorded event '%s' for req=%s (tenant=%s, fp=%s)",
            event_type.value,
            approval_request_id,
            tenant_id,
            event_fp,
        )

        return event

    def verify_audit_event_integrity(self, event: ApprovalAuditEvent) -> bool:
        """Verify whether an audit event's SHA-256 fingerprint matches computed hash."""
        expected_fp = self._calculate_event_fingerprint(
            tenant_id=event.tenant_id,
            approval_request_id=event.approval_request_id,
            transaction_id=event.transaction_id,
            agent_id=event.agent_id,
            event_type=event.event_type,
            actor_type=event.actor_type,
            actor_id=event.actor_id,
            previous_status=event.previous_status,
            resulting_status=event.resulting_status,
            approval_fingerprint=event.approval_fingerprint,
            timestamp_utc=event.timestamp_utc,
        )
        return event.event_fingerprint == expected_fp

    def get_audit_events_for_request(
        self, tenant_id: uuid.UUID, approval_request_id: uuid.UUID
    ) -> ApprovalAuditQueryResult:
        """Retrieve audit history for an approval request enforcing tenant isolation."""
        with self._lock:
            key = (tenant_id, approval_request_id)
            events = list(self._store_by_request.get(key, []))

        all_verified = all(self.verify_audit_event_integrity(e) for e in events)

        return ApprovalAuditQueryResult(
            tenant_id=tenant_id,
            approval_request_id=approval_request_id,
            total_events=len(events),
            events=events,
            all_events_verified=all_verified,
        )

    def _sanitize_metadata(self, metadata: dict[str, str]) -> dict[str, str]:
        """Strip or reject sensitive credentials from metadata payload."""
        cleaned: dict[str, str] = {}
        for k, v in metadata.items():
            if k.lower() in FORBIDDEN_METADATA_KEYS:
                logger.warning("Stripped forbidden secret key '%s' from audit metadata", k)
                continue
            cleaned[k] = str(v)
        return cleaned

    def _calculate_event_fingerprint(
        self,
        tenant_id: uuid.UUID,
        approval_request_id: uuid.UUID,
        transaction_id: str,
        agent_id: uuid.UUID,
        event_type: ApprovalAuditEventType,
        actor_type: ApprovalAuditActorType,
        actor_id: uuid.UUID | None,
        previous_status: ApprovalRequestStatus | None,
        resulting_status: ApprovalRequestStatus | None,
        approval_fingerprint: str,
        timestamp_utc: datetime,
    ) -> str:
        """Compute canonical SHA-256 fingerprint over audit event fields."""
        payload = {
            "tenant_id": str(tenant_id),
            "approval_request_id": str(approval_request_id),
            "transaction_id": transaction_id,
            "agent_id": str(agent_id),
            "event_type": event_type.value,
            "actor_type": actor_type.value,
            "actor_id": str(actor_id) if actor_id else "",
            "previous_status": previous_status.value if previous_status else "",
            "resulting_status": resulting_status.value if resulting_status else "",
            "approval_fingerprint": approval_fingerprint,
            "timestamp_utc": timestamp_utc.isoformat(),
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
