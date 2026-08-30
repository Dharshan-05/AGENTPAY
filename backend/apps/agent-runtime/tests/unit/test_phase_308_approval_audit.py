"""Unit, Security & Adversarial Test Suite for Phase 308 — Approval Audit Subsystem."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from app.payment.approval.approval_audit_service import (
    ApprovalAuditService,
)
from app.payment.approval.approval_expiration_service import ApprovalExpirationService
from app.payment.approval.approval_policy_engine import ApprovalPolicyEngine
from app.payment.approval.approval_rejection_service import (
    ApprovalRejectionService,
)
from app.payment.approval.approval_request_service import ApprovalRequestService
from app.payment.approval.approval_workflow_service import ApprovalWorkflowService
from app.schemas.approval_audit import (
    ApprovalAuditActorType,
    ApprovalAuditEvent,
    ApprovalAuditEventType,
)
from app.schemas.approval_rejection import ApprovalRejectionCommand, RejectionReason
from app.schemas.approval_request import ApprovalRequestStatus
from app.schemas.approval_workflow import (
    ApprovalDecisionCommand,
    ApprovalDecisionType,
)
from app.schemas.payment import SupportedCurrency
from app.schemas.reviewer_authorization import (
    ReviewerPermission,
    ReviewerRole,
    TrustedReviewerContext,
)
from app.schemas.risk_engine import (
    FinalRiskDecision,
    FinalRiskDecisionResult,
    RiskThresholdBand,
)


def _make_decision_result(
    tenant_id: uuid.UUID, agent_id: uuid.UUID, tx_id: str, score: float = 75.0
) -> FinalRiskDecisionResult:
    return FinalRiskDecisionResult(
        evaluation_id=uuid.uuid4(),
        decision_id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        prediction_timestamp=datetime.now(UTC),
        decision=FinalRiskDecision.REVIEW,
        decision_reason="HIGH_RISK_REVIEW",
        composite_risk_score=score,
        risk_band=RiskThresholdBand.HIGH_RISK_BAND,
        policy_precedence="REVIEW",
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
        source_fingerprints=["s" * 64],
        calculation_fingerprint="c" * 64,
        decision_fingerprint="fp_dec_308",
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def audit_service() -> ApprovalAuditService:
    return ApprovalAuditService()


@pytest.fixture
def request_service(audit_service: ApprovalAuditService) -> ApprovalRequestService:
    return ApprovalRequestService(audit_service=audit_service)


@pytest.fixture
def sample_ids() -> dict[str, uuid.UUID | str]:
    return {
        "tenant_id": uuid.uuid4(),
        "agent_id": uuid.uuid4(),
        "reviewer_id": uuid.uuid4(),
        "transaction_id": f"tx_audit_{uuid.uuid4().hex[:8]}",
        "req_id": uuid.uuid4(),
    }


# -----------------------------------------------------------------------------
# PHASE 308 TEST MATRIX (25 Required Scenarios)
# -----------------------------------------------------------------------------


def test_01_audit_event_creation(
    audit_service: ApprovalAuditService, sample_ids: dict[str, Any]
) -> None:
    """Test 1: Audit creation records valid immutable event."""
    event = audit_service.record_event(
        tenant_id=sample_ids["tenant_id"],
        approval_request_id=sample_ids["req_id"],
        transaction_id=sample_ids["transaction_id"],
        agent_id=sample_ids["agent_id"],
        event_type=ApprovalAuditEventType.APPROVAL_REQUEST_CREATED,
        actor_type=ApprovalAuditActorType.SYSTEM,
        resulting_status=ApprovalRequestStatus.PENDING,
        approval_fingerprint="fp_test_01",
    )
    assert event.audit_event_id is not None
    assert event.event_type == ApprovalAuditEventType.APPROVAL_REQUEST_CREATED
    assert event.actor_type == ApprovalAuditActorType.SYSTEM
    assert event.event_fingerprint != ""


def test_02_immutable_audit_model(
    audit_service: ApprovalAuditService, sample_ids: dict[str, Any]
) -> None:
    """Test 2: Audit model is frozen and rejects attribute assignment."""
    event = audit_service.record_event(
        tenant_id=sample_ids["tenant_id"],
        approval_request_id=sample_ids["req_id"],
        transaction_id=sample_ids["transaction_id"],
        agent_id=sample_ids["agent_id"],
        event_type=ApprovalAuditEventType.APPROVAL_REQUEST_CREATED,
        actor_type=ApprovalAuditActorType.SYSTEM,
        approval_fingerprint="fp_test_02",
    )
    with pytest.raises((TypeError, ValidationError, AttributeError)):
        event.resulting_status = ApprovalRequestStatus.APPROVED


def test_03_extra_field_rejection() -> None:
    """Test 3: Extra fields in audit model trigger ValidationError (extra='forbid')."""
    with pytest.raises(ValidationError):
        ApprovalAuditEvent(
            tenant_id=uuid.uuid4(),
            approval_request_id=uuid.uuid4(),
            transaction_id="tx_extra",
            agent_id=uuid.uuid4(),
            event_type=ApprovalAuditEventType.APPROVAL_REQUEST_CREATED,
            actor_type=ApprovalAuditActorType.SYSTEM,
            approval_fingerprint="fp",
            timestamp_utc=datetime.now(UTC),
            event_fingerprint="fp",
            unauthorized_field="malicious_payload",  # type: ignore[call-arg]
        )


def test_04_deterministic_fingerprint(
    audit_service: ApprovalAuditService, sample_ids: dict[str, Any]
) -> None:
    """Test 4: Event fingerprint is deterministic given same input fields."""
    ts = datetime(2026, 8, 27, 12, 0, 0, tzinfo=UTC)
    fp1 = audit_service._calculate_event_fingerprint(
        tenant_id=sample_ids["tenant_id"],
        approval_request_id=sample_ids["req_id"],
        transaction_id=sample_ids["transaction_id"],
        agent_id=sample_ids["agent_id"],
        event_type=ApprovalAuditEventType.APPROVAL_APPROVED,
        actor_type=ApprovalAuditActorType.REVIEWER,
        actor_id=sample_ids["reviewer_id"],
        previous_status=ApprovalRequestStatus.PENDING,
        resulting_status=ApprovalRequestStatus.APPROVED,
        approval_fingerprint="fp_canonical",
        timestamp_utc=ts,
    )
    fp2 = audit_service._calculate_event_fingerprint(
        tenant_id=sample_ids["tenant_id"],
        approval_request_id=sample_ids["req_id"],
        transaction_id=sample_ids["transaction_id"],
        agent_id=sample_ids["agent_id"],
        event_type=ApprovalAuditEventType.APPROVAL_APPROVED,
        actor_type=ApprovalAuditActorType.REVIEWER,
        actor_id=sample_ids["reviewer_id"],
        previous_status=ApprovalRequestStatus.PENDING,
        resulting_status=ApprovalRequestStatus.APPROVED,
        approval_fingerprint="fp_canonical",
        timestamp_utc=ts,
    )
    assert fp1 == fp2


def test_05_fingerprint_verification(
    audit_service: ApprovalAuditService, sample_ids: dict[str, Any]
) -> None:
    """Test 5: Audit event integrity verification succeeds for pristine records."""
    event = audit_service.record_event(
        tenant_id=sample_ids["tenant_id"],
        approval_request_id=sample_ids["req_id"],
        transaction_id=sample_ids["transaction_id"],
        agent_id=sample_ids["agent_id"],
        event_type=ApprovalAuditEventType.APPROVAL_APPROVED,
        actor_type=ApprovalAuditActorType.REVIEWER,
        actor_id=sample_ids["reviewer_id"],
        approval_fingerprint="fp_test_05",
    )
    assert audit_service.verify_audit_event_integrity(event) is True


def test_06_fingerprint_tampering_detection(
    audit_service: ApprovalAuditService, sample_ids: dict[str, Any]
) -> None:
    """Test 6: Tampering with audit record fields invalidates event integrity."""
    event = audit_service.record_event(
        tenant_id=sample_ids["tenant_id"],
        approval_request_id=sample_ids["req_id"],
        transaction_id=sample_ids["transaction_id"],
        agent_id=sample_ids["agent_id"],
        event_type=ApprovalAuditEventType.APPROVAL_APPROVED,
        actor_type=ApprovalAuditActorType.REVIEWER,
        actor_id=sample_ids["reviewer_id"],
        approval_fingerprint="fp_test_06",
    )
    tampered_event = event.model_copy(update={"transaction_id": "tx_tampered"})
    assert audit_service.verify_audit_event_integrity(tampered_event) is False


def test_07_tenant_isolation(audit_service: ApprovalAuditService) -> None:
    """Test 7: Audit log query strictly respects tenant boundary."""
    t1, t2 = uuid.uuid4(), uuid.uuid4()
    req_id = uuid.uuid4()

    audit_service.record_event(
        tenant_id=t1,
        approval_request_id=req_id,
        transaction_id="tx_t1",
        agent_id=uuid.uuid4(),
        event_type=ApprovalAuditEventType.APPROVAL_REQUEST_CREATED,
        actor_type=ApprovalAuditActorType.SYSTEM,
        approval_fingerprint="fp_t1",
    )

    res_t1 = audit_service.get_audit_events_for_request(t1, req_id)
    assert res_t1.total_events == 1

    res_t2 = audit_service.get_audit_events_for_request(t2, req_id)
    assert res_t2.total_events == 0


def test_08_cross_tenant_query_prevention(audit_service: ApprovalAuditService) -> None:
    """Test 8: Querying audit log under different tenant_id returns 0 results."""
    t1 = uuid.uuid4()
    req_id = uuid.uuid4()
    audit_service.record_event(
        tenant_id=t1,
        approval_request_id=req_id,
        transaction_id="tx_cross",
        agent_id=uuid.uuid4(),
        event_type=ApprovalAuditEventType.APPROVAL_VIEWED,
        actor_type=ApprovalAuditActorType.REVIEWER,
        approval_fingerprint="fp_cross",
    )
    res = audit_service.get_audit_events_for_request(uuid.uuid4(), req_id)
    assert res.total_events == 0
    assert len(res.events) == 0


def test_09_reviewer_identity_binding(
    audit_service: ApprovalAuditService, sample_ids: dict[str, Any]
) -> None:
    """Test 9: Audit events record authenticated reviewer_id bound to REVIEWER actor."""
    event = audit_service.record_event(
        tenant_id=sample_ids["tenant_id"],
        approval_request_id=sample_ids["req_id"],
        transaction_id=sample_ids["transaction_id"],
        agent_id=sample_ids["agent_id"],
        event_type=ApprovalAuditEventType.APPROVAL_APPROVED,
        actor_type=ApprovalAuditActorType.REVIEWER,
        actor_id=sample_ids["reviewer_id"],
        approval_fingerprint="fp_reviewer",
    )
    assert event.actor_type == ApprovalAuditActorType.REVIEWER
    assert event.actor_id == sample_ids["reviewer_id"]


def test_10_impersonation_prevention(audit_service: ApprovalAuditService) -> None:
    """Test 10: Verify actor_type and actor_id are explicitly recorded."""
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    event = audit_service.record_event(
        tenant_id=uuid.uuid4(),
        approval_request_id=uuid.uuid4(),
        transaction_id="tx_imp",
        agent_id=agent_id,
        event_type=ApprovalAuditEventType.APPROVAL_REJECTED,
        actor_type=ApprovalAuditActorType.REVIEWER,
        actor_id=reviewer_id,
        approval_fingerprint="fp_imp",
    )
    assert event.actor_id != agent_id
    assert event.actor_type == ApprovalAuditActorType.REVIEWER


def test_11_approval_creation_audit_integration(
    request_service: ApprovalRequestService, audit_service: ApprovalAuditService
) -> None:
    """Test 11: Creating approval request automatically emits APPROVAL_REQUEST_CREATED."""
    t_id = uuid.uuid4()
    a_id = uuid.uuid4()
    tx_id = f"tx_create_{uuid.uuid4().hex[:8]}"

    risk = _make_decision_result(t_id, a_id, tx_id, score=75.0)
    engine = ApprovalPolicyEngine()
    req = engine.evaluate_approval_requirement(risk, Decimal("25000.00"), SupportedCurrency.INR)

    res = request_service.create_approval_request(risk, req, idempotency_key="idemp_11")

    history = audit_service.get_audit_events_for_request(
        t_id, res.request_record.approval_request_id
    )
    assert history.total_events == 1
    assert history.events[0].event_type == ApprovalAuditEventType.APPROVAL_REQUEST_CREATED


def test_12_approval_approved_audit_integration(
    request_service: ApprovalRequestService, audit_service: ApprovalAuditService
) -> None:
    """Test 12: Approving request emits APPROVAL_APPROVED event."""
    t_id, a_id, r_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    tx_id = f"tx_app_{uuid.uuid4().hex[:8]}"

    risk = _make_decision_result(t_id, a_id, tx_id, score=70.0)
    engine = ApprovalPolicyEngine()
    req = engine.evaluate_approval_requirement(risk, Decimal("15000.00"), SupportedCurrency.INR)
    created = request_service.create_approval_request(risk, req, idempotency_key="idemp_12")
    req_rec = created.request_record

    from app.payment.approval.reviewer_authorization_service import (
        ReviewerAuthorizationService,
    )

    auth_service = ReviewerAuthorizationService()
    workflow_service = ApprovalWorkflowService(
        request_service=request_service,
        auth_service=auth_service,
        audit_service=audit_service,
    )

    reviewer_ctx = TrustedReviewerContext(
        reviewer_id=r_id,
        tenant_id=t_id,
        reviewer_role=ReviewerRole.REVIEWER,
        permissions={
            ReviewerPermission.VIEW_APPROVAL_REQUEST,
            ReviewerPermission.APPROVE_PAYMENT,
        },
    )

    cmd = ApprovalDecisionCommand(
        approval_request_id=req_rec.approval_request_id,
        tenant_id=t_id,
        reviewer_context=reviewer_ctx,
        decision=ApprovalDecisionType.APPROVE,
        idempotency_key="idemp_app_12",
        expected_approval_fingerprint=req_rec.approval_fingerprint,
    )
    workflow_service.approve_request(cmd)

    history = audit_service.get_audit_events_for_request(t_id, req_rec.approval_request_id)
    assert history.total_events == 2
    types = [e.event_type for e in history.events]
    assert ApprovalAuditEventType.APPROVAL_REQUEST_CREATED in types
    assert ApprovalAuditEventType.APPROVAL_APPROVED in types


def test_13_rejection_audit_integration(
    request_service: ApprovalRequestService, audit_service: ApprovalAuditService
) -> None:
    """Test 13: Rejecting request emits APPROVAL_REJECTED event."""
    t_id, a_id, r_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    tx_id = f"tx_rej_{uuid.uuid4().hex[:8]}"

    risk = _make_decision_result(t_id, a_id, tx_id, score=85.0)
    engine = ApprovalPolicyEngine()
    req = engine.evaluate_approval_requirement(risk, Decimal("50000.00"), SupportedCurrency.INR)
    created = request_service.create_approval_request(risk, req, idempotency_key="idemp_13")
    req_rec = created.request_record

    from app.payment.approval.reviewer_authorization_service import (
        ReviewerAuthorizationService,
    )

    auth_service = ReviewerAuthorizationService()
    rejection_service = ApprovalRejectionService(
        request_service=request_service,
        auth_service=auth_service,
        audit_service=audit_service,
    )

    reviewer_ctx = TrustedReviewerContext(
        reviewer_id=r_id,
        tenant_id=t_id,
        reviewer_role=ReviewerRole.REVIEWER,
        permissions={
            ReviewerPermission.VIEW_APPROVAL_REQUEST,
            ReviewerPermission.REJECT_PAYMENT,
        },
    )

    cmd = ApprovalRejectionCommand(
        approval_request_id=req_rec.approval_request_id,
        tenant_id=t_id,
        reviewer_context=reviewer_ctx,
        rejection_reason=RejectionReason.HIGH_RISK_SUSPECTED,
        idempotency_key="idemp_rej_13",
        expected_approval_fingerprint=req_rec.approval_fingerprint,
    )
    rejection_service.reject_request(cmd)

    history = audit_service.get_audit_events_for_request(t_id, req_rec.approval_request_id)
    assert history.total_events == 2
    types = [e.event_type for e in history.events]
    assert ApprovalAuditEventType.APPROVAL_REJECTED in types


def test_14_expiration_audit_integration(
    request_service: ApprovalRequestService, audit_service: ApprovalAuditService
) -> None:
    """Test 14: Expiring request emits APPROVAL_EXPIRED event."""
    t_id, a_id = uuid.uuid4(), uuid.uuid4()
    tx_id = f"tx_exp_{uuid.uuid4().hex[:8]}"

    risk = _make_decision_result(t_id, a_id, tx_id, score=50.0)
    engine = ApprovalPolicyEngine()
    req = engine.evaluate_approval_requirement(risk, Decimal("1000.00"), SupportedCurrency.INR)
    created = request_service.create_approval_request(risk, req, idempotency_key="idemp_14")
    req_rec = created.request_record

    exp_service = ApprovalExpirationService(
        request_service=request_service,
        audit_service=audit_service,
        default_ttl_hours=1,
    )

    future_time = datetime.now(UTC) + pytest.importorskip("datetime").timedelta(hours=2)
    exp_service.expire_approval_request(
        approval_request_id=req_rec.approval_request_id,
        tenant_id=t_id,
        now_utc=future_time,
    )

    history = audit_service.get_audit_events_for_request(t_id, req_rec.approval_request_id)
    assert history.total_events == 2
    types = [e.event_type for e in history.events]
    assert ApprovalAuditEventType.APPROVAL_EXPIRED in types


def test_15_execution_start_audit(
    audit_service: ApprovalAuditService, sample_ids: dict[str, Any]
) -> None:
    """Test 15: Recording APPROVAL_EXECUTION_STARTED audit event."""
    event = audit_service.record_event(
        tenant_id=sample_ids["tenant_id"],
        approval_request_id=sample_ids["req_id"],
        transaction_id=sample_ids["transaction_id"],
        agent_id=sample_ids["agent_id"],
        event_type=ApprovalAuditEventType.APPROVAL_EXECUTION_STARTED,
        actor_type=ApprovalAuditActorType.PAYMENT_ENGINE,
        approval_fingerprint="fp_exec_start",
    )
    assert event.event_type == ApprovalAuditEventType.APPROVAL_EXECUTION_STARTED


def test_16_execution_success_audit(
    audit_service: ApprovalAuditService, sample_ids: dict[str, Any]
) -> None:
    """Test 16: Recording APPROVAL_EXECUTION_SUCCEEDED audit event."""
    event = audit_service.record_event(
        tenant_id=sample_ids["tenant_id"],
        approval_request_id=sample_ids["req_id"],
        transaction_id=sample_ids["transaction_id"],
        agent_id=sample_ids["agent_id"],
        event_type=ApprovalAuditEventType.APPROVAL_EXECUTION_SUCCEEDED,
        actor_type=ApprovalAuditActorType.PAYMENT_ENGINE,
        approval_fingerprint="fp_exec_succ",
    )
    assert event.event_type == ApprovalAuditEventType.APPROVAL_EXECUTION_SUCCEEDED


def test_17_execution_failure_audit(
    audit_service: ApprovalAuditService, sample_ids: dict[str, Any]
) -> None:
    """Test 17: Recording APPROVAL_EXECUTION_FAILED audit event."""
    event = audit_service.record_event(
        tenant_id=sample_ids["tenant_id"],
        approval_request_id=sample_ids["req_id"],
        transaction_id=sample_ids["transaction_id"],
        agent_id=sample_ids["agent_id"],
        event_type=ApprovalAuditEventType.APPROVAL_EXECUTION_FAILED,
        actor_type=ApprovalAuditActorType.PAYMENT_ENGINE,
        approval_fingerprint="fp_exec_fail",
    )
    assert event.event_type == ApprovalAuditEventType.APPROVAL_EXECUTION_FAILED


def test_18_execution_blocked_audit(
    audit_service: ApprovalAuditService, sample_ids: dict[str, Any]
) -> None:
    """Test 18: Recording APPROVAL_EXECUTION_BLOCKED audit event."""
    event = audit_service.record_event(
        tenant_id=sample_ids["tenant_id"],
        approval_request_id=sample_ids["req_id"],
        transaction_id=sample_ids["transaction_id"],
        agent_id=sample_ids["agent_id"],
        event_type=ApprovalAuditEventType.APPROVAL_EXECUTION_BLOCKED,
        actor_type=ApprovalAuditActorType.PAYMENT_ENGINE,
        approval_fingerprint="fp_exec_block",
        metadata={"reason": "TAMPERED_AMOUNT"},
    )
    assert event.event_type == ApprovalAuditEventType.APPROVAL_EXECUTION_BLOCKED


def test_19_replay_audit(audit_service: ApprovalAuditService, sample_ids: dict[str, Any]) -> None:
    """Test 19: Recording APPROVAL_REPLAYED audit event."""
    event = audit_service.record_event(
        tenant_id=sample_ids["tenant_id"],
        approval_request_id=sample_ids["req_id"],
        transaction_id=sample_ids["transaction_id"],
        agent_id=sample_ids["agent_id"],
        event_type=ApprovalAuditEventType.APPROVAL_REPLAYED,
        actor_type=ApprovalAuditActorType.PAYMENT_ENGINE,
        approval_fingerprint="fp_replay",
    )
    assert event.event_type == ApprovalAuditEventType.APPROVAL_REPLAYED


def test_20_conflict_audit(audit_service: ApprovalAuditService, sample_ids: dict[str, Any]) -> None:
    """Test 20: Recording APPROVAL_CONFLICT audit event."""
    event = audit_service.record_event(
        tenant_id=sample_ids["tenant_id"],
        approval_request_id=sample_ids["req_id"],
        transaction_id=sample_ids["transaction_id"],
        agent_id=sample_ids["agent_id"],
        event_type=ApprovalAuditEventType.APPROVAL_CONFLICT,
        actor_type=ApprovalAuditActorType.PAYMENT_ENGINE,
        approval_fingerprint="fp_conflict",
    )
    assert event.event_type == ApprovalAuditEventType.APPROVAL_CONFLICT


def test_21_secret_redaction(
    audit_service: ApprovalAuditService, sample_ids: dict[str, Any]
) -> None:
    """Test 21: Metadata automatically sanitizes secret keys."""
    meta = {
        "key_secret": "rzp_secret_12345",
        "webhook_secret": "wh_secret_999",
        "authorization": "Bearer token_abc",
        "safe_context": "order_evaluation",
    }
    event = audit_service.record_event(
        tenant_id=sample_ids["tenant_id"],
        approval_request_id=sample_ids["req_id"],
        transaction_id=sample_ids["transaction_id"],
        agent_id=sample_ids["agent_id"],
        event_type=ApprovalAuditEventType.APPROVAL_REQUEST_CREATED,
        actor_type=ApprovalAuditActorType.SYSTEM,
        approval_fingerprint="fp_sec",
        metadata=meta,
    )
    assert "key_secret" not in event.metadata
    assert "webhook_secret" not in event.metadata
    assert "authorization" not in event.metadata
    assert event.metadata["safe_context"] == "order_evaluation"


def test_22_no_razorpay_import() -> None:
    """Test 22: Static boundary check confirming 0 Razorpay SDK imports in audit module."""
    import inspect

    import app.payment.approval.approval_audit_service as mod

    source = inspect.getsource(mod)
    assert "import razorpay" not in source
    assert "from razorpay" not in source


def test_23_no_payment_status_mutation() -> None:
    """Test 23: Static boundary check confirming audit service does not assign PaymentStatus."""
    import inspect

    import app.payment.approval.approval_audit_service as mod

    source = inspect.getsource(mod)
    assert "PaymentStatusService" not in source
    assert "transition_status" not in source


def test_24_no_audit_deletion_exposed(audit_service: ApprovalAuditService) -> None:
    """Test 24: Verify append-only semantics: no delete or update methods exist on service."""
    assert not hasattr(audit_service, "delete_audit_event")
    assert not hasattr(audit_service, "delete_audit_log")
    assert not hasattr(audit_service, "update_audit_event")


def test_25_empty_audit_query(audit_service: ApprovalAuditService) -> None:
    """Test 25: Querying audit log for unknown request returns 0 events and verified=True."""
    res = audit_service.get_audit_events_for_request(uuid.uuid4(), uuid.uuid4())
    assert res.total_events == 0
    assert len(res.events) == 0
    assert res.all_events_verified is True
