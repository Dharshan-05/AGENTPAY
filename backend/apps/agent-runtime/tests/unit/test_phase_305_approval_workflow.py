"""Unit, Security & Adversarial Tests for Phase 305 — Approval Workflow."""

from __future__ import annotations

import inspect
import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.payment.approval.approval_policy_engine import ApprovalPolicyEngine
from app.payment.approval.approval_request_service import ApprovalRequestService
from app.payment.approval.approval_workflow_service import (
    ApprovalWorkflowConflictError,
    ApprovalWorkflowError,
    ApprovalWorkflowService,
)
from app.payment.approval.reviewer_authorization_service import (
    ReviewerAuthorizationService,
)
from app.schemas.approval_request import (
    ApprovalRequestStatus,
)
from app.schemas.approval_workflow import (
    ApprovalDecisionCommand,
    ApprovalDecisionType,
    ApprovalWorkflowResult,
)
from app.schemas.payment import SupportedCurrency
from app.schemas.reviewer_authorization import (
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
        decision_fingerprint="fp_dec_305",
        created_at=datetime.now(UTC),
    )


def test_01_pending_to_approved_success() -> None:
    """1. Test PENDING -> APPROVED state transition succeeds when authorized."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()
    tx_id = "tx_wf_01"

    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("15000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_01")
    req_id = created.request_record.approval_request_id

    auth_svc = ReviewerAuthorizationService()
    wf_svc = ApprovalWorkflowService(request_service=req_svc, auth_service=auth_svc)

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id,
        tenant_id=tenant_id,
        reviewer_role=ReviewerRole.REVIEWER,
        authorization_limit=Decimal("50000.00"),
    )

    cmd = ApprovalDecisionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        decision=ApprovalDecisionType.APPROVE,
        reviewer_comment="Approved after verifying identity.",
        idempotency_key="idemp_wf_01",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    res = wf_svc.approve_request(cmd)

    assert isinstance(res, ApprovalWorkflowResult)
    assert res.previous_status == ApprovalRequestStatus.PENDING
    assert res.new_status == ApprovalRequestStatus.APPROVED
    assert res.is_existing is False
    assert len(res.decision_fingerprint) == 64

    # Verify request record status in request_service is now APPROVED!
    updated_req = req_svc.get_approval_request(tenant_id, req_id)
    assert updated_req is not None
    assert updated_req.status == ApprovalRequestStatus.APPROVED


def test_02_idempotent_approval_replay() -> None:
    """2. Test duplicate approval command with same idempotency key returns existing result."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()
    tx_id = "tx_wf_02"

    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_02")
    req_id = created.request_record.approval_request_id

    auth_svc = ReviewerAuthorizationService()
    wf_svc = ApprovalWorkflowService(request_service=req_svc, auth_service=auth_svc)

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id,
        tenant_id=tenant_id,
        reviewer_role=ReviewerRole.REVIEWER,
    )

    cmd = ApprovalDecisionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        decision=ApprovalDecisionType.APPROVE,
        idempotency_key="idemp_wf_02",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    res1 = wf_svc.approve_request(cmd)
    res2 = wf_svc.approve_request(cmd)

    assert res1.is_existing is False
    assert res2.is_existing is True
    assert res1.decision_fingerprint == res2.decision_fingerprint


