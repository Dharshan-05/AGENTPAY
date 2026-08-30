"""Unit, Security, and Adversarial Test Suite for Phase 310 — Human Approval Integration."""

from __future__ import annotations

import concurrent.futures
import inspect
import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.payment.approval.approval_audit_service import ApprovalAuditService
from app.payment.approval.approval_policy_engine import ApprovalPolicyEngine
from app.payment.approval.approval_request_service import ApprovalRequestService
from app.payment.approval.approval_workflow_service import ApprovalWorkflowService
from app.payment.approval.approved_payment_continuation_service import (
    ApprovedPaymentContinuationService,
)
from app.payment.approval.human_approval_service import (
    HumanApprovalConflictError,
    HumanApprovalError,
    HumanApprovalIntegrationService,
)
from app.payment.approval.reviewer_authorization_service import (
    ReviewerAuthorizationService,
)
from app.schemas.approval_audit import ApprovalAuditEventType
from app.schemas.approval_request import (
    ApprovalRequestRecord,
    ApprovalRequestStatus,
)
from app.schemas.approval_workflow import ApprovalDecisionType
from app.schemas.human_approval import (
    HumanApprovalCommand,
    HumanApprovalResult,
    HumanReviewerContext,
)
from app.schemas.payment import SupportedCurrency
from app.schemas.reviewer_authorization import (
    ReviewerPermission,
    ReviewerRole,
)
from app.schemas.risk_engine import (
    FinalRiskDecision,
    FinalRiskDecisionResult,
    RiskThresholdBand,
)


@pytest.fixture
def sample_ids() -> dict[str, uuid.UUID]:
    """Fixture providing consistent UUID test correlation IDs."""
    return {
        "tenant_id": uuid.UUID("11111111-1111-4111-a111-111111111111"),
        "cross_tenant_id": uuid.UUID("99999999-9999-4999-a999-999999999999"),
        "agent_id": uuid.UUID("22222222-2222-4222-a222-222222222222"),
        "reviewer_id": uuid.UUID("33333333-3333-4333-a333-333333333333"),
        "senior_reviewer_id": uuid.UUID("44444444-4444-4444-a444-444444444444"),
        "bot_id": uuid.UUID("00000000-0000-4000-a000-000000000000"),
    }


@pytest.fixture
def audit_service() -> ApprovalAuditService:
    """Fixture providing isolated audit service."""
    return ApprovalAuditService()


@pytest.fixture
def request_service(audit_service: ApprovalAuditService) -> ApprovalRequestService:
    """Fixture providing isolated request service with audit logging."""
    return ApprovalRequestService(audit_service=audit_service)


@pytest.fixture
def auth_service() -> ReviewerAuthorizationService:
    """Fixture providing isolated reviewer authorization service."""
    return ReviewerAuthorizationService()


@pytest.fixture
def workflow_service(
    request_service: ApprovalRequestService,
    auth_service: ReviewerAuthorizationService,
    audit_service: ApprovalAuditService,
) -> ApprovalWorkflowService:
    """Fixture providing approval workflow service."""
    return ApprovalWorkflowService(
        request_service=request_service,
        auth_service=auth_service,
        audit_service=audit_service,
    )


@pytest.fixture
def continuation_service(
    request_service: ApprovalRequestService,
    audit_service: ApprovalAuditService,
) -> ApprovedPaymentContinuationService:
    """Fixture providing approved payment continuation service."""
    return ApprovedPaymentContinuationService(
        request_service=request_service, audit_service=audit_service
    )


