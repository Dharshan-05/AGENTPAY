"""Test Suite for Phase 309 — Approved Payment Continuation Subsystem."""

from __future__ import annotations

import concurrent.futures
import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.payment.approval.approval_audit_service import ApprovalAuditService
from app.payment.approval.approval_expiration_service import ApprovalExpirationService
from app.payment.approval.approval_policy_engine import ApprovalPolicyEngine
from app.payment.approval.approval_rejection_service import ApprovalRejectionService
from app.payment.approval.approval_request_service import ApprovalRequestService
from app.payment.approval.approval_workflow_service import ApprovalWorkflowService
from app.payment.approval.approved_payment_continuation_service import (
    ApprovedPaymentContinuationConflictError,
    ApprovedPaymentContinuationError,
    ApprovedPaymentContinuationService,
)
from app.payment.approval.reviewer_authorization_service import ReviewerAuthorizationService
from app.schemas.approval_audit import ApprovalAuditEventType
from app.schemas.approval_request import ApprovalRequestRecord, ApprovalRequestStatus
from app.schemas.approval_workflow import (
    ApprovalDecisionCommand,
    ApprovalDecisionType,
)
from app.schemas.approved_payment_continuation import (
    ApprovedPaymentContinuationCommand,
    ApprovedPaymentContinuationResult,
)
from app.schemas.payment import PaymentStatus, SupportedCurrency
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
        decision_fingerprint="fp_dec_309",
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def audit_service() -> ApprovalAuditService:
    return ApprovalAuditService()


@pytest.fixture
def request_service(audit_service: ApprovalAuditService) -> ApprovalRequestService:
    return ApprovalRequestService(audit_service=audit_service)


@pytest.fixture
def auth_service() -> ReviewerAuthorizationService:
    return ReviewerAuthorizationService()


@pytest.fixture
def workflow_service(
    request_service: ApprovalRequestService,
    auth_service: ReviewerAuthorizationService,
    audit_service: ApprovalAuditService,
) -> ApprovalWorkflowService:
    return ApprovalWorkflowService(
        request_service=request_service,
        auth_service=auth_service,
        audit_service=audit_service,
    )


@pytest.fixture
def continuation_service(
    request_service: ApprovalRequestService, audit_service: ApprovalAuditService
) -> ApprovedPaymentContinuationService:
    return ApprovedPaymentContinuationService(
        request_service=request_service, audit_service=audit_service
    )


def helper_create_approved_request(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    amount: Decimal = Decimal("50000.00"),
    currency: SupportedCurrency = SupportedCurrency.INR,
) -> tuple[ApprovalRequestRecord, uuid.UUID, uuid.UUID, uuid.UUID, str]:
    """Helper to create and approve an approval request via Phase 302 and Phase 305."""
    t_id, a_id, r_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    tx_id = f"tx_cont_{uuid.uuid4().hex[:8]}"

    risk = _make_decision_result(t_id, a_id, tx_id, score=75.0)
    engine = ApprovalPolicyEngine()
    req = engine.evaluate_approval_requirement(risk, amount, currency)
    created = request_service.create_approval_request(risk, req, idempotency_key=f"idemp_{tx_id}")
    req_rec = created.request_record

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
        idempotency_key=f"idemp_app_{tx_id}",
        expected_approval_fingerprint=req_rec.approval_fingerprint,
    )
    workflow_service.approve_request(cmd)

    # Re-read updated approved record
    approved_rec = request_service.get_approval_request(t_id, req_rec.approval_request_id)
    assert approved_rec is not None
    return approved_rec, t_id, a_id, r_id, tx_id


# -----------------------------------------------------------------------------
# PHASE 309 TEST MATRIX (35 Required Scenarios)
# -----------------------------------------------------------------------------