def test_03_idempotency_conflict_raises_409() -> None:
    """3. Test same idempotency key with modified parameters raises 409 Conflict."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()
    tx_id = "tx_wf_03"

    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_03")
    req_id = created.request_record.approval_request_id

    auth_svc = ReviewerAuthorizationService()
    wf_svc = ApprovalWorkflowService(request_service=req_svc, auth_service=auth_svc)

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id,
        tenant_id=tenant_id,
        reviewer_role=ReviewerRole.REVIEWER,
    )

    cmd1 = ApprovalDecisionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        decision=ApprovalDecisionType.APPROVE,
        reviewer_comment="Comment 1",
        idempotency_key="shared_key_03",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    cmd2 = ApprovalDecisionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        decision=ApprovalDecisionType.APPROVE,
        reviewer_comment="Comment 2 modified!",  # Modified comment!
        idempotency_key="shared_key_03",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    wf_svc.approve_request(cmd1)

    with pytest.raises(ApprovalWorkflowConflictError) as exc_info:
        wf_svc.approve_request(cmd2)

    assert exc_info.value.error_code == "APPROVAL_WORKFLOW_CONFLICT"


def test_04_already_approved_request_fails() -> None:
    """4. Security Test: Re-approving an already APPROVED request without key fails."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id1 = uuid.uuid4()
    reviewer_id2 = uuid.uuid4()
    tx_id = "tx_wf_04"

    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_04")
    req_id = created.request_record.approval_request_id

    auth_svc = ReviewerAuthorizationService()
    wf_svc = ApprovalWorkflowService(request_service=req_svc, auth_service=auth_svc)

    rev1 = TrustedReviewerContext(
        reviewer_id=reviewer_id1, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )
    rev2 = TrustedReviewerContext(
        reviewer_id=reviewer_id2, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    cmd1 = ApprovalDecisionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=rev1,
        decision=ApprovalDecisionType.APPROVE,
        idempotency_key="key_rev1",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )
    cmd2 = ApprovalDecisionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=rev2,
        decision=ApprovalDecisionType.APPROVE,
        idempotency_key="key_rev2",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    wf_svc.approve_request(cmd1)

    with pytest.raises(ApprovalWorkflowError) as exc_info:
        wf_svc.approve_request(cmd2)

    assert exc_info.value.error_code == "ALREADY_APPROVED"


def test_05_unauthorized_reviewer_denied() -> None:
    """5. Security Test: Reviewer authorization failure denies state transition."""
    tenant_id = uuid.uuid4()
    other_tenant = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()
    tx_id = "tx_wf_05"

    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_05")
    req_id = created.request_record.approval_request_id

    auth_svc = ReviewerAuthorizationService()
    wf_svc = ApprovalWorkflowService(request_service=req_svc, auth_service=auth_svc)

    # Reviewer from wrong tenant!
    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id,
        tenant_id=other_tenant,
        reviewer_role=ReviewerRole.APPROVAL_ADMIN,
    )

    cmd = ApprovalDecisionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        decision=ApprovalDecisionType.APPROVE,
        idempotency_key="idemp_wf_05",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    with pytest.raises(ApprovalWorkflowError) as exc_info:
        wf_svc.approve_request(cmd)

    assert exc_info.value.error_code == "CROSS_TENANT_ACCESS"


def test_06_self_approval_denied() -> None:
    """6. Security Test: AI Agent attempting to approve its own request fails closed."""
    tenant_id = uuid.uuid4()
    same_id = uuid.uuid4()  # Agent and Reviewer share same ID!
    tx_id = "tx_wf_06"

    decision = _make_decision_result(tenant_id, same_id, tx_id)
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_06")
    req_id = created.request_record.approval_request_id

    auth_svc = ReviewerAuthorizationService()
    wf_svc = ApprovalWorkflowService(request_service=req_svc, auth_service=auth_svc)

    reviewer = TrustedReviewerContext(
        reviewer_id=same_id,
        tenant_id=tenant_id,
        reviewer_role=ReviewerRole.APPROVAL_ADMIN,
    )

    cmd = ApprovalDecisionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        decision=ApprovalDecisionType.APPROVE,
        idempotency_key="idemp_wf_06",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    with pytest.raises(ApprovalWorkflowError) as exc_info:
        wf_svc.approve_request(cmd)

    assert exc_info.value.error_code == "SELF_APPROVAL_FORBIDDEN"


def test_07_reviewer_comment_validation() -> None:
    """7. Test reviewer comment length and script injection validation."""
    tenant_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    # Long comment > 500 chars fails validation
    with pytest.raises(ValueError) as exc_info:
        ApprovalDecisionCommand(
            approval_request_id=uuid.uuid4(),
            tenant_id=tenant_id,
            reviewer_context=reviewer,
            reviewer_comment="a" * 501,
            idempotency_key="k",
            expected_approval_fingerprint="fp",
        )
    assert "cannot exceed 500" in str(exc_info.value)

    # Script tag injection fails validation
    with pytest.raises(ValueError) as exc_info:
        ApprovalDecisionCommand(
            approval_request_id=uuid.uuid4(),
            tenant_id=tenant_id,
            reviewer_context=reviewer,
            reviewer_comment="<script>alert(1)</script>",
            idempotency_key="k",
            expected_approval_fingerprint="fp",
        )
    assert "forbidden executable script tags" in str(exc_info.value)


