"""Unit & Security Tests for Phase 283 — Decision Audit Subsystem."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.risk.audit.decision_audit import DecisionAuditEventBuilder, DecisionAuditEventService
from app.schemas.risk_engine import (
    DecisionAuditEvent,
    FinalRiskDecision,
    FinalRiskDecisionResult,
    RiskEvaluationContext,
    RiskThresholdBand,
)


def _make_context(
    t_id: uuid.UUID | None = None,
    a_id: uuid.UUID | None = None,
    tx_id: str = "tx_audit_01",
) -> RiskEvaluationContext:
    return RiskEvaluationContext(
        tenant_id=t_id or uuid.uuid4(),
        agent_id=a_id or uuid.uuid4(),
        transaction_id=tx_id,
        prediction_timestamp=datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC),
    )


def _make_decision_result(
    ctx: RiskEvaluationContext,
    decision: FinalRiskDecision = FinalRiskDecision.ALLOW,
    score: float = 10.0,
    band: RiskThresholdBand = RiskThresholdBand.LOW_RISK_BAND,
    reason: str = "LOW_RISK_ALLOW_CLEAN",
    fp: str = "d" * 64,
    created_at: datetime | None = None,
) -> FinalRiskDecisionResult:
    return FinalRiskDecisionResult(
        evaluation_id=ctx.evaluation_id,
        decision_id=uuid.uuid4(),
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        decision=decision,
        decision_reason=reason,
        composite_risk_score=score,
        risk_band=band,
        policy_precedence=decision.value,
        hard_security_status="PASSED",
        triggered_rule_ids=[],
        review_reasons=[],
        block_reasons=[],
        available_signal_types=["FRAUDGUARD"],
        unavailable_signal_types=[],
        cold_start=False,
        policy_authoritative=True,
        threshold_configuration_version="1.0.0",
        threshold_configuration_hash="t" * 64,
        weight_configuration_version="1.0.0",
        weight_configuration_hash="w" * 64,
        source_fingerprints=["s1" * 32],
        calculation_fingerprint="c" * 64,
        decision_fingerprint=fp,
        created_at=created_at or datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC),
    )


def test_01_audit_event_creation_and_field_preservation() -> None:
    """1. Test audit event creation and required field preservation."""
    ctx = _make_context()
    dec_res = _make_decision_result(ctx)
    builder = DecisionAuditEventBuilder()

    event = builder.build_audit_event(dec_res)

    assert isinstance(event, DecisionAuditEvent)
    assert event.decision_id == dec_res.decision_id
    assert event.evaluation_id == dec_res.evaluation_id
    assert event.tenant_id == ctx.tenant_id
    assert event.agent_id == ctx.agent_id
    assert event.transaction_id == ctx.transaction_id
    assert event.decision == FinalRiskDecision.ALLOW
    assert event.reason_code == "LOW_RISK_ALLOW_CLEAN"
    assert event.composite_risk_score == 10.0
    assert event.risk_band == RiskThresholdBand.LOW_RISK_BAND
    assert event.decision_fingerprint == dec_res.decision_fingerprint
    assert len(event.audit_fingerprint) == 64


def test_02_deterministic_audit_fingerprint() -> None:
    """2. Test identical audit input produces identical SHA-256 fingerprint."""
    ctx = _make_context()
    fixed_ts = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
    dec_res = _make_decision_result(ctx, created_at=fixed_ts)
    builder = DecisionAuditEventBuilder()

    event1 = builder.build_audit_event(dec_res, decision_timestamp=fixed_ts)
    event2 = builder.build_audit_event(dec_res, decision_timestamp=fixed_ts)

    assert event1.audit_fingerprint == event2.audit_fingerprint


def test_03_tampered_audit_event_detection() -> None:
    """3. Test modifying audit payload alters SHA-256 audit fingerprint."""
    ctx = _make_context()
    fixed_ts = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
    dec_res1 = _make_decision_result(ctx, score=10.0, created_at=fixed_ts)
    dec_res2 = _make_decision_result(ctx, score=99.0, created_at=fixed_ts)
    builder = DecisionAuditEventBuilder()

    event1 = builder.build_audit_event(dec_res1, decision_timestamp=fixed_ts)
    event2 = builder.build_audit_event(dec_res2, decision_timestamp=fixed_ts)

    assert event1.audit_fingerprint != event2.audit_fingerprint


def test_04_immutability_of_audit_events() -> None:
    """4. Test DecisionAuditEvent is frozen/immutable (Pydantic ValidationError on mutation)."""
    ctx = _make_context()
    dec_res = _make_decision_result(ctx)
    builder = DecisionAuditEventBuilder()
    event = builder.build_audit_event(dec_res)

    with pytest.raises(ValidationError):
        event.composite_risk_score = 0.0  # Mutating frozen schema raises ValidationError


def test_05_idempotent_duplicate_handling() -> None:
    """5. Test recording duplicate audit event returns existing matching event."""
    ctx = _make_context()
    dec_res = _make_decision_result(ctx)
    service = DecisionAuditEventService()

    event1 = service.record_decision_event(dec_res)
    event2 = service.record_decision_event(dec_res)

    assert event1.event_id == event2.event_id
    assert len(service.list_events()) == 1


def test_06_conflicting_duplicate_rejection() -> None:
    """6. Test duplicate decision_id with conflicting fingerprint raises ValueError."""
    ctx = _make_context()
    dec_res1 = _make_decision_result(ctx, fp="d1" * 32)
    dec_res2 = _make_decision_result(ctx, fp="d2" * 32)
    # Force matching decision_id
    dec_res2 = dec_res2.model_copy(update={"decision_id": dec_res1.decision_id})

    service = DecisionAuditEventService()
    service.record_decision_event(dec_res1)

    with pytest.raises(ValueError, match="Conflicting audit event"):
        service.record_decision_event(dec_res2)


def test_07_tenant_isolation_retrieval() -> None:
    """7. Test tenant isolation during audit event retrieval."""
    tenant1 = uuid.uuid4()
    tenant2 = uuid.uuid4()
    ctx1 = _make_context(t_id=tenant1)
    ctx2 = _make_context(t_id=tenant2)

    dec_res1 = _make_decision_result(ctx1)
    dec_res2 = _make_decision_result(ctx2)

    service = DecisionAuditEventService()
    event1 = service.record_decision_event(dec_res1)
    event2 = service.record_decision_event(dec_res2)

    assert service.get_event_by_id(tenant1, event1.decision_id) == event1
    assert service.get_event_by_id(tenant1, event2.decision_id) is None
    assert len(service.list_events_for_tenant(tenant1)) == 1
    assert len(service.list_events_for_tenant(tenant2)) == 1


def test_08_secret_redaction_and_no_target_leakage() -> None:
    """8. Test audit event serialization redacts secrets and target leakage."""
    ctx = _make_context()
    dec_res = _make_decision_result(ctx)
    builder = DecisionAuditEventBuilder()
    event = builder.build_audit_event(dec_res)

    dumped = event.model_dump_json()
    assert "password" not in dumped
    assert "secret" not in dumped
    assert "jwt" not in dumped
    assert "is_fraud" not in dumped
    assert "fraud_label" not in dumped
    assert "chargeback_result" not in dumped


def test_09_decision_lineage_audits() -> None:
    """9. Test ALLOW, REVIEW, and BLOCK decision lineage audits."""
    ctx = _make_context()
    builder = DecisionAuditEventBuilder()

    allow_res = _make_decision_result(ctx, decision=FinalRiskDecision.ALLOW, score=15.0)
    review_res = _make_decision_result(ctx, decision=FinalRiskDecision.REVIEW, score=50.0)
    block_res = _make_decision_result(ctx, decision=FinalRiskDecision.BLOCK, score=90.0)

    allow_event = builder.build_audit_event(allow_res)
    review_event = builder.build_audit_event(review_res)
    block_event = builder.build_audit_event(block_res)

    assert allow_event.decision == FinalRiskDecision.ALLOW
    assert review_event.decision == FinalRiskDecision.REVIEW
    assert block_event.decision == FinalRiskDecision.BLOCK
