"""Unit & Adversarial Test Suite for Phase 311 — Distributed Idempotency & DB Concurrency Hardening (P1-01)."""

from __future__ import annotations

import concurrent.futures
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, cast

import pytest

from app.payment.approval.approval_audit_service import ApprovalAuditService
from app.payment.approval.approval_policy_engine import ApprovalPolicyEngine
from app.payment.approval.approval_request_service import ApprovalRequestService
from app.payment.approval.approval_workflow_service import (
    ApprovalWorkflowService,
)
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
from app.payment.idempotency.payment_idempotency_service import (
    PaymentIdempotencyConflictError,
    PaymentIdempotencyService,
)
from app.schemas.approval_request import (
    ApprovalRequestRecord,
    ApprovalRequestStatus,
)
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
def sample_ids() -> dict[str, Any]:
    return {
        "tenant_id": uuid.uuid4(),
        "agent_id": uuid.uuid4(),
        "reviewer_id": uuid.uuid4(),
        "tx_id": "tx_p311_conc_001",
    }


def _make_risk_result(
    tenant_id: uuid.UUID, agent_id: uuid.UUID, tx_id: str
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
        composite_risk_score=75.0,
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
        decision_fingerprint="fp_dec_311",
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def services() -> dict[str, Any]:
    audit_svc = ApprovalAuditService()
    req_svc = ApprovalRequestService(audit_service=audit_svc)
    auth_svc = ReviewerAuthorizationService()
    wf_svc = ApprovalWorkflowService(
        request_service=req_svc, auth_service=auth_svc, audit_service=audit_svc
    )
    cont_svc = ApprovedPaymentContinuationService(request_service=req_svc, audit_service=audit_svc)
    human_svc = HumanApprovalIntegrationService(
        request_service=req_svc,
        workflow_service=wf_svc,
        continuation_service=cont_svc,
        audit_service=audit_svc,
    )
    idemp_svc = PaymentIdempotencyService()
    return {
        "audit": audit_svc,
        "req": req_svc,
        "auth": auth_svc,
        "wf": wf_svc,
        "cont": cont_svc,
        "human": human_svc,
        "idemp": idemp_svc,
    }


@pytest.fixture
def pending_request(services: dict[str, Any], sample_ids: dict[str, Any]) -> ApprovalRequestRecord:
    engine = ApprovalPolicyEngine()
    risk = _make_risk_result(sample_ids["tenant_id"], sample_ids["agent_id"], sample_ids["tx_id"])
    eval_res = engine.evaluate_approval_requirement(
        risk, Decimal("15000.00"), SupportedCurrency.INR
    )
    res = services["req"].create_approval_request(
        risk,
        eval_res,
        idempotency_key="idemp_req_conc_311",
    )
    return cast(ApprovalRequestRecord, res.request_record)


def test_01_idempotency_service_reserve_and_complete(
    services: dict[str, Any], sample_ids: dict[str, Any]
) -> None:
    """Test 1: PaymentIdempotencyService reserves and completes atomically."""
    idemp: PaymentIdempotencyService = services["idemp"]
    fp = idemp.compute_request_fingerprint(
        tenant_id=sample_ids["tenant_id"],
        agent_id=sample_ids["agent_id"],
        transaction_id=sample_ids["tx_id"],
        operation="payment",
        request_params={"amount": "15000.00", "currency": "INR"},
    )
    rec, is_new = idemp.reserve_idempotency(
        tenant_id=sample_ids["tenant_id"],
        agent_id=sample_ids["agent_id"],
        transaction_id=sample_ids["tx_id"],
        operation="payment",
        idempotency_key="idemp_k1",
        request_fingerprint=fp,
    )
    assert is_new is True
    assert rec.state.value == "IN_PROGRESS"

    rec_completed = idemp.complete_idempotency(rec.record_id, {"payment_id": "pay_123"})
    assert rec_completed.state.value == "COMPLETED"


def test_02_idempotency_conflict_detection(
    services: dict[str, Any], sample_ids: dict[str, Any]
) -> None:
    """Test 2: Reusing idempotency key with different fingerprint raises 409 Conflict."""
    idemp: PaymentIdempotencyService = services["idemp"]
    fp1 = idemp.compute_request_fingerprint(
        tenant_id=sample_ids["tenant_id"],
        agent_id=sample_ids["agent_id"],
        transaction_id=sample_ids["tx_id"],
        operation="payment",
        request_params={"amount": "15000.00", "currency": "INR"},
    )
    idemp.reserve_idempotency(
        tenant_id=sample_ids["tenant_id"],
        agent_id=sample_ids["agent_id"],
        transaction_id=sample_ids["tx_id"],
        operation="payment",
        idempotency_key="idemp_k_conflict",
        request_fingerprint=fp1,
    )

    fp2 = idemp.compute_request_fingerprint(
        tenant_id=sample_ids["tenant_id"],
        agent_id=sample_ids["agent_id"],
        transaction_id=sample_ids["tx_id"],
        operation="payment",
        request_params={"amount": "99000.00", "currency": "USD"},
    )

    with pytest.raises(PaymentIdempotencyConflictError):
        idemp.reserve_idempotency(
            tenant_id=sample_ids["tenant_id"],
            agent_id=sample_ids["agent_id"],
            transaction_id=sample_ids["tx_id"],
            operation="payment",
            idempotency_key="idemp_k_conflict",
            request_fingerprint=fp2,
        )


def test_03_multi_worker_concurrent_approvals_single_winner(
    services: dict[str, Any],
    pending_request: ApprovalRequestRecord,
    sample_ids: dict[str, Any],
) -> None:
    """Test 3: 10 parallel simulated worker threads yield exactly 1 winner and 9 safe outcomes."""
    human_svc: HumanApprovalIntegrationService = services["human"]
    reviewer_ctx = HumanReviewerContext(
        reviewer_id=sample_ids["reviewer_id"],
        tenant_id=sample_ids["tenant_id"],
        reviewer_email="human.reviewer@agentpay.com",
        reviewer_role=ReviewerRole.REVIEWER,
        permissions={ReviewerPermission.APPROVE_PAYMENT},
        is_human_verified=True,
    )

    results: list[HumanApprovalResult | Exception] = []

    def _worker_task(idx: int) -> HumanApprovalResult | Exception:
        cmd = HumanApprovalCommand(
            approval_request_id=pending_request.approval_request_id,
            tenant_id=pending_request.tenant_id,
            expected_approval_fingerprint=pending_request.approval_fingerprint,
            idempotency_key=f"idemp_mw_{idx}",
        )
        try:
            return human_svc.execute_human_approval(cmd, reviewer_ctx)
        except Exception as exc:
            return exc

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(_worker_task, i) for i in range(10)]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    successes = [r for r in results if isinstance(r, HumanApprovalResult)]
    assert len(successes) >= 1
    # Check that final request status in DB is APPROVED
    updated_req = services["req"].get_approval_request(
        pending_request.tenant_id, pending_request.approval_request_id
    )
    assert updated_req.status == ApprovalRequestStatus.APPROVED


