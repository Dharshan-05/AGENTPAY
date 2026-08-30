"""Unit, Security & Adversarial Tests for Phase 306 — Rejection Workflow."""

from __future__ import annotations

import inspect
import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.payment.approval.approval_policy_engine import ApprovalPolicyEngine
from app.payment.approval.approval_rejection_service import (
    ApprovalRejectionConflictError,
    ApprovalRejectionError,
    ApprovalRejectionService,
)
from app.payment.approval.approval_request_service import ApprovalRequestService
from app.payment.approval.reviewer_authorization_service import (
    ReviewerAuthorizationService,
)
from app.schemas.approval_rejection import (
    ApprovalRejectionCommand,
    ApprovalRejectionResult,
    RejectionReason,
)
from app.schemas.approval_request import ApprovalRequestStatus
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
    tenant_id: uuid.UUID,
    agent_id: uuid.UUID,
    tx_id: str,
    score: float = 45.0,
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
        decision_fingerprint="fp_dec_306",
        created_at=datetime.now(UTC),
    )


def test_01_pending_to_rejected_success() -> None:
    """1. Test PENDING -> REJECTED state transition succeeds when authorized."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()
    tx_id = "tx_rej_01"

    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("15000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_01")
    req_id = created.request_record.approval_request_id

    auth_svc = ReviewerAuthorizationService()
    rej_svc = ApprovalRejectionService(request_service=req_svc, auth_service=auth_svc)

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id,
        tenant_id=tenant_id,
        reviewer_role=ReviewerRole.REVIEWER,
        permissions={
            ReviewerPermission.VIEW_APPROVAL_REQUEST,
            ReviewerPermission.REJECT_PAYMENT,
        },
    )

    cmd = ApprovalRejectionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        rejection_reason=RejectionReason.HIGH_RISK_SUSPECTED,
        reviewer_comment="Rejected due to suspicious IP activity.",
        idempotency_key="idemp_rej_01",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    res = rej_svc.reject_request(cmd)

    assert isinstance(res, ApprovalRejectionResult)
    assert res.previous_status == ApprovalRequestStatus.PENDING
    assert res.resulting_status == ApprovalRequestStatus.REJECTED
    assert res.rejection_reason == RejectionReason.HIGH_RISK_SUSPECTED
    assert res.is_existing is False
    assert len(res.decision_fingerprint) == 64

    # Verify status in request_service storage is now REJECTED
    updated_req = req_svc.get_approval_request(tenant_id, req_id)
    assert updated_req is not None
    assert updated_req.status == ApprovalRequestStatus.REJECTED


def test_02_approved_state_cannot_be_rejected() -> None:
    """2. Security Test: Already APPROVED request cannot be transitioned to REJECTED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()
    tx_id = "tx_rej_02"

    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_02")
    req_id = created.request_record.approval_request_id

    # Mutate to APPROVED
    req_svc._store_by_id[req_id] = req_svc._store_by_id[req_id].model_copy(
        update={"status": ApprovalRequestStatus.APPROVED}
    )

    auth_svc = ReviewerAuthorizationService()
    rej_svc = ApprovalRejectionService(request_service=req_svc, auth_service=auth_svc)

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    cmd = ApprovalRejectionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        rejection_reason=RejectionReason.POLICY_VIOLATION,
        idempotency_key="idemp_rej_02",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    with pytest.raises(ApprovalRejectionError) as exc_info:
        rej_svc.reject_request(cmd)

    assert exc_info.value.error_code == "INVALID_STATE_TRANSITION"