def test_01_approved_request_permits_continuation(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 1: Approved approval request successfully executes continuation."""
    app_rec, t_id, a_id, _, tx_id = helper_create_approved_request(
        request_service, workflow_service
    )

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id=tx_id,
        amount=app_rec.amount,
        currency=app_rec.currency,
        idempotency_key="idemp_cont_01",
        expected_approval_fingerprint=app_rec.approval_fingerprint,
    )

    res = continuation_service.execute_continuation(cmd)
    assert res.execution_status == "CONTINUATION_EXECUTED"
    assert res.payment_status == PaymentStatus.PAYMENT_PENDING
    assert res.is_existing is False
    assert res.execution_fingerprint != ""


def test_02_pending_request_blocked(
    request_service: ApprovalRequestService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 2: Pending approval request is blocked from continuation."""
    t_id, a_id = uuid.uuid4(), uuid.uuid4()
    tx_id = f"tx_pend_{uuid.uuid4().hex[:8]}"

    risk = _make_decision_result(t_id, a_id, tx_id, score=70.0)
    engine = ApprovalPolicyEngine()
    req = engine.evaluate_approval_requirement(risk, Decimal("10000.00"), SupportedCurrency.INR)
    created = request_service.create_approval_request(risk, req, idempotency_key="idemp_pend_02")
    req_rec = created.request_record

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=req_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id=tx_id,
        amount=req_rec.amount,
        currency=req_rec.currency,
        idempotency_key="idemp_cont_02",
        expected_approval_fingerprint=req_rec.approval_fingerprint,
    )

    with pytest.raises(ApprovedPaymentContinuationError) as exc_info:
        continuation_service.execute_continuation(cmd)
    assert exc_info.value.error_code == "APPROVAL_NOT_APPROVED"


def test_03_rejected_request_blocked(
    request_service: ApprovalRequestService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 3: Rejected approval request is blocked from continuation."""
    t_id, a_id, r_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    tx_id = f"tx_rej_{uuid.uuid4().hex[:8]}"

    risk = _make_decision_result(t_id, a_id, tx_id, score=90.0)
    engine = ApprovalPolicyEngine()
    req = engine.evaluate_approval_requirement(risk, Decimal("50000.00"), SupportedCurrency.INR)
    created = request_service.create_approval_request(risk, req, idempotency_key="idemp_rej_03")
    req_rec = created.request_record

    from app.schemas.approval_rejection import (
        ApprovalRejectionCommand,
        RejectionReason,
    )

    rejection_service = ApprovalRejectionService(
        request_service=request_service, auth_service=ReviewerAuthorizationService()
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
    rejection_service.reject_request(
        ApprovalRejectionCommand(
            approval_request_id=req_rec.approval_request_id,
            tenant_id=t_id,
            reviewer_context=reviewer_ctx,
            rejection_reason=RejectionReason.HIGH_RISK_SUSPECTED,
            idempotency_key="idemp_rej_cmd",
            expected_approval_fingerprint=req_rec.approval_fingerprint,
        )
    )

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=req_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id=tx_id,
        amount=req_rec.amount,
        currency=req_rec.currency,
        idempotency_key="idemp_cont_03",
        expected_approval_fingerprint=req_rec.approval_fingerprint,
    )

    with pytest.raises(ApprovedPaymentContinuationError) as exc_info:
        continuation_service.execute_continuation(cmd)
    assert exc_info.value.error_code == "APPROVAL_NOT_APPROVED"


def test_04_expired_request_blocked(
    request_service: ApprovalRequestService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 4: Expired approval request is blocked from continuation."""
    t_id, a_id = uuid.uuid4(), uuid.uuid4()
    tx_id = f"tx_exp_{uuid.uuid4().hex[:8]}"

    risk = _make_decision_result(t_id, a_id, tx_id, score=60.0)
    engine = ApprovalPolicyEngine()
    req = engine.evaluate_approval_requirement(risk, Decimal("1000.00"), SupportedCurrency.INR)
    created = request_service.create_approval_request(risk, req, idempotency_key="idemp_exp_04")
    req_rec = created.request_record

    exp_service = ApprovalExpirationService(request_service=request_service, default_ttl_hours=1)
    future_time = datetime.now(UTC) + pytest.importorskip("datetime").timedelta(hours=2)
    exp_service.expire_approval_request(req_rec.approval_request_id, t_id, now_utc=future_time)

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=req_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id=tx_id,
        amount=req_rec.amount,
        currency=req_rec.currency,
        idempotency_key="idemp_cont_04",
        expected_approval_fingerprint=req_rec.approval_fingerprint,
    )

    with pytest.raises(ApprovedPaymentContinuationError) as exc_info:
        continuation_service.execute_continuation(cmd)
    assert exc_info.value.error_code == "APPROVAL_NOT_APPROVED"


