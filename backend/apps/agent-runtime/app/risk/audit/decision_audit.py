"""Decision Audit Event Engine (Phase 283)."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime

from app.schemas.risk_engine import (
    DecisionAuditEvent,
    FinalRiskDecisionResult,
    HardSecurityEvaluationResult,
)

logger = logging.getLogger("agentpay.risk.audit.decision")


class DecisionAuditEventBuilder:
    """Builder for constructing immutable, canonical DecisionAuditEvent instances (Phase 283)."""

    def _compute_audit_fingerprint(
        self,
        decision_id: str,
        evaluation_id: str,
        tenant_id: str,
        agent_id: str,
        transaction_id: str,
        decision: str,
        reason_code: str,
        decision_timestamp: datetime,
        prediction_timestamp: datetime,
        composite_risk_score: float,
        risk_band: str,
        policy_precedence: str,
        hard_security_status: str,
        cold_start: bool,
        unavailable_signal_types: list[str],
        source_fingerprints: list[str],
        weight_configuration_hash: str,
        threshold_configuration_hash: str,
        security_rule_configuration_hash: str,
        decision_fingerprint: str,
    ) -> str:
        """Compute canonical SHA-256 fingerprint of audit event payload."""
        payload = {
            "decision_id": decision_id,
            "evaluation_id": evaluation_id,
            "tenant_id": tenant_id,
            "agent_id": agent_id,
            "transaction_id": transaction_id,
            "decision": decision,
            "reason_code": reason_code,
            "decision_timestamp": decision_timestamp.isoformat(),
            "prediction_timestamp": prediction_timestamp.isoformat(),
            "composite_risk_score": composite_risk_score,
            "risk_band": risk_band,
            "policy_precedence": policy_precedence,
            "hard_security_status": hard_security_status,
            "cold_start": cold_start,
            "unavailable_signal_types": sorted(unavailable_signal_types),
            "source_fingerprints": sorted(source_fingerprints),
            "weight_configuration_hash": weight_configuration_hash,
            "threshold_configuration_hash": threshold_configuration_hash,
            "security_rule_configuration_hash": security_rule_configuration_hash,
            "decision_fingerprint": decision_fingerprint,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def build_audit_event(
        self,
        decision_result: FinalRiskDecisionResult,
        security_result: HardSecurityEvaluationResult | None = None,
        correlation_id: str | None = None,
        decision_timestamp: datetime | None = None,
    ) -> DecisionAuditEvent:
        """Build canonical immutable DecisionAuditEvent (Phase 283)."""
        dec_ts = decision_timestamp or decision_result.created_at
        sec_hash = security_result.configuration_hash if security_result else "h" * 64

        audit_fp = self._compute_audit_fingerprint(
            decision_id=str(decision_result.decision_id),
            evaluation_id=str(decision_result.evaluation_id),
            tenant_id=str(decision_result.tenant_id),
            agent_id=str(decision_result.agent_id),
            transaction_id=decision_result.transaction_id,
            decision=decision_result.decision.value,
            reason_code=decision_result.decision_reason,
            decision_timestamp=dec_ts,
            prediction_timestamp=decision_result.prediction_timestamp,
            composite_risk_score=decision_result.composite_risk_score,
            risk_band=decision_result.risk_band.value,
            policy_precedence=decision_result.policy_precedence,
            hard_security_status=decision_result.hard_security_status,
            cold_start=decision_result.cold_start,
            unavailable_signal_types=decision_result.unavailable_signal_types,
            source_fingerprints=decision_result.source_fingerprints,
            weight_configuration_hash=decision_result.weight_configuration_hash,
            threshold_configuration_hash=decision_result.threshold_configuration_hash,
            security_rule_configuration_hash=sec_hash,
            decision_fingerprint=decision_result.decision_fingerprint,
        )

        return DecisionAuditEvent(
            decision_id=decision_result.decision_id,
            evaluation_id=decision_result.evaluation_id,
            tenant_id=decision_result.tenant_id,
            agent_id=decision_result.agent_id,
            transaction_id=decision_result.transaction_id,
            decision=decision_result.decision,
            reason_code=decision_result.decision_reason,
            decision_timestamp=dec_ts,
            prediction_timestamp=decision_result.prediction_timestamp,
            composite_risk_score=decision_result.composite_risk_score,
            risk_band=decision_result.risk_band,
            policy_precedence=decision_result.policy_precedence,
            hard_security_status=decision_result.hard_security_status,
            cold_start=decision_result.cold_start,
            unavailable_signal_types=sorted(decision_result.unavailable_signal_types),
            source_fingerprints=sorted(decision_result.source_fingerprints),
            weight_configuration_hash=decision_result.weight_configuration_hash,
            threshold_configuration_hash=decision_result.threshold_configuration_hash,
            security_rule_configuration_hash=sec_hash,
            decision_fingerprint=decision_result.decision_fingerprint,
            audit_fingerprint=audit_fp,
            engine_version="1.0.0",
            schema_version="1.0.0",
            correlation_id=correlation_id,
        )


class DecisionAuditEventService:
    """Service managing append-only DecisionAuditEvent persistence and retrieval (Phase 283)."""

    def __init__(self, builder: DecisionAuditEventBuilder | None = None) -> None:
        self.builder = builder or DecisionAuditEventBuilder()
        self._events: list[DecisionAuditEvent] = []

    def record_decision_event(
        self,
        decision_result: FinalRiskDecisionResult,
        security_result: HardSecurityEvaluationResult | None = None,
        correlation_id: str | None = None,
    ) -> DecisionAuditEvent:
        """Record an append-only DecisionAuditEvent with idempotency protection (Phase 283)."""
        # Idempotency check: Return existing matching audit event if decision_id exists
        for existing in self._events:
            if existing.decision_id == decision_result.decision_id:
                if existing.decision_fingerprint == decision_result.decision_fingerprint:
                    logger.info(
                        "Duplicate decision audit recording requested for decision %s; returning existing audit event %s",  # noqa: E501
                        decision_result.decision_id,
                        existing.event_id,
                    )
                    return existing
                else:
                    raise ValueError(
                        f"Conflicting audit event for decision '{decision_result.decision_id}'! Fingerprints do not match."  # noqa: E501
                    )

        event = self.builder.build_audit_event(
            decision_result=decision_result,
            security_result=security_result,
            correlation_id=correlation_id,
        )
        self._events.append(event)
        logger.info(
            "Recorded decision audit event %s for decision %s (tx=%s)",
            event.event_id,
            event.decision_id,
            event.transaction_id,
        )
        return event

    def list_events(self) -> list[DecisionAuditEvent]:
        """Return immutable copy of recorded audit events."""
        return list(self._events)

    def get_event_by_id(
        self, tenant_id: uuid.UUID, decision_id: uuid.UUID
    ) -> DecisionAuditEvent | None:
        """Retrieve audit event by decision ID under strict tenant isolation."""
        for event in self._events:
            if event.tenant_id == tenant_id and event.decision_id == decision_id:
                return event
        return None

    def list_events_for_tenant(self, tenant_id: uuid.UUID) -> list[DecisionAuditEvent]:
        """Retrieve all audit events under strict tenant isolation."""
        return [e for e in self._events if e.tenant_id == tenant_id]