def test_03_rejection_idempotent_replay() -> None:
    """3. Test duplicate rejection command with same key replays existing result."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()
    tx_id = "tx_rej_03"

    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_03")
    req_id = created.request_record.approval_request_id

    auth_svc = ReviewerAuthorizationService()
    rej_svc = ApprovalRejectionService(request_service=req_svc, auth_service=auth_svc)

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    cmd = ApprovalRejectionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        rejection_reason=RejectionReason.UNAUTHORIZED_TRANSACTION,
        idempotency_key="idemp_rej_03",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    res1 = rej_svc.reject_request(cmd)
    res2 = rej_svc.reject_request(cmd)

    assert res1.is_existing is False
    assert res2.is_existing is True
    assert res1.decision_fingerprint == res2.decision_fingerprint


def test_04_expired_state_cannot_be_rejected() -> None:
    """4. Security Test: EXPIRED state request cannot be transitioned to REJECTED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    decision = _make_decision_result(tenant_id, agent_id, "tx_rej_04")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_04")
    req_id = created.request_record.approval_request_id

    req_svc._store_by_id[req_id] = req_svc._store_by_id[req_id].model_copy(
        update={"status": ApprovalRequestStatus.EXPIRED}
    )

    auth_svc = ReviewerAuthorizationService()
    rej_svc = ApprovalRejectionService(request_service=req_svc, auth_service=auth_svc)
    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    cmd = ApprovalRejectionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        rejection_reason=RejectionReason.OTHER,
        idempotency_key="idemp_rej_04",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    with pytest.raises(ApprovalRejectionError) as exc_info:
        rej_svc.reject_request(cmd)

    assert exc_info.value.error_code == "INVALID_STATE_TRANSITION"


def test_05_cancelled_state_cannot_be_rejected() -> None:
    """5. Security Test: CANCELLED state request cannot be transitioned to REJECTED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    decision = _make_decision_result(tenant_id, agent_id, "tx_rej_05")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_05")
    req_id = created.request_record.approval_request_id

    req_svc._store_by_id[req_id] = req_svc._store_by_id[req_id].model_copy(
        update={"status": ApprovalRequestStatus.CANCELLED}
    )

    auth_svc = ReviewerAuthorizationService()
    rej_svc = ApprovalRejectionService(request_service=req_svc, auth_service=auth_svc)
    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    cmd = ApprovalRejectionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        rejection_reason=RejectionReason.OTHER,
        idempotency_key="idemp_rej_05",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    with pytest.raises(ApprovalRejectionError) as exc_info:
        rej_svc.reject_request(cmd)

    assert exc_info.value.error_code == "INVALID_STATE_TRANSITION"


def test_06_cross_tenant_rejection_denied() -> None:
    """6. Security Test: Cross-tenant reviewer rejection fails closed (CROSS_TENANT_ACCESS)."""
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    decision = _make_decision_result(tenant_a, agent_id, "tx_rej_06")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_06")
    req_id = created.request_record.approval_request_id

    auth_svc = ReviewerAuthorizationService()
    rej_svc = ApprovalRejectionService(request_service=req_svc, auth_service=auth_svc)

    # Reviewer belongs to Tenant B!
    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_b, reviewer_role=ReviewerRole.APPROVAL_ADMIN
    )

    cmd = ApprovalRejectionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_a,
        reviewer_context=reviewer,
        rejection_reason=RejectionReason.HIGH_RISK_SUSPECTED,
        idempotency_key="idemp_rej_06",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    with pytest.raises(ApprovalRejectionError) as exc_info:
        rej_svc.reject_request(cmd)

    assert exc_info.value.error_code == "CROSS_TENANT_ACCESS"


def test_07_request_not_found_fails() -> None:
    """7. Security Test: Non-existent request ID raises APPROVAL_REQUEST_NOT_FOUND."""
    tenant_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    req_svc = ApprovalRequestService()
    auth_svc = ReviewerAuthorizationService()
    rej_svc = ApprovalRejectionService(request_service=req_svc, auth_service=auth_svc)

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    cmd = ApprovalRejectionCommand(
        approval_request_id=uuid.uuid4(),
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        rejection_reason=RejectionReason.OTHER,
        idempotency_key="idemp_rej_07",
        expected_approval_fingerprint="fp_dummy",
    )

    with pytest.raises(ApprovalRejectionError) as exc_info:
        rej_svc.reject_request(cmd)

    assert exc_info.value.error_code == "APPROVAL_REQUEST_NOT_FOUND"


def test_08_self_rejection_forbidden() -> None:
    """8. Security Test: AI Agent attempting self-rejection fails closed."""
    tenant_id = uuid.uuid4()
    same_id = uuid.uuid4()  # Agent and Reviewer share same ID!

    decision = _make_decision_result(tenant_id, same_id, "tx_rej_08")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_08")
    req_id = created.request_record.approval_request_id

    auth_svc = ReviewerAuthorizationService()
    rej_svc = ApprovalRejectionService(request_service=req_svc, auth_service=auth_svc)

    reviewer = TrustedReviewerContext(
        reviewer_id=same_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.APPROVAL_ADMIN
    )

    cmd = ApprovalRejectionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        rejection_reason=RejectionReason.OTHER,
        idempotency_key="idemp_rej_08",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    with pytest.raises(ApprovalRejectionError) as exc_info:
        rej_svc.reject_request(cmd)

    assert exc_info.value.error_code == "SELF_APPROVAL_FORBIDDEN"


def test_09_missing_reject_permission_denied() -> None:
    """9. Security Test: Reviewer lacking REJECT_PAYMENT permission is denied."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    decision = _make_decision_result(tenant_id, agent_id, "tx_rej_09")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_09")
    req_id = created.request_record.approval_request_id

    auth_svc = ReviewerAuthorizationService()
    rej_svc = ApprovalRejectionService(request_service=req_svc, auth_service=auth_svc)

    # Reviewer with view-only permissions
    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id,
        tenant_id=tenant_id,
        reviewer_role=ReviewerRole.REVIEWER,
        permissions={ReviewerPermission.VIEW_APPROVAL_REQUEST},
    )

    cmd = ApprovalRejectionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        rejection_reason=RejectionReason.OTHER,
        idempotency_key="idemp_rej_09",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    with pytest.raises(ApprovalRejectionError) as exc_info:
        rej_svc.reject_request(cmd)

    assert exc_info.value.error_code == "REVIEWER_PERMISSION_DENIED"