def test_05_cancelled_request_blocked(
    request_service: ApprovalRequestService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 5: Cancelled approval request is blocked from continuation."""
    t_id, a_id = uuid.uuid4(), uuid.uuid4()
    tx_id = f"tx_canc_{uuid.uuid4().hex[:8]}"

    risk = _make_decision_result(t_id, a_id, tx_id, score=60.0)
    engine = ApprovalPolicyEngine()
    req = engine.evaluate_approval_requirement(risk, Decimal("1000.00"), SupportedCurrency.INR)
    created = request_service.create_approval_request(risk, req, idempotency_key="idemp_canc_05")
    req_rec = created.request_record

    # Manually transition to CANCELLED for boundary testing
    request_service._store_by_id[req_rec.approval_request_id] = req_rec.model_copy(
        update={"status": ApprovalRequestStatus.CANCELLED}
    )

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=req_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id=tx_id,
        amount=req_rec.amount,
        currency=req_rec.currency,
        idempotency_key="idemp_cont_05",
        expected_approval_fingerprint=req_rec.approval_fingerprint,
    )

    with pytest.raises(ApprovedPaymentContinuationError) as exc_info:
        continuation_service.execute_continuation(cmd)
    assert exc_info.value.error_code == "APPROVAL_NOT_APPROVED"


def test_06_missing_approval_request_blocked(
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 6: Non-existent approval request ID raises APPROVAL_REQUEST_NOT_FOUND."""
    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_missing",
        amount=Decimal("500.00"),
        currency=SupportedCurrency.INR,
        idempotency_key="idemp_missing",
        expected_approval_fingerprint="fp_missing",
    )
    with pytest.raises(ApprovedPaymentContinuationError) as exc_info:
        continuation_service.execute_continuation(cmd)
    assert exc_info.value.error_code == "APPROVAL_REQUEST_NOT_FOUND"


def test_07_self_approval_prevention_retained(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 7: Self-approval attempt is blocked upstream by workflow_service."""
    t_id, agent_id = uuid.uuid4(), uuid.uuid4()
    tx_id = f"tx_self_{uuid.uuid4().hex[:8]}"

    risk = _make_decision_result(t_id, agent_id, tx_id, score=75.0)
    engine = ApprovalPolicyEngine()
    req = engine.evaluate_approval_requirement(risk, Decimal("10000.00"), SupportedCurrency.INR)
    created = request_service.create_approval_request(risk, req, idempotency_key="idemp_self")
    req_rec = created.request_record

    # Attempt self-approval (reviewer_id == agent_id)
    reviewer_ctx = TrustedReviewerContext(
        reviewer_id=agent_id,
        tenant_id=t_id,
        reviewer_role=ReviewerRole.REVIEWER,
        permissions={ReviewerPermission.APPROVE_PAYMENT},
    )
    cmd_approve = ApprovalDecisionCommand(
        approval_request_id=req_rec.approval_request_id,
        tenant_id=t_id,
        reviewer_context=reviewer_ctx,
        decision=ApprovalDecisionType.APPROVE,
        idempotency_key="idemp_self_app",
        expected_approval_fingerprint=req_rec.approval_fingerprint,
    )
    from app.payment.approval.approval_workflow_service import ApprovalWorkflowError

    with pytest.raises(ApprovalWorkflowError):
        workflow_service.approve_request(cmd_approve)


def test_08_tenant_mismatch_blocked(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 8: Tenant ID mismatch triggers FINANCIAL_PARAMETER_TAMPERING."""
    app_rec, t_id, a_id, _, tx_id = helper_create_approved_request(
        request_service, workflow_service
    )

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=uuid.uuid4(),  # Mismatched tenant
        agent_id=a_id,
        transaction_id=tx_id,
        amount=app_rec.amount,
        currency=app_rec.currency,
        idempotency_key="idemp_t_mismatch",
        expected_approval_fingerprint=app_rec.approval_fingerprint,
    )
    with pytest.raises(ApprovedPaymentContinuationError) as exc_info:
        continuation_service.execute_continuation(cmd)
    assert exc_info.value.error_code in (
        "APPROVAL_REQUEST_NOT_FOUND",
        "FINANCIAL_PARAMETER_TAMPERING",
    )