def test_08_static_check_no_direct_razorpay_sdk_imports() -> None:
    """8. Static Check: ApprovalWorkflowService DOES NOT import razorpay SDK directly."""
    import app.payment.approval.approval_workflow_service as aws_mod

    source_code = inspect.getsource(aws_mod)
    assert "import razorpay" not in source_code
    assert "from razorpay" not in source_code


def test_09_static_check_no_payment_status_mutation() -> None:
    """9. Static Check: ApprovalWorkflowService DOES NOT mutate PaymentStatus."""
    import app.payment.approval.approval_workflow_service as aws_mod

    source_code = inspect.getsource(aws_mod)
    assert "transition_status" not in source_code
    assert "PaymentStatusService" not in source_code


def test_10_static_check_no_risk_recalculation() -> None:
    """10. Static Check: ApprovalWorkflowService DOES NOT recalculate risk."""
    import app.payment.approval.approval_workflow_service as aws_mod

    source_code = inspect.getsource(aws_mod)
    assert "evaluate_approval_requirement" not in source_code
    assert "calculate_composite_score" not in source_code


def test_11_wrong_approval_request_id_fails() -> None:
    """11. Security Test: Non-existent approval request ID raises APPROVAL_REQUEST_NOT_FOUND."""
    tenant_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    req_svc = ApprovalRequestService()
    auth_svc = ReviewerAuthorizationService()
    wf_svc = ApprovalWorkflowService(request_service=req_svc, auth_service=auth_svc)

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    cmd = ApprovalDecisionCommand(
        approval_request_id=uuid.uuid4(),  # Non-existent ID!
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        decision=ApprovalDecisionType.APPROVE,
        idempotency_key="idemp_wf_11",
        expected_approval_fingerprint="fp_dummy",
    )

    with pytest.raises(ApprovalWorkflowError) as exc_info:
        wf_svc.approve_request(cmd)

    assert exc_info.value.error_code == "APPROVAL_REQUEST_NOT_FOUND"


def test_12_wrong_fingerprint_fails() -> None:
    """12. Security Test: Approval fingerprint mismatch raises APPROVAL_FINGERPRINT_MISMATCH."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()
    tx_id = "tx_wf_12"

    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_12")
    req_id = created.request_record.approval_request_id

    auth_svc = ReviewerAuthorizationService()
    wf_svc = ApprovalWorkflowService(request_service=req_svc, auth_service=auth_svc)

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    cmd = ApprovalDecisionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        decision=ApprovalDecisionType.APPROVE,
        idempotency_key="idemp_wf_12",
        expected_approval_fingerprint="fp_invalid_tampered",  # Tampered fingerprint!
    )

    with pytest.raises(ApprovalWorkflowError) as exc_info:
        wf_svc.approve_request(cmd)

    assert exc_info.value.error_code == "APPROVAL_FINGERPRINT_MISMATCH"


def test_13_rejected_state_cannot_be_approved() -> None:
    """13. Security Test: Approval request in REJECTED state cannot transition to APPROVED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()
    tx_id = "tx_wf_13"

    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_13")
    req_id = created.request_record.approval_request_id

    # Mutate to REJECTED directly in mock storage
    req_svc._store_by_id[req_id] = req_svc._store_by_id[req_id].model_copy(
        update={"status": ApprovalRequestStatus.REJECTED}
    )

    auth_svc = ReviewerAuthorizationService()
    wf_svc = ApprovalWorkflowService(request_service=req_svc, auth_service=auth_svc)

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    cmd = ApprovalDecisionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        decision=ApprovalDecisionType.APPROVE,
        idempotency_key="idemp_wf_13",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    with pytest.raises(ApprovalWorkflowError) as exc_info:
        wf_svc.approve_request(cmd)

    assert exc_info.value.error_code == "INVALID_STATE_TRANSITION"