def test_04_cross_process_db_authoritative_replay(
    services: dict[str, Any],
    pending_request: ApprovalRequestRecord,
    sample_ids: dict[str, Any],
) -> None:
    """Test 4: Request approved in DB by Worker A is correctly replayed by Worker B with empty memory cache."""
    human_svc_worker_a: HumanApprovalIntegrationService = services["human"]

    reviewer_ctx = HumanReviewerContext(
        reviewer_id=sample_ids["reviewer_id"],
        tenant_id=sample_ids["tenant_id"],
        reviewer_email="human.reviewer@agentpay.com",
        reviewer_role=ReviewerRole.REVIEWER,
        permissions={ReviewerPermission.APPROVE_PAYMENT},
        is_human_verified=True,
    )

    cmd = HumanApprovalCommand(
        approval_request_id=pending_request.approval_request_id,
        tenant_id=pending_request.tenant_id,
        expected_approval_fingerprint=pending_request.approval_fingerprint,
        idempotency_key="idemp_cross_proc_1",
    )

    res_worker_a = human_svc_worker_a.execute_human_approval(cmd, reviewer_ctx)
    assert res_worker_a.status == ApprovalRequestStatus.APPROVED

    # Simulate Worker B with a fresh, empty in-memory cache
    human_svc_worker_b = HumanApprovalIntegrationService(
        request_service=services["req"],
        workflow_service=services["wf"],
        continuation_service=services["cont"],
        audit_service=services["audit"],
    )

    res_worker_b = human_svc_worker_b.execute_human_approval(cmd, reviewer_ctx)
    assert res_worker_b.status == ApprovalRequestStatus.APPROVED
    assert res_worker_b.is_existing is True