def test_10_fingerprint_mismatch_denied() -> None:
    """10. Security Test: Approval fingerprint mismatch raises APPROVAL_FINGERPRINT_MISMATCH."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    decision = _make_decision_result(tenant_id, agent_id, "tx_rej_10")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_10")
    req_id = created.request_record.approval_request_id

    auth_svc = ReviewerAuthorizationService()
    rej_svc = ApprovalRejectionService(request_service=req_svc, auth_service=auth_svc)
    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    cmd = ApprovalRejectionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        rejection_reason=RejectionReason.OTHER,
        idempotency_key="idemp_rej_10",
        expected_approval_fingerprint="fp_tampered_10",  # Tampered fingerprint!
    )

    with pytest.raises(ApprovalRejectionError) as exc_info:
        rej_svc.reject_request(cmd)

    assert exc_info.value.error_code == "APPROVAL_FINGERPRINT_MISMATCH"


def test_11_idempotency_conflict_raises_409() -> None:
    """11. Security Test: Same idempotency key with modified parameters raises 409 Conflict."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    decision = _make_decision_result(tenant_id, agent_id, "tx_rej_11")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_11")
    req_id = created.request_record.approval_request_id

    auth_svc = ReviewerAuthorizationService()
    rej_svc = ApprovalRejectionService(request_service=req_svc, auth_service=auth_svc)
    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    cmd1 = ApprovalRejectionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        rejection_reason=RejectionReason.HIGH_RISK_SUSPECTED,
        reviewer_comment="Reason A",
        idempotency_key="key_rej_11",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    cmd2 = ApprovalRejectionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        rejection_reason=RejectionReason.POLICY_VIOLATION,  # Modified reason!
        reviewer_comment="Reason B",
        idempotency_key="key_rej_11",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    rej_svc.reject_request(cmd1)

    with pytest.raises(ApprovalRejectionConflictError) as exc_info:
        rej_svc.reject_request(cmd2)

    assert exc_info.value.error_code in (
        "APPROVAL_REJECTION_CONFLICT",
        "REJECTION_IDEMPOTENCY_CONFLICT",
    )


def test_12_malicious_script_comment_rejected() -> None:
    """12. Security Test: Reviewer comment containing script tags raises ValidationError."""
    tenant_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    with pytest.raises(ValidationError) as exc_info:
        ApprovalRejectionCommand(
            approval_request_id=uuid.uuid4(),
            tenant_id=tenant_id,
            reviewer_context=reviewer,
            rejection_reason=RejectionReason.OTHER,
            reviewer_comment="<script>document.cookie='leak'</script>",
            idempotency_key="k",
            expected_approval_fingerprint="fp",
        )
    assert "forbidden executable script tags" in str(exc_info.value)