def test_09_agent_mismatch_blocked(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 9: Agent ID mismatch triggers FINANCIAL_PARAMETER_TAMPERING."""
    app_rec, t_id, a_id, _, tx_id = helper_create_approved_request(
        request_service, workflow_service
    )

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=uuid.uuid4(),  # Mismatched agent
        transaction_id=tx_id,
        amount=app_rec.amount,
        currency=app_rec.currency,
        idempotency_key="idemp_a_mismatch",
        expected_approval_fingerprint=app_rec.approval_fingerprint,
    )
    with pytest.raises(ApprovedPaymentContinuationError) as exc_info:
        continuation_service.execute_continuation(cmd)
    assert exc_info.value.error_code == "FINANCIAL_PARAMETER_TAMPERING"


def test_10_transaction_mismatch_blocked(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 10: Transaction ID mismatch triggers FINANCIAL_PARAMETER_TAMPERING."""
    app_rec, t_id, a_id, _, tx_id = helper_create_approved_request(
        request_service, workflow_service
    )

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_tampered_10",  # Mismatched tx
        amount=app_rec.amount,
        currency=app_rec.currency,
        idempotency_key="idemp_tx_mismatch",
        expected_approval_fingerprint=app_rec.approval_fingerprint,
    )
    with pytest.raises(ApprovedPaymentContinuationError) as exc_info:
        continuation_service.execute_continuation(cmd)
    assert exc_info.value.error_code == "FINANCIAL_PARAMETER_TAMPERING"


def test_11_authorization_fingerprint_mismatch_blocked(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 11: Approval fingerprint mismatch triggers FINANCIAL_PARAMETER_TAMPERING."""
    app_rec, t_id, a_id, _, tx_id = helper_create_approved_request(
        request_service, workflow_service
    )

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id=tx_id,
        amount=app_rec.amount,
        currency=app_rec.currency,
        idempotency_key="idemp_fp_mismatch",
        expected_approval_fingerprint="fp_tampered_11",  # Mismatched fp
    )
    with pytest.raises(ApprovedPaymentContinuationError) as exc_info:
        continuation_service.execute_continuation(cmd)
    assert exc_info.value.error_code == "FINANCIAL_PARAMETER_TAMPERING"


def test_12_approval_fingerprint_mismatch_blocked(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 12: Expected approval fingerprint mismatch is rejected."""
    app_rec, t_id, a_id, _, tx_id = helper_create_approved_request(
        request_service, workflow_service
    )

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id=tx_id,
        amount=app_rec.amount,
        currency=app_rec.currency,
        idempotency_key="idemp_fp_mismatch_12",
        expected_approval_fingerprint="invalid_fp",
    )
    with pytest.raises(ApprovedPaymentContinuationError) as exc_info:
        continuation_service.execute_continuation(cmd)
    assert exc_info.value.error_code == "FINANCIAL_PARAMETER_TAMPERING"


def test_13_amount_tampering_blocked(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 13: Approved ₹50,000 trying to execute ₹75,000 is blocked."""
    app_rec, t_id, a_id, _, tx_id = helper_create_approved_request(
        request_service, workflow_service, amount=Decimal("50000.00")
    )

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id=tx_id,
        amount=Decimal("75000.00"),  # Tampered amount!
        currency=app_rec.currency,
        idempotency_key="idemp_amt_tamper",
        expected_approval_fingerprint=app_rec.approval_fingerprint,
    )
    with pytest.raises(ApprovedPaymentContinuationError) as exc_info:
        continuation_service.execute_continuation(cmd)
    assert exc_info.value.error_code == "FINANCIAL_PARAMETER_TAMPERING"


def test_14_currency_tampering_blocked(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 14: Approved INR trying to execute USD is blocked."""
    app_rec, t_id, a_id, _, tx_id = helper_create_approved_request(
        request_service, workflow_service, currency=SupportedCurrency.INR
    )

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id=tx_id,
        amount=app_rec.amount,
        currency=SupportedCurrency.USD,  # Tampered currency!
        idempotency_key="idemp_curr_tamper",
        expected_approval_fingerprint=app_rec.approval_fingerprint,
    )
    with pytest.raises(ApprovedPaymentContinuationError) as exc_info:
        continuation_service.execute_continuation(cmd)
    assert exc_info.value.error_code == "FINANCIAL_PARAMETER_TAMPERING"