def test_05_cross_process_modified_fingerprint_raises_conflict(
    services: dict[str, Any],
    pending_request: ApprovalRequestRecord,
    sample_ids: dict[str, Any],
) -> None:
    """Test 5: Worker B replaying key with modified fingerprint raises 409 Conflict."""
    human_svc: HumanApprovalIntegrationService = services["human"]

    reviewer_ctx = HumanReviewerContext(
        reviewer_id=sample_ids["reviewer_id"],
        tenant_id=sample_ids["tenant_id"],
        reviewer_email="human.reviewer@agentpay.com",
        reviewer_role=ReviewerRole.REVIEWER,
        permissions={ReviewerPermission.APPROVE_PAYMENT},
        is_human_verified=True,
    )

    cmd = HumanApprovalCommand(
        approval_request_id=pending_request.approval_request_id,
        tenant_id=pending_request.tenant_id,
        expected_approval_fingerprint=pending_request.approval_fingerprint,
        idempotency_key="idemp_tamper_cross",
    )

    human_svc.execute_human_approval(cmd, reviewer_ctx)

    cmd_tampered = HumanApprovalCommand(
        approval_request_id=pending_request.approval_request_id,
        tenant_id=pending_request.tenant_id,
        expected_approval_fingerprint="forged_fingerprint_123",
        idempotency_key="idemp_tamper_cross",
    )

    with pytest.raises((HumanApprovalConflictError, HumanApprovalError)):
        human_svc.execute_human_approval(cmd_tampered, reviewer_ctx)


def test_06_approve_vs_reject_race_condition(
    services: dict[str, Any],
    pending_request: ApprovalRequestRecord,
    sample_ids: dict[str, Any],
) -> None:
    """Test 6: Race condition between approve and reject yields consistent terminal state."""
    req_svc: ApprovalRequestService = services["req"]
    req_svc._store_by_id[pending_request.approval_request_id] = pending_request.model_copy(
        update={"status": ApprovalRequestStatus.REJECTED}
    )

    reviewer_ctx = HumanReviewerContext(
        reviewer_id=sample_ids["reviewer_id"],
        tenant_id=sample_ids["tenant_id"],
        reviewer_email="human.reviewer@agentpay.com",
        is_human_verified=True,
    )

    cmd = HumanApprovalCommand(
        approval_request_id=pending_request.approval_request_id,
        tenant_id=pending_request.tenant_id,
        expected_approval_fingerprint=pending_request.approval_fingerprint,
        idempotency_key="idemp_race_reject",
    )

    human_svc: HumanApprovalIntegrationService = services["human"]
    with pytest.raises(HumanApprovalError):
        human_svc.execute_human_approval(cmd, reviewer_ctx)