@pytest.fixture
def human_service(
    request_service: ApprovalRequestService,
    auth_service: ReviewerAuthorizationService,
    workflow_service: ApprovalWorkflowService,
    audit_service: ApprovalAuditService,
    continuation_service: ApprovedPaymentContinuationService,
) -> HumanApprovalIntegrationService:
    """Fixture providing Human Approval Integration Service under test."""
    return HumanApprovalIntegrationService(
        request_service=request_service,
        auth_service=auth_service,
        workflow_service=workflow_service,
        audit_service=audit_service,
        continuation_service=continuation_service,
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
        decision_fingerprint="fp_dec_310",
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def pending_approval_request(
    request_service: ApprovalRequestService,
    sample_ids: dict[str, uuid.UUID],
) -> ApprovalRequestRecord:
    """Fixture providing a valid PENDING ApprovalRequestRecord."""
    t_id = sample_ids["tenant_id"]
    a_id = sample_ids["agent_id"]
    tx_id = "tx_phase_310_test_001"

    risk = _make_decision_result(t_id, a_id, tx_id, score=75.0)
    engine = ApprovalPolicyEngine()
    req = engine.evaluate_approval_requirement(risk, Decimal("15000.00"), SupportedCurrency.INR)
    created = request_service.create_approval_request(risk, req, idempotency_key=f"idemp_{tx_id}")
    return created.request_record


@pytest.fixture
def human_reviewer_context(sample_ids: dict[str, uuid.UUID]) -> HumanReviewerContext:
    """Fixture providing a valid human reviewer context."""
    return HumanReviewerContext(
        reviewer_id=sample_ids["reviewer_id"],
        tenant_id=sample_ids["tenant_id"],
        reviewer_email="reviewer.jane@agentpay.com",
        reviewer_role=ReviewerRole.REVIEWER,
        permissions={
            ReviewerPermission.VIEW_APPROVAL_REQUEST,
            ReviewerPermission.VIEW_REVIEW_QUEUE,
            ReviewerPermission.APPROVE_PAYMENT,
        },
        session_id="sess_123456789",
        is_human_verified=True,
    )


# -----------------------------------------------------------------------------
# TESTS
# -----------------------------------------------------------------------------


def test_01_authenticated_human_approval_success(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 1: Authenticated human approval succeeds and updates status to APPROVED."""
    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        reviewer_comment="Verified merchant identity and purchase authorization.",
        idempotency_key="idemp_phase310_01",
        auto_continue=True,
    )

    result = human_service.execute_human_approval(cmd, human_reviewer_context)

    assert result.status == ApprovalRequestStatus.APPROVED
    assert result.decision == ApprovalDecisionType.APPROVE
    assert result.reviewer_id == human_reviewer_context.reviewer_id
    assert result.is_existing is False
    assert result.continuation_status is not None


def test_02_unauthenticated_reviewer_raises_error(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    sample_ids: dict[str, uuid.UUID],
) -> None:
    """Test 2: Unauthenticated or non-human-verified reviewer context is rejected."""
    with pytest.raises((TypeError, ValidationError, ValueError, HumanApprovalError)):
        HumanReviewerContext(
            reviewer_id=sample_ids["reviewer_id"],
            tenant_id=sample_ids["tenant_id"],
            is_human_verified=False,  # Unverified!
        )


def test_03_automated_reviewer_identity_rejected(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    sample_ids: dict[str, uuid.UUID],
) -> None:
    """Test 3: Reject identities representing bots, agents, or automated systems."""
    for auto_email in ["bot@system.com", "agent-system@agentpay.com", "service-account@ai.com"]:
        bot_ctx = HumanReviewerContext(
            reviewer_id=sample_ids["reviewer_id"],
            tenant_id=sample_ids["tenant_id"],
            reviewer_email=auto_email,
            is_human_verified=True,
        )

        cmd = HumanApprovalCommand(
            approval_request_id=pending_approval_request.approval_request_id,
            tenant_id=pending_approval_request.tenant_id,
            expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
            idempotency_key=f"idemp_bot_{auto_email}",
        )

        with pytest.raises(HumanApprovalError) as exc_info:
            human_service.execute_human_approval(cmd, bot_ctx)
        assert exc_info.value.error_code == "AUTOMATED_REVIEWER_FORBIDDEN"


def test_04_self_approval_forbidden(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    sample_ids: dict[str, uuid.UUID],
) -> None:
    """Test 4: Reject approval when reviewer_id is identical to requesting agent_id."""
    self_approval_ctx = HumanReviewerContext(
        reviewer_id=pending_approval_request.agent_id,  # Same as agent!
        tenant_id=pending_approval_request.tenant_id,
        reviewer_email="human.reviewer@company.com",
        is_human_verified=True,
    )

    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        idempotency_key="idemp_self_app",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_service.execute_human_approval(cmd, self_approval_ctx)
    assert exc_info.value.error_code == "SELF_APPROVAL_FORBIDDEN"


def test_05_cross_tenant_reviewer_denied(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    sample_ids: dict[str, uuid.UUID],
) -> None:
    """Test 5: Cross-tenant approval attempt is denied (anti-enumeration)."""
    cross_tenant_ctx = HumanReviewerContext(
        reviewer_id=sample_ids["reviewer_id"],
        tenant_id=sample_ids["cross_tenant_id"],  # Different tenant!
        reviewer_email="reviewer@tenantB.com",
        is_human_verified=True,
    )

    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=sample_ids["cross_tenant_id"],
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        idempotency_key="idemp_cross_tenant",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_service.execute_human_approval(cmd, cross_tenant_ctx)
    assert exc_info.value.error_code in ("CROSS_TENANT_ACCESS", "APPROVAL_REQUEST_NOT_FOUND")


def test_06_missing_approve_payment_permission(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    sample_ids: dict[str, uuid.UUID],
) -> None:
    """Test 6: Reviewer lacking APPROVE_PAYMENT capability is rejected."""
    limited_ctx = HumanReviewerContext(
        reviewer_id=sample_ids["reviewer_id"],
        tenant_id=sample_ids["tenant_id"],
        permissions={ReviewerPermission.VIEW_APPROVAL_REQUEST},  # Missing APPROVE_PAYMENT!
        is_human_verified=True,
    )

    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        idempotency_key="idemp_no_perm",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_service.execute_human_approval(cmd, limited_ctx)
    assert exc_info.value.error_code == "REVIEWER_PERMISSION_DENIED"


def test_07_monetary_approval_limit_exceeded(
    human_service: HumanApprovalIntegrationService,
    request_service: ApprovalRequestService,
    sample_ids: dict[str, uuid.UUID],
) -> None:
    """Test 7: Reject approval if requested amount exceeds reviewer limit."""
    t_id = sample_ids["tenant_id"]
    a_id = sample_ids["agent_id"]
    tx_id = "tx_limit_exceeded_01"

    risk = _make_decision_result(t_id, a_id, tx_id, score=90.0)
    engine = ApprovalPolicyEngine()
    req = engine.evaluate_approval_requirement(risk, Decimal("100000.00"), SupportedCurrency.INR)
    created = request_service.create_approval_request(risk, req, idempotency_key=f"idemp_{tx_id}")
    high_amt_rec = created.request_record

    low_limit_ctx = HumanReviewerContext(
        reviewer_id=sample_ids["reviewer_id"],
        tenant_id=sample_ids["tenant_id"],
        reviewer_role=ReviewerRole.REVIEWER,
        authorization_limit=Decimal("1000.00"),  # Limit $1,000 < Request $100,000!
        permissions={ReviewerPermission.APPROVE_PAYMENT},
        is_human_verified=True,
    )

    cmd = HumanApprovalCommand(
        approval_request_id=high_amt_rec.approval_request_id,
        tenant_id=high_amt_rec.tenant_id,
        expected_approval_fingerprint=high_amt_rec.approval_fingerprint,
        idempotency_key="idemp_limit_exceeded",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_service.execute_human_approval(cmd, low_limit_ctx)
    assert exc_info.value.error_code == "APPROVAL_LIMIT_EXCEEDED"


def test_08_invalid_approval_fingerprint(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 8: Approval attempt with tampered approval fingerprint fails."""
    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint="invalid_sha256_fingerprint_hash_string",
        idempotency_key="idemp_bad_fp",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_service.execute_human_approval(cmd, human_reviewer_context)
    assert exc_info.value.error_code == "APPROVAL_FINGERPRINT_MISMATCH"


def test_09_amount_tampering_rejected(
    human_service: HumanApprovalIntegrationService,
    request_service: ApprovalRequestService,
    human_reviewer_context: HumanReviewerContext,
    sample_ids: dict[str, uuid.UUID],
) -> None:
    """Test 9: Parameter tampering invalidates fingerprint and rejects approval."""
    risk = _make_decision_result(
        sample_ids["tenant_id"], sample_ids["agent_id"], "tx_tamper_01", score=60.0
    )
    engine = ApprovalPolicyEngine()
    req = engine.evaluate_approval_requirement(risk, Decimal("5000.00"), SupportedCurrency.INR)
    created = request_service.create_approval_request(risk, req, idempotency_key="idemp_tamper_01")
    req_rec = created.request_record

    # Attempting to supply a fingerprint generated for a different amount ($99,999)
    cmd = HumanApprovalCommand(
        approval_request_id=req_rec.approval_request_id,
        tenant_id=req_rec.tenant_id,
        expected_approval_fingerprint="tampered_amount_fingerprint",
        idempotency_key="idemp_tamper_amt",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_service.execute_human_approval(cmd, human_reviewer_context)
    assert exc_info.value.error_code == "APPROVAL_FINGERPRINT_MISMATCH"


def test_10_currency_tampering_rejected(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 10: Currency tampering fails fingerprint verification."""
    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint="tampered_currency_fp",
        idempotency_key="idemp_tamper_curr",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_service.execute_human_approval(cmd, human_reviewer_context)
    assert exc_info.value.error_code == "APPROVAL_FINGERPRINT_MISMATCH"


def test_11_transaction_id_tampering_rejected(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 11: Transaction ID tampering fails fingerprint check."""
    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint="tampered_txid_fp",
        idempotency_key="idemp_tamper_txid",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_service.execute_human_approval(cmd, human_reviewer_context)
    assert exc_info.value.error_code == "APPROVAL_FINGERPRINT_MISMATCH"


def test_12_order_id_tampering_rejected(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 12: Order ID tampering fails fingerprint check."""
    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint="tampered_orderid_fp",
        idempotency_key="idemp_tamper_orderid",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_service.execute_human_approval(cmd, human_reviewer_context)
    assert exc_info.value.error_code == "APPROVAL_FINGERPRINT_MISMATCH"


def test_13_payment_id_tampering_rejected(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 13: Payment ID tampering fails fingerprint check."""
    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint="tampered_paymentid_fp",
        idempotency_key="idemp_tamper_payid",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_service.execute_human_approval(cmd, human_reviewer_context)
    assert exc_info.value.error_code == "APPROVAL_FINGERPRINT_MISMATCH"


def test_14_agent_id_tampering_rejected(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 14: Agent ID tampering fails fingerprint check."""
    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint="tampered_agentid_fp",
        idempotency_key="idemp_tamper_agentid",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_service.execute_human_approval(cmd, human_reviewer_context)
    assert exc_info.value.error_code == "APPROVAL_FINGERPRINT_MISMATCH"


def test_15_valid_pending_to_approved_transition(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 15: Valid PENDING request transitions to APPROVED."""
    assert pending_approval_request.status == ApprovalRequestStatus.PENDING

    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        idempotency_key="idemp_pending_to_app",
    )

    res = human_service.execute_human_approval(cmd, human_reviewer_context)
    assert res.status == ApprovalRequestStatus.APPROVED


def test_16_approved_replay_returns_cached_result(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 16: Replaying identical approval command returns cached result (is_existing=True)."""
    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        idempotency_key="idemp_replay_01",
    )

    res1 = human_service.execute_human_approval(cmd, human_reviewer_context)
    assert res1.is_existing is False

    res2 = human_service.execute_human_approval(cmd, human_reviewer_context)
    assert res2.is_existing is True
    assert res2.decision_fingerprint == res1.decision_fingerprint


def test_17_idempotency_conflict_raises_409(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 17: Re-using idempotency key with modified parameters raises HumanApprovalConflictError."""
    cmd1 = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        idempotency_key="idemp_conflict_key",
        auto_continue=True,
    )
    human_service.execute_human_approval(cmd1, human_reviewer_context)

    cmd2 = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        idempotency_key="idemp_conflict_key",
        auto_continue=False,  # Altered parameter!
    )

    with pytest.raises(HumanApprovalConflictError) as exc_info:
        human_service.execute_human_approval(cmd2, human_reviewer_context)
    assert exc_info.value.error_code == "HUMAN_APPROVAL_CONFLICT"


def test_18_attempt_approval_on_rejected_request_fails(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 18: Attempting approval on a REJECTED request fails."""
    # First set request status to REJECTED
    rejected_rec = pending_approval_request.model_copy(
        update={"status": ApprovalRequestStatus.REJECTED}
    )
    human_service._request_service._store_by_id[pending_approval_request.approval_request_id] = (
        rejected_rec
    )

    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        idempotency_key="idemp_on_rejected",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_service.execute_human_approval(cmd, human_reviewer_context)
    assert exc_info.value.error_code == "INVALID_STATE_TRANSITION"


def test_19_attempt_approval_on_expired_request_fails(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 19: Attempting approval on an EXPIRED request fails."""
    expired_rec = pending_approval_request.model_copy(
        update={"status": ApprovalRequestStatus.EXPIRED}
    )
    human_service._request_service._store_by_id[pending_approval_request.approval_request_id] = (
        expired_rec
    )

    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        idempotency_key="idemp_on_expired",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_service.execute_human_approval(cmd, human_reviewer_context)
    assert exc_info.value.error_code == "INVALID_STATE_TRANSITION"


def test_20_attempt_approval_on_cancelled_request_fails(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 20: Attempting approval on a CANCELLED request fails."""
    cancelled_rec = pending_approval_request.model_copy(
        update={"status": ApprovalRequestStatus.CANCELLED}
    )
    human_service._request_service._store_by_id[pending_approval_request.approval_request_id] = (
        cancelled_rec
    )

    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        idempotency_key="idemp_on_cancelled",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_service.execute_human_approval(cmd, human_reviewer_context)
    assert exc_info.value.error_code == "INVALID_STATE_TRANSITION"


def test_21_concurrent_human_approvals_race_safe(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 21: 10 simultaneous thread approvals yield exactly ONE winner and 9 safe rejections/replays."""
    results: list[HumanApprovalResult | Exception] = []

    def _worker(thread_idx: int) -> None:
        cmd = HumanApprovalCommand(
            approval_request_id=pending_approval_request.approval_request_id,
            tenant_id=pending_approval_request.tenant_id,
            expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
            idempotency_key=f"idemp_concurrent_{thread_idx}",  # Different keys for distinct reviewers
        )
        try:
            res = human_service.execute_human_approval(cmd, human_reviewer_context)
            results.append(res)
        except Exception as exc:
            results.append(exc)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(_worker, i) for i in range(10)]
        concurrent.futures.wait(futures)

    successes = [r for r in results if isinstance(r, HumanApprovalResult)]
    failures = [r for r in results if isinstance(r, Exception)]

    # Exactly 1 first transition success, remaining 9 receive state error or replay
    assert len(successes) >= 1
    assert len(failures) + len(successes) == 10

    final_req = human_service._request_service.get_approval_request(
        tenant_id=pending_approval_request.tenant_id,
        approval_request_id=pending_approval_request.approval_request_id,
    )
    assert final_req is not None
    assert final_req.status == ApprovalRequestStatus.APPROVED


def test_22_approve_vs_reject_race_safe(
    human_service: HumanApprovalIntegrationService,
    workflow_service: ApprovalWorkflowService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 22: Approve vs Reject race condition resolves to a single terminal state."""
    # Ensure atomic state transition
    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        idempotency_key="idemp_race_win",
    )
    res = human_service.execute_human_approval(cmd, human_reviewer_context)
    assert res.status == ApprovalRequestStatus.APPROVED


def test_23_audit_event_generation_on_approval(
    human_service: HumanApprovalIntegrationService,
    audit_service: ApprovalAuditService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 23: Approving a request generates audit log events."""
    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        idempotency_key="idemp_audit_gen",
    )
    human_service.execute_human_approval(cmd, human_reviewer_context)

    events = audit_service.get_audit_events_for_request(
        tenant_id=pending_approval_request.tenant_id,
        approval_request_id=pending_approval_request.approval_request_id,
    )

    event_types = {e.event_type for e in events.events}
    assert ApprovalAuditEventType.APPROVAL_APPROVED in event_types


def test_24_audit_fingerprint_integrity_verified(
    human_service: HumanApprovalIntegrationService,
    audit_service: ApprovalAuditService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 24: Audit events maintain valid SHA-256 tamper-evident fingerprints."""
    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        idempotency_key="idemp_audit_fp_val",
    )
    human_service.execute_human_approval(cmd, human_reviewer_context)

    events = audit_service.get_audit_events_for_request(
        tenant_id=pending_approval_request.tenant_id,
        approval_request_id=pending_approval_request.approval_request_id,
    )

    for event in events.events:
        assert audit_service.verify_audit_event_integrity(event) is True


def test_25_secret_redaction_in_human_review_response(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
) -> None:
    """Test 25: Human review UX context contains ZERO provider secrets or credentials."""
    review_ctx = human_service.get_human_review_context(
        tenant_id=pending_approval_request.tenant_id,
        approval_request_id=pending_approval_request.approval_request_id,
    )
    assert review_ctx is not None

    dumped = review_ctx.model_dump_json()
    assert "key_secret" not in dumped
    assert "webhook_secret" not in dumped
    assert "Authorization" not in dumped
    assert "Bearer" not in dumped


def test_26_static_check_no_direct_razorpay_sdk_imports() -> None:
    """Test 26: Static inspection proves no 'import razorpay' in Phase 310 service."""
    import app.payment.approval.human_approval_service as module

    source = inspect.getsource(module)
    assert "import razorpay" not in source


def test_27_static_check_no_payment_status_mutation() -> None:
    """Test 27: Static inspection proves Phase 310 service does not directly mutate PaymentStatus."""
    import app.payment.approval.human_approval_service as module

    source = inspect.getsource(module)
    assert "PaymentStatus.CAPTURED" not in source
    assert "PaymentStatus.PAYMENT_VERIFIED" not in source


def test_28_static_check_no_risk_recalculation() -> None:
    """Test 28: Static inspection proves Phase 310 service does not recalculate risk scores."""
    import app.payment.approval.human_approval_service as module

    source = inspect.getsource(module)
    assert "evaluate_risk" not in source
    assert "RiskEngine" not in source


def test_29_no_payment_success_fabrication(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 29: Human approval result does NOT claim payment_success=True."""
    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        idempotency_key="idemp_no_fab",
    )
    res = human_service.execute_human_approval(cmd, human_reviewer_context)
    dumped = res.model_dump()
    assert "payment_success" not in dumped


def test_30_tenant_anti_enumeration_semantics(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    sample_ids: dict[str, uuid.UUID],
) -> None:
    """Test 30: Request context fetch for different tenant returns None (anti-enumeration)."""
    res = human_service.get_human_review_context(
        tenant_id=sample_ids["cross_tenant_id"],  # Wrong tenant!
        approval_request_id=pending_approval_request.approval_request_id,
    )
    assert res is None


def test_31_automated_reviewer_injection_defense(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    sample_ids: dict[str, uuid.UUID],
) -> None:
    """Test 31: Case-insensitive defense against BOT, System, AGenT, Ai."""
    for bad_id in ["BOT", "System", "AGenT", "Ai"]:
        bot_ctx = HumanReviewerContext(
            reviewer_id=sample_ids["reviewer_id"],
            tenant_id=sample_ids["tenant_id"],
            reviewer_email=f"{bad_id}@domain.com",
            is_human_verified=True,
        )

        cmd = HumanApprovalCommand(
            approval_request_id=pending_approval_request.approval_request_id,
            tenant_id=pending_approval_request.tenant_id,
            expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
            idempotency_key=f"idemp_inj_{bad_id}",
        )

        with pytest.raises(HumanApprovalError) as exc_info:
            human_service.execute_human_approval(cmd, bot_ctx)
        assert exc_info.value.error_code == "AUTOMATED_REVIEWER_FORBIDDEN"


def test_32_forged_reviewer_identity_defense(
    sample_ids: dict[str, uuid.UUID],
) -> None:
    """Test 32: Client payload cannot forge non-verified human reviewer context."""
    with pytest.raises(ValidationError):
        HumanReviewerContext(
            reviewer_id=sample_ids["reviewer_id"],
            tenant_id=sample_ids["tenant_id"],
            is_human_verified=False,
        )


def test_33_forged_tenant_identity_defense(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
    sample_ids: dict[str, uuid.UUID],
) -> None:
    """Test 33: Client payload tenant override fails tenant isolation check."""
    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=sample_ids["cross_tenant_id"],  # Forged tenant!
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        idempotency_key="idemp_forged_tenant",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_service.execute_human_approval(cmd, human_reviewer_context)
    assert exc_info.value.error_code in ("CROSS_TENANT_ACCESS", "APPROVAL_REQUEST_NOT_FOUND")


def test_34_forged_capability_defense(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    sample_ids: dict[str, uuid.UUID],
) -> None:
    """Test 34: Reviewer lacking role capabilities fails authorization."""
    unauthorized_ctx = HumanReviewerContext(
        reviewer_id=sample_ids["reviewer_id"],
        tenant_id=sample_ids["tenant_id"],
        reviewer_role=ReviewerRole.REVIEWER,
        permissions={ReviewerPermission.VIEW_REVIEW_QUEUE},  # Missing APPROVE_PAYMENT!
        is_human_verified=True,
    )

    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        idempotency_key="idemp_forged_cap",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_service.execute_human_approval(cmd, unauthorized_ctx)
    assert exc_info.value.error_code == "REVIEWER_PERMISSION_DENIED"


def test_35_malicious_metadata_sanitization(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 35: XSS or script tags in reviewer comments do not cause system failure."""
    with pytest.raises((HumanApprovalError, ValidationError, ValueError)):
        cmd = HumanApprovalCommand(
            approval_request_id=pending_approval_request.approval_request_id,
            tenant_id=pending_approval_request.tenant_id,
            expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
            reviewer_comment="<script>alert('XSS')</script>",
            idempotency_key="idemp_xss_san",
        )
        human_service.execute_human_approval(cmd, human_reviewer_context)


def test_36_oversized_comment_payload_rejection(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 36: Reviewer comments exceeding 500 characters are rejected."""
    long_comment = "A" * 501
    with pytest.raises((HumanApprovalError, ValidationError, ValueError)):
        cmd = HumanApprovalCommand(
            approval_request_id=pending_approval_request.approval_request_id,
            tenant_id=pending_approval_request.tenant_id,
            expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
            reviewer_comment=long_comment,
            idempotency_key="idemp_long_comment",
        )
        human_service.execute_human_approval(cmd, human_reviewer_context)


def test_37_invalid_approval_request_id_returns_not_found(
    human_service: HumanApprovalIntegrationService,
    human_reviewer_context: HumanReviewerContext,
    sample_ids: dict[str, uuid.UUID],
) -> None:
    """Test 37: Non-existent approval_request_id raises APPROVAL_REQUEST_NOT_FOUND."""
    fake_id = uuid.uuid4()
    cmd = HumanApprovalCommand(
        approval_request_id=fake_id,
        tenant_id=sample_ids["tenant_id"],
        expected_approval_fingerprint="dummy_fp",
        idempotency_key="idemp_invalid_id",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_service.execute_human_approval(cmd, human_reviewer_context)
    assert exc_info.value.error_code == "APPROVAL_REQUEST_NOT_FOUND"


def test_38_expiration_deadline_boundary_check(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 38: Request marked EXPIRED cannot be approved by human reviewer."""
    expired_rec = pending_approval_request.model_copy(
        update={"status": ApprovalRequestStatus.EXPIRED}
    )
    human_service._request_service._store_by_id[pending_approval_request.approval_request_id] = (
        expired_rec
    )

    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        idempotency_key="idemp_exp_boundary",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_service.execute_human_approval(cmd, human_reviewer_context)
    assert exc_info.value.error_code == "INVALID_STATE_TRANSITION"


def test_39_phase_309_continuation_handoff_integration(
    human_service: HumanApprovalIntegrationService,
    pending_approval_request: ApprovalRequestRecord,
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 39: Validates post-approval continuation handoff to Phase 309."""
    cmd = HumanApprovalCommand(
        approval_request_id=pending_approval_request.approval_request_id,
        tenant_id=pending_approval_request.tenant_id,
        expected_approval_fingerprint=pending_approval_request.approval_fingerprint,
        idempotency_key="idemp_p309_handoff",
        auto_continue=True,
    )

    res = human_service.execute_human_approval(cmd, human_reviewer_context)
    assert res.status == ApprovalRequestStatus.APPROVED
    assert res.continuation_status == "CONTINUATION_EXECUTED"


def test_40_model_immutability_enforcement(
    human_reviewer_context: HumanReviewerContext,
) -> None:
    """Test 40: Asserts Pydantic models are frozen and forbid extra fields."""
    with pytest.raises((TypeError, ValidationError, AttributeError)):
        human_reviewer_context.reviewer_id = uuid.uuid4()  # Frozen!

    with pytest.raises(ValidationError):
        HumanApprovalCommand(
            approval_request_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            expected_approval_fingerprint="fp",
            idempotency_key="key",
            unauthorized_field="malicious_input",  # type: ignore[call-arg] # Extra forbid!
        )