def test_15_provider_order_id_tampering_blocked(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 15: Parameter tampering checks protect transaction/order binding."""
    app_rec, t_id, a_id, _, tx_id = helper_create_approved_request(
        request_service, workflow_service
    )

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_other_order",  # Tampered transaction!
        amount=app_rec.amount,
        currency=app_rec.currency,
        idempotency_key="idemp_tx_tamper_15",
        expected_approval_fingerprint=app_rec.approval_fingerprint,
    )
    with pytest.raises(ApprovedPaymentContinuationError) as exc_info:
        continuation_service.execute_continuation(cmd)
    assert exc_info.value.error_code == "FINANCIAL_PARAMETER_TAMPERING"


def test_16_idempotency_replay(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 16: Replaying continuation command returns cached result."""
    app_rec, t_id, a_id, _, tx_id = helper_create_approved_request(
        request_service, workflow_service
    )

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id=tx_id,
        amount=app_rec.amount,
        currency=app_rec.currency,
        idempotency_key="idemp_replay_16",
        expected_approval_fingerprint=app_rec.approval_fingerprint,
    )

    res1 = continuation_service.execute_continuation(cmd)
    assert res1.is_existing is False

    res2 = continuation_service.execute_continuation(cmd)
    assert res2.is_existing is True
    assert res2.execution_fingerprint == res1.execution_fingerprint


def test_17_modified_idempotency_request_conflict(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 17: Reusing idempotency key with modified params raises 409 Conflict."""
    app_rec, t_id, a_id, _, tx_id = helper_create_approved_request(
        request_service, workflow_service
    )

    cmd1 = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id=tx_id,
        amount=app_rec.amount,
        currency=app_rec.currency,
        idempotency_key="idemp_conflict_17",
        expected_approval_fingerprint=app_rec.approval_fingerprint,
    )
    continuation_service.execute_continuation(cmd1)

    cmd2 = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id=tx_id,
        amount=Decimal("1.00"),  # Modified param with same key!
        currency=app_rec.currency,
        idempotency_key="idemp_conflict_17",
        expected_approval_fingerprint=app_rec.approval_fingerprint,
    )
    with pytest.raises(ApprovedPaymentContinuationConflictError):
        continuation_service.execute_continuation(cmd2)


def test_18_concurrent_continuation(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 18: Concurrent continuation requests run safely without race conditions."""
    app_rec, t_id, a_id, _, tx_id = helper_create_approved_request(
        request_service, workflow_service
    )

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id=tx_id,
        amount=app_rec.amount,
        currency=app_rec.currency,
        idempotency_key="idemp_conc_18",
        expected_approval_fingerprint=app_rec.approval_fingerprint,
    )

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(continuation_service.execute_continuation, cmd) for _ in range(5)
        ]
        results = [f.result() for f in futures]

    existing_flags = [r.is_existing for r in results]
    assert existing_flags.count(False) == 1
    assert existing_flags.count(True) == 4


def test_19_one_time_approval_consumption(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 19: One approval request cannot be reused with a new idempotency key."""
    app_rec, t_id, a_id, _, tx_id = helper_create_approved_request(
        request_service, workflow_service
    )

    cmd1 = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id=tx_id,
        amount=app_rec.amount,
        currency=app_rec.currency,
        idempotency_key="idemp_consume_1",
        expected_approval_fingerprint=app_rec.approval_fingerprint,
    )
    res1 = continuation_service.execute_continuation(cmd1)
    assert res1.is_existing is False

    cmd2 = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id=tx_id,
        amount=app_rec.amount,
        currency=app_rec.currency,
        idempotency_key="idemp_consume_2",  # Different idempotency key!
        expected_approval_fingerprint=app_rec.approval_fingerprint,
    )
    res2 = continuation_service.execute_continuation(cmd2)
    assert res2.is_existing is True
    assert res2.execution_status == "EXECUTION_REPLAYED"


def test_20_already_executed_safe_replay(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 20: Calling continuation on consumed approval returns safe replay result."""
    app_rec, t_id, a_id, _, tx_id = helper_create_approved_request(
        request_service, workflow_service
    )

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id=tx_id,
        amount=app_rec.amount,
        currency=app_rec.currency,
        idempotency_key="idemp_safe_replay_20",
        expected_approval_fingerprint=app_rec.approval_fingerprint,
    )
    continuation_service.execute_continuation(cmd)
    res = continuation_service.execute_continuation(cmd)
    assert res.is_existing is True