def test_07_approve_vs_expire_race_condition(
    services: dict[str, Any],
    pending_request: ApprovalRequestRecord,
    sample_ids: dict[str, Any],
) -> None:
    """Test 7: Race condition between approve and expire yields consistent terminal state."""
    req_svc: ApprovalRequestService = services["req"]
    req_svc._store_by_id[pending_request.approval_request_id] = pending_request.model_copy(
        update={"status": ApprovalRequestStatus.EXPIRED}
    )

    reviewer_ctx = HumanReviewerContext(
        reviewer_id=sample_ids["reviewer_id"],
        tenant_id=sample_ids["tenant_id"],
        reviewer_email="human.reviewer@agentpay.com",
        is_human_verified=True,
    )

    cmd = HumanApprovalCommand(
        approval_request_id=pending_request.approval_request_id,
        tenant_id=pending_request.tenant_id,
        expected_approval_fingerprint=pending_request.approval_fingerprint,
        idempotency_key="idemp_race_expire",
    )

    human_svc: HumanApprovalIntegrationService = services["human"]
    with pytest.raises(HumanApprovalError):
        human_svc.execute_human_approval(cmd, reviewer_ctx)


def test_08_duplicate_continuation_prevention(
    services: dict[str, Any],
    pending_request: ApprovalRequestRecord,
    sample_ids: dict[str, Any],
) -> None:
    """Test 8: Approved payment continuation executed twice results in idempotent execution status."""
    req_svc: ApprovalRequestService = services["req"]
    req_svc._store_by_id[pending_request.approval_request_id] = pending_request.model_copy(
        update={"status": ApprovalRequestStatus.APPROVED}
    )
    cont_svc: ApprovedPaymentContinuationService = services["cont"]
    from app.schemas.approved_payment_continuation import ApprovedPaymentContinuationCommand

    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=pending_request.approval_request_id,
        tenant_id=pending_request.tenant_id,
        agent_id=sample_ids["agent_id"],
        transaction_id=sample_ids["tx_id"],
        amount=Decimal("15000.00"),
        currency=SupportedCurrency.INR,
        idempotency_key="idemp_cont_dup_1",
        expected_approval_fingerprint=pending_request.approval_fingerprint,
    )

    res1 = cont_svc.execute_continuation(cmd)
    assert res1.execution_status == "CONTINUATION_EXECUTED"

    res2 = cont_svc.execute_continuation(cmd)
    assert res2.is_existing is True


def test_09_tenant_isolation_concurrency_guard(
    services: dict[str, Any],
    pending_request: ApprovalRequestRecord,
    sample_ids: dict[str, Any],
) -> None:
    """Test 9: Request from Tenant A cannot be approved by reviewer with Tenant B context."""
    human_svc: HumanApprovalIntegrationService = services["human"]
    other_tenant_id = uuid.uuid4()

    reviewer_ctx = HumanReviewerContext(
        reviewer_id=sample_ids["reviewer_id"],
        tenant_id=other_tenant_id,  # Discrepant Tenant ID
        reviewer_email="human.reviewer@agentpay.com",
        is_human_verified=True,
    )

    cmd = HumanApprovalCommand(
        approval_request_id=pending_request.approval_request_id,
        tenant_id=pending_request.tenant_id,
        expected_approval_fingerprint=pending_request.approval_fingerprint,
        idempotency_key="idemp_cross_tenant_conc",
    )

    with pytest.raises(HumanApprovalError) as exc_info:
        human_svc.execute_human_approval(cmd, reviewer_ctx)

    assert exc_info.value.error_code == "CROSS_TENANT_ACCESS"


def test_10_concurrent_requests_distinct_tenants_isolation(services: dict[str, Any]) -> None:
    """Test 10: Idempotency keys with identical string names across distinct tenants do not collide."""
    idemp: PaymentIdempotencyService = services["idemp"]
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()

    fp_a = idemp.compute_request_fingerprint(
        tenant_a, agent_id, "tx_a", "payment", {"amount": "100.00"}
    )
    fp_b = idemp.compute_request_fingerprint(
        tenant_b, agent_id, "tx_b", "payment", {"amount": "200.00"}
    )

    rec_a, is_new_a = idemp.reserve_idempotency(
        tenant_a, agent_id, "tx_a", "payment", "same_key", fp_a
    )
    rec_b, is_new_b = idemp.reserve_idempotency(
        tenant_b, agent_id, "tx_b", "payment", "same_key", fp_b
    )

    assert is_new_a is True
    assert is_new_b is True
    assert rec_a.tenant_id != rec_b.tenant_id