def test_13_oversized_comment_rejected() -> None:
    """13. Security Test: Reviewer comment exceeding 500 chars raises ValidationError."""
    tenant_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    with pytest.raises(ValidationError) as exc_info:
        ApprovalRejectionCommand(
            approval_request_id=uuid.uuid4(),
            tenant_id=tenant_id,
            reviewer_context=reviewer,
            rejection_reason=RejectionReason.OTHER,
            reviewer_comment="x" * 501,
            idempotency_key="k",
            expected_approval_fingerprint="fp",
        )
    assert "cannot exceed 500" in str(exc_info.value)


def test_14_secret_redaction_in_rejection_result() -> None:
    """14. Security Test: ApprovalRejectionResult contains zero secret fields."""
    assert "key_secret" not in ApprovalRejectionResult.model_fields
    assert "webhook_secret" not in ApprovalRejectionResult.model_fields
    assert "authorization_header" not in ApprovalRejectionResult.model_fields


def test_15_static_check_no_direct_razorpay_sdk_imports() -> None:
    """15. Static Check: ApprovalRejectionService DOES NOT import razorpay SDK directly."""
    import app.payment.approval.approval_rejection_service as ars_mod

    source_code = inspect.getsource(ars_mod)
    assert "import razorpay" not in source_code
    assert "from razorpay" not in source_code


def test_16_static_check_no_payment_status_mutation() -> None:
    """16. Static Check: ApprovalRejectionService DOES NOT mutate PaymentStatus."""
    import app.payment.approval.approval_rejection_service as ars_mod

    source_code = inspect.getsource(ars_mod)
    assert "transition_status" not in source_code
    assert "PaymentStatusService" not in source_code


def test_17_static_check_no_risk_recalculation() -> None:
    """17. Static Check: ApprovalRejectionService DOES NOT recalculate risk scores."""
    import app.payment.approval.approval_rejection_service as ars_mod

    source_code = inspect.getsource(ars_mod)
    assert "evaluate_approval_requirement" not in source_code
    assert "calculate_composite_score" not in source_code


def test_18_command_extra_forbid() -> None:
    """18. Security Test: ApprovalRejectionCommand rejects extra injected parameters."""
    tenant_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    with pytest.raises(ValidationError):
        ApprovalRejectionCommand.model_validate(
            {
                "approval_request_id": str(uuid.uuid4()),
                "tenant_id": str(tenant_id),
                "reviewer_context": reviewer.model_dump(),
                "rejection_reason": "OTHER",
                "idempotency_key": "k",
                "expected_approval_fingerprint": "fp",
                "injected_field": "unauthorized",
            }
        )


def test_19_deterministic_decision_fingerprint() -> None:
    """19. Test decision fingerprint is deterministic across identical rejection executions."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    decision = _make_decision_result(tenant_id, agent_id, "tx_rej_19")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_19")
    req_id = created.request_record.approval_request_id

    auth_svc = ReviewerAuthorizationService()
    rej_svc = ApprovalRejectionService(request_service=req_svc, auth_service=auth_svc)
    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    cmd = ApprovalRejectionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        rejection_reason=RejectionReason.POLICY_VIOLATION,
        idempotency_key="idemp_rej_19",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    res1 = rej_svc.reject_request(cmd)
    res2 = rej_svc.reject_request(cmd)

    assert res1.decision_fingerprint == res2.decision_fingerprint


def test_20_already_rejected_request_raises_error() -> None:
    """20. Security Test: Re-rejecting an already REJECTED request without key fails."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    rev1_id = uuid.uuid4()
    rev2_id = uuid.uuid4()

    decision = _make_decision_result(tenant_id, agent_id, "tx_rej_20")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_20")
    req_id = created.request_record.approval_request_id

    auth_svc = ReviewerAuthorizationService()
    rej_svc = ApprovalRejectionService(request_service=req_svc, auth_service=auth_svc)

    rev1 = TrustedReviewerContext(
        reviewer_id=rev1_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )
    rev2 = TrustedReviewerContext(
        reviewer_id=rev2_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    cmd1 = ApprovalRejectionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=rev1,
        rejection_reason=RejectionReason.HIGH_RISK_SUSPECTED,
        idempotency_key="key_rev1",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    cmd2 = ApprovalRejectionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=rev2,
        rejection_reason=RejectionReason.POLICY_VIOLATION,
        idempotency_key="key_rev2",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    rej_svc.reject_request(cmd1)

    with pytest.raises(ApprovalRejectionError) as exc_info:
        rej_svc.reject_request(cmd2)

    assert exc_info.value.error_code == "ALREADY_REJECTED"