def test_14_expired_state_cannot_be_approved() -> None:
    """14. Security Test: Approval request in EXPIRED state cannot transition to APPROVED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()
    tx_id = "tx_wf_14"

    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_14")
    req_id = created.request_record.approval_request_id

    req_svc._store_by_id[req_id] = req_svc._store_by_id[req_id].model_copy(
        update={"status": ApprovalRequestStatus.EXPIRED}
    )

    auth_svc = ReviewerAuthorizationService()
    wf_svc = ApprovalWorkflowService(request_service=req_svc, auth_service=auth_svc)

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    cmd = ApprovalDecisionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        decision=ApprovalDecisionType.APPROVE,
        idempotency_key="idemp_wf_14",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    with pytest.raises(ApprovalWorkflowError) as exc_info:
        wf_svc.approve_request(cmd)

    assert exc_info.value.error_code == "INVALID_STATE_TRANSITION"


def test_15_cancelled_state_cannot_be_approved() -> None:
    """15. Security Test: Approval request in CANCELLED state cannot transition to APPROVED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()
    tx_id = "tx_wf_15"

    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_15")
    req_id = created.request_record.approval_request_id

    req_svc._store_by_id[req_id] = req_svc._store_by_id[req_id].model_copy(
        update={"status": ApprovalRequestStatus.CANCELLED}
    )

    auth_svc = ReviewerAuthorizationService()
    wf_svc = ApprovalWorkflowService(request_service=req_svc, auth_service=auth_svc)

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    cmd = ApprovalDecisionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        decision=ApprovalDecisionType.APPROVE,
        idempotency_key="idemp_wf_15",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    with pytest.raises(ApprovalWorkflowError) as exc_info:
        wf_svc.approve_request(cmd)

    assert exc_info.value.error_code == "INVALID_STATE_TRANSITION"


def test_16_command_extra_forbid() -> None:
    """16. Security Test: ApprovalDecisionCommand rejects unknown injected fields."""
    tenant_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    with pytest.raises(ValidationError):
        ApprovalDecisionCommand.model_validate(
            {
                "approval_request_id": str(uuid.uuid4()),
                "tenant_id": str(tenant_id),
                "reviewer_context": reviewer.model_dump(),
                "decision": "APPROVE",
                "idempotency_key": "k",
                "expected_approval_fingerprint": "fp",
                "injected_secret": "key_secret_12345",  # Injected field!
            }
        )


def test_17_result_secret_redaction() -> None:
    """17. Security Test: ApprovalWorkflowResult exposes zero secret attributes."""
    assert "key_secret" not in ApprovalWorkflowResult.model_fields
    assert "webhook_secret" not in ApprovalWorkflowResult.model_fields
    assert "authorization_header" not in ApprovalWorkflowResult.model_fields


def test_18_static_check_no_phase_309_continuation() -> None:
    """18. Static Check: ApprovalWorkflowService DOES NOT implement Phase 309 continuation."""
    import app.payment.approval.approval_workflow_service as aws_mod

    source_code = inspect.getsource(aws_mod)
    assert "create_payment_order" not in source_code
    assert "PaymentService" not in source_code


def test_19_static_check_no_phase_310_human_integration() -> None:
    """19. Static Check: ApprovalWorkflowService DOES NOT implement Phase 310 integration."""
    import app.payment.approval.approval_workflow_service as aws_mod

    source_code = inspect.getsource(aws_mod)
    assert "webauthn" not in source_code.lower()
    assert "otp_verify" not in source_code.lower()


def test_20_deterministic_decision_fingerprint() -> None:
    """20. Test decision fingerprint is deterministic across identical executions."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()
    tx_id = "tx_wf_20"

    decision = _make_decision_result(tenant_id, agent_id, tx_id)
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_20")
    req_id = created.request_record.approval_request_id

    auth_svc = ReviewerAuthorizationService()
    wf_svc = ApprovalWorkflowService(request_service=req_svc, auth_service=auth_svc)

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    cmd = ApprovalDecisionCommand(
        approval_request_id=req_id,
        tenant_id=tenant_id,
        reviewer_context=reviewer,
        decision=ApprovalDecisionType.APPROVE,
        idempotency_key="idemp_wf_20",
        expected_approval_fingerprint=policy_req.approval_fingerprint,
    )

    res1 = wf_svc.approve_request(cmd)
    res2 = wf_svc.approve_request(cmd)

    assert res1.decision_fingerprint == res2.decision_fingerprint