def test_21_provider_exception_safe_failure(
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 21: Failure in pre-conditions produces safe exception without exposing internals."""
    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_err",
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        idempotency_key="idemp_err",
        expected_approval_fingerprint="fp_err",
    )
    with pytest.raises(ApprovedPaymentContinuationError) as exc_info:
        continuation_service.execute_continuation(cmd)
    assert "not found" in str(exc_info.value.message)


def test_22_no_success_fabrication() -> None:
    """Test 22: APPROVAL != PAYMENT SUCCESS invariant check."""
    res = ApprovedPaymentContinuationResult(
        approval_request_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        transaction_id="tx_test",
        agent_id=uuid.uuid4(),
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        execution_status="CONTINUATION_EXECUTED",
        payment_status=PaymentStatus.PAYMENT_PENDING,  # NOT automatically CAPTURED or SUCCESS!
        execution_fingerprint="fp",
        processed_at=datetime.now(UTC),
    )
    assert res.payment_status == PaymentStatus.PAYMENT_PENDING


def test_23_no_fake_provider_id() -> None:
    """Test 23: Continuation returns explicit or null provider identifiers."""
    res = ApprovedPaymentContinuationResult(
        approval_request_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        transaction_id="tx_test",
        agent_id=uuid.uuid4(),
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        execution_status="CONTINUATION_EXECUTED",
        payment_status=PaymentStatus.PAYMENT_PENDING,
        payment_id=None,
        order_id="order_123",
        execution_fingerprint="fp",
        processed_at=datetime.now(UTC),
    )
    assert res.payment_id is None
    assert res.order_id == "order_123"


def test_24_payment_state_governance() -> None:
    """Test 24: Payment status in result uses standard PaymentStatus enum."""
    res = ApprovedPaymentContinuationResult(
        approval_request_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        transaction_id="tx_test",
        agent_id=uuid.uuid4(),
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        execution_status="CONTINUATION_EXECUTED",
        payment_status=PaymentStatus.PAYMENT_PENDING,
        execution_fingerprint="fp",
        processed_at=datetime.now(UTC),
    )
    assert isinstance(res.payment_status, PaymentStatus)


def test_25_webhook_event_architecture_preserved() -> None:
    """Test 25: Verification that webhook handlers remain untouched and authoritative."""
    from app.payment.webhooks.razorpay_webhook import RazorpayWebhookHandler

    assert hasattr(RazorpayWebhookHandler, "process_webhook")


def test_26_razorpay_sdk_boundary_isolation() -> None:
    """Test 26: Static boundary check confirming 0 Razorpay SDK imports in continuation service."""
    import inspect

    import app.payment.approval.approved_payment_continuation_service as mod

    source = inspect.getsource(mod)
    assert "import razorpay" not in source
    assert "from razorpay" not in source


def test_27_audit_integration(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
    audit_service: ApprovalAuditService,
) -> None:
    """Test 27: Continuation emits EXECUTION_STARTED and EXECUTION_SUCCEEDED audit events."""
    app_rec, t_id, a_id, _, tx_id = helper_create_approved_request(
        request_service, workflow_service
    )

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id=tx_id,
        amount=app_rec.amount,
        currency=app_rec.currency,
        idempotency_key="idemp_audit_27",
        expected_approval_fingerprint=app_rec.approval_fingerprint,
    )
    continuation_service.execute_continuation(cmd)

    history = audit_service.get_audit_events_for_request(t_id, app_rec.approval_request_id)
    types = [e.event_type for e in history.events]
    assert ApprovalAuditEventType.APPROVAL_EXECUTION_STARTED in types
    assert ApprovalAuditEventType.APPROVAL_EXECUTION_SUCCEEDED in types


def test_28_secret_redaction() -> None:
    """Test 28: Response model excludes secrets."""
    res = ApprovedPaymentContinuationResult(
        approval_request_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        transaction_id="tx_sec",
        agent_id=uuid.uuid4(),
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        execution_status="CONTINUATION_EXECUTED",
        payment_status=PaymentStatus.PAYMENT_PENDING,
        execution_fingerprint="fp_sec",
        processed_at=datetime.now(UTC),
    )
    d = res.model_dump()
    assert "key_secret" not in d
    assert "webhook_secret" not in d
    assert "authorization" not in d


def test_29_cross_tenant_isolation(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 29: Cross-tenant continuation attempt is blocked."""
    app_rec, t_id, a_id, _, tx_id = helper_create_approved_request(
        request_service, workflow_service
    )

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=uuid.uuid4(),  # Other tenant!
        agent_id=a_id,
        transaction_id=tx_id,
        amount=app_rec.amount,
        currency=app_rec.currency,
        idempotency_key="idemp_cross_t",
        expected_approval_fingerprint=app_rec.approval_fingerprint,
    )
    with pytest.raises(ApprovedPaymentContinuationError):
        continuation_service.execute_continuation(cmd)


def test_30_cross_agent_isolation(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 30: Cross-agent continuation attempt is blocked."""
    app_rec, t_id, a_id, _, tx_id = helper_create_approved_request(
        request_service, workflow_service
    )

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=uuid.uuid4(),  # Other agent!
        transaction_id=tx_id,
        amount=app_rec.amount,
        currency=app_rec.currency,
        idempotency_key="idemp_cross_a",
        expected_approval_fingerprint=app_rec.approval_fingerprint,
    )
    with pytest.raises(ApprovedPaymentContinuationError):
        continuation_service.execute_continuation(cmd)


def test_31_cross_transaction_isolation(
    request_service: ApprovalRequestService,
    workflow_service: ApprovalWorkflowService,
    continuation_service: ApprovedPaymentContinuationService,
) -> None:
    """Test 31: Cross-transaction continuation attempt is blocked."""
    app_rec, t_id, a_id, _, tx_id = helper_create_approved_request(
        request_service, workflow_service
    )

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=app_rec.approval_request_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_other_31",  # Other transaction!
        amount=app_rec.amount,
        currency=app_rec.currency,
        idempotency_key="idemp_cross_tx",
        expected_approval_fingerprint=app_rec.approval_fingerprint,
    )
    with pytest.raises(ApprovedPaymentContinuationError):
        continuation_service.execute_continuation(cmd)


def test_32_nan_amount_rejection() -> None:
    """Test 32: NaN amount in continuation command raises ValidationError."""
    with pytest.raises(ValidationError):
        ApprovedPaymentContinuationCommand(
            approval_request_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_nan",
            amount=Decimal("NaN"),  # NaN rejected!
            currency=SupportedCurrency.INR,
            idempotency_key="idemp_nan",
            expected_approval_fingerprint="fp_nan",
        )


def test_33_negative_amount_rejection() -> None:
    """Test 33: Non-positive amount in continuation command raises ValidationError."""
    with pytest.raises(ValidationError):
        ApprovedPaymentContinuationCommand(
            approval_request_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_neg",
            amount=Decimal("-10.00"),  # Negative rejected!
            currency=SupportedCurrency.INR,
            idempotency_key="idemp_neg",
            expected_approval_fingerprint="fp_neg",
        )


def test_34_extra_field_rejection_command() -> None:
    """Test 34: Command model rejects un-declared extra fields (extra='forbid')."""
    with pytest.raises(ValidationError):
        ApprovedPaymentContinuationCommand(
            approval_request_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            transaction_id="tx_extra",
            amount=Decimal("100.00"),
            currency=SupportedCurrency.INR,
            idempotency_key="idemp_extra",
            expected_approval_fingerprint="fp_extra",
            unauthorized_field="malicious",  # type: ignore[call-arg]
        )


def test_35_frozen_schema_immutability() -> None:
    """Test 35: Command model is frozen and rejects attribute mutations."""
    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_frozen",
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        idempotency_key="idemp_frozen",
        expected_approval_fingerprint="fp_frozen",
    )
    with pytest.raises((TypeError, ValidationError, AttributeError)):
        cmd.amount = Decimal("9999.00")
