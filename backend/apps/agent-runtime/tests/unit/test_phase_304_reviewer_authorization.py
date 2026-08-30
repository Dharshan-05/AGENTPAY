"""Unit, Security & Adversarial Tests for Phase 304 — Reviewer Authorization."""

from __future__ import annotations

import inspect
import uuid
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.payment.approval.reviewer_authorization_service import (
    ReviewerAuthorizationService,
)
from app.schemas.approval_request import (
    ApprovalRequestPriority,
    ApprovalRequestRecord,
    ApprovalRequestStatus,
)
from app.schemas.payment import SupportedCurrency
from app.schemas.reviewer_authorization import (
    ReviewerAuthorizationResult,
    ReviewerPermission,
    ReviewerRole,
    TrustedReviewerContext,
)


def _make_sample_request(
    tenant_id: uuid.UUID,
    agent_id: uuid.UUID,
    tx_id: str = "tx_auth_304",
    amount: Decimal = Decimal("15000.00"),
    status: ApprovalRequestStatus = ApprovalRequestStatus.PENDING,
) -> ApprovalRequestRecord:
    return ApprovalRequestRecord(
        approval_request_id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="fp_auth_304",
        approval_fingerprint="fp_appr_304",
        amount=amount,
        currency=SupportedCurrency.INR,
        operation="create_order",
        status=status,
        risk_score=45.0,
        priority=ApprovalRequestPriority.MEDIUM,
        idempotency_key="idemp_304",
    )


def test_01_valid_reviewer_authorization_granted() -> None:
    """1. Test valid human reviewer authorization grants permission."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    req = _make_sample_request(tenant_id, agent_id)
    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id,
        tenant_id=tenant_id,
        reviewer_role=ReviewerRole.REVIEWER,
        authorization_limit=Decimal("50000.00"),
    )

    svc = ReviewerAuthorizationService()
    res = svc.authorize_reviewer(
        reviewer_context=reviewer,
        approval_request=req,
        required_permission=ReviewerPermission.APPROVE_PAYMENT,
    )

    assert isinstance(res, ReviewerAuthorizationResult)
    assert res.authorized is True
    assert res.reason_code == "AUTHORIZATION_GRANTED"
    assert len(res.authorization_fingerprint) == 64


def test_02_cross_tenant_reviewer_denied() -> None:
    """2. Security Test: Cross-tenant reviewer attempt fails closed (CROSS_TENANT_ACCESS)."""
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    req = _make_sample_request(tenant_a, agent_id)
    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id,
        tenant_id=tenant_b,  # Different tenant!
        reviewer_role=ReviewerRole.APPROVAL_ADMIN,
    )

    svc = ReviewerAuthorizationService()
    res = svc.authorize_reviewer(reviewer, req)

    assert res.authorized is False
    assert res.reason_code == "CROSS_TENANT_ACCESS"


def test_03_self_approval_forbidden() -> None:
    """3. Security Test: Reviewer attempting self-approval fails closed."""
    tenant_id = uuid.uuid4()
    same_id = uuid.uuid4()  # AI Agent ID and Reviewer ID are identical!

    req = _make_sample_request(tenant_id, agent_id=same_id)
    reviewer = TrustedReviewerContext(
        reviewer_id=same_id,
        tenant_id=tenant_id,
        reviewer_role=ReviewerRole.APPROVAL_ADMIN,
    )

    svc = ReviewerAuthorizationService()
    res = svc.authorize_reviewer(reviewer, req)

    assert res.authorized is False
    assert res.reason_code == "SELF_APPROVAL_FORBIDDEN"


def test_04_permission_denied_for_missing_capability() -> None:
    """4. Security Test: Reviewer lacking capability is denied (REVIEWER_PERMISSION_DENIED)."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    req = _make_sample_request(tenant_id, agent_id)
    # Reviewer with custom empty permissions set
    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id,
        tenant_id=tenant_id,
        reviewer_role=ReviewerRole.REVIEWER,
        permissions={ReviewerPermission.VIEW_APPROVAL_REQUEST},  # Missing APPROVE_PAYMENT!
    )

    svc = ReviewerAuthorizationService()
    res = svc.authorize_reviewer(
        reviewer, req, required_permission=ReviewerPermission.CANCEL_APPROVAL
    )

    assert res.authorized is False
    assert res.reason_code == "REVIEWER_PERMISSION_DENIED"


def test_05_approval_limit_exceeded() -> None:
    """5. Security Test: Amount exceeding reviewer limit fails (APPROVAL_LIMIT_EXCEEDED)."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    req = _make_sample_request(tenant_id, agent_id, amount=Decimal("150000.00"))
    # Standard REVIEWER limit is 50,000 INR
    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id,
        tenant_id=tenant_id,
        reviewer_role=ReviewerRole.REVIEWER,
        authorization_limit=Decimal("50000.00"),
    )

    svc = ReviewerAuthorizationService()
    res = svc.authorize_reviewer(reviewer, req)

    assert res.authorized is False
    assert res.reason_code == "APPROVAL_LIMIT_EXCEEDED"


def test_06_already_finalized_request_denied() -> None:
    """6. Security Test: Request not in PENDING status fails closed (APPROVAL_ALREADY_FINALIZED)."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    # Request mutated to APPROVED after creation
    req_pending = _make_sample_request(tenant_id, agent_id)
    req_finalized = req_pending.model_copy(update={"status": ApprovalRequestStatus.APPROVED})

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id,
        tenant_id=tenant_id,
        reviewer_role=ReviewerRole.APPROVAL_ADMIN,
    )

    svc = ReviewerAuthorizationService()
    res = svc.authorize_reviewer(reviewer, req_finalized)

    assert res.authorized is False
    assert res.reason_code == "APPROVAL_ALREADY_FINALIZED"


def test_07_fingerprint_mismatch_denied() -> None:
    """7. Security Test: Provided expected fingerprint mismatch fails closed."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    req = _make_sample_request(tenant_id, agent_id)
    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id,
        tenant_id=tenant_id,
        reviewer_role=ReviewerRole.REVIEWER,
    )

    svc = ReviewerAuthorizationService()
    res = svc.authorize_reviewer(
        reviewer,
        req,
        expected_approval_fingerprint="fp_tampered_fingerprint_999",
    )

    assert res.authorized is False
    assert res.reason_code == "APPROVAL_FINGERPRINT_MISMATCH"


def test_08_senior_reviewer_limit_elevation() -> None:
    """8. Test SENIOR_REVIEWER can approve higher limits (up to 500,000 INR)."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    req = _make_sample_request(tenant_id, agent_id, amount=Decimal("250000.00"))
    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id,
        tenant_id=tenant_id,
        reviewer_role=ReviewerRole.SENIOR_REVIEWER,
        authorization_limit=Decimal("500000.00"),
    )

    svc = ReviewerAuthorizationService()
    res = svc.authorize_reviewer(reviewer, req)

    assert res.authorized is True
    assert res.reason_code == "AUTHORIZATION_GRANTED"


def test_09_secret_redaction_in_authorization_result() -> None:
    """9. Security Test: ReviewerAuthorizationResult contains zero secrets."""
    assert "key_secret" not in ReviewerAuthorizationResult.model_fields
    assert "webhook_secret" not in ReviewerAuthorizationResult.model_fields
    assert "authorization_header" not in ReviewerAuthorizationResult.model_fields


def test_10_static_check_no_direct_razorpay_sdk_imports() -> None:
    """10. Static Check: ReviewerAuthorizationService DOES NOT import razorpay SDK directly."""
    import app.payment.approval.reviewer_authorization_service as ras_mod

    source_code = inspect.getsource(ras_mod)
    assert "import razorpay" not in source_code
    assert "from razorpay" not in source_code


def test_11_rejected_status_denied() -> None:
    """11. Security Test: REJECTED status request fails closed (APPROVAL_ALREADY_FINALIZED)."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    req_pending = _make_sample_request(tenant_id, agent_id)
    req_rejected = req_pending.model_copy(update={"status": ApprovalRequestStatus.REJECTED})

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.APPROVAL_ADMIN
    )
    svc = ReviewerAuthorizationService()
    res = svc.authorize_reviewer(reviewer, req_rejected)

    assert res.authorized is False
    assert res.reason_code == "APPROVAL_ALREADY_FINALIZED"


def test_12_expired_status_denied() -> None:
    """12. Security Test: EXPIRED status request fails closed (APPROVAL_ALREADY_FINALIZED)."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    req_pending = _make_sample_request(tenant_id, agent_id)
    req_expired = req_pending.model_copy(update={"status": ApprovalRequestStatus.EXPIRED})

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.APPROVAL_ADMIN
    )
    svc = ReviewerAuthorizationService()
    res = svc.authorize_reviewer(reviewer, req_expired)

    assert res.authorized is False
    assert res.reason_code == "APPROVAL_ALREADY_FINALIZED"


def test_13_cancelled_status_denied() -> None:
    """13. Security Test: CANCELLED status request fails closed (APPROVAL_ALREADY_FINALIZED)."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    req_pending = _make_sample_request(tenant_id, agent_id)
    req_cancelled = req_pending.model_copy(update={"status": ApprovalRequestStatus.CANCELLED})

    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.APPROVAL_ADMIN
    )
    svc = ReviewerAuthorizationService()
    res = svc.authorize_reviewer(reviewer, req_cancelled)

    assert res.authorized is False
    assert res.reason_code == "APPROVAL_ALREADY_FINALIZED"


def test_14_approval_admin_elevated_limit() -> None:
    """14. Test APPROVAL_ADMIN supports limits up to 10,000,000 INR."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    req = _make_sample_request(tenant_id, agent_id, amount=Decimal("5000000.00"))
    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id,
        tenant_id=tenant_id,
        reviewer_role=ReviewerRole.APPROVAL_ADMIN,
        authorization_limit=Decimal("10000000.00"),
    )

    svc = ReviewerAuthorizationService()
    res = svc.authorize_reviewer(reviewer, req)

    assert res.authorized is True
    assert res.reason_code == "AUTHORIZATION_GRANTED"


def test_15_approval_admin_limit_exceeded() -> None:
    """15. Test APPROVAL_ADMIN exceeding limit (e.g. 15,000,000 INR > 10,000,000) fails."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    req = _make_sample_request(tenant_id, agent_id, amount=Decimal("15000000.00"))
    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id,
        tenant_id=tenant_id,
        reviewer_role=ReviewerRole.APPROVAL_ADMIN,
        authorization_limit=Decimal("10000000.00"),
    )

    svc = ReviewerAuthorizationService()
    res = svc.authorize_reviewer(reviewer, req)

    assert res.authorized is False
    assert res.reason_code == "APPROVAL_LIMIT_EXCEEDED"


def test_16_trusted_reviewer_context_extra_forbid() -> None:
    """16. Security Test: Injecting spoofed fields into context raises ValidationError."""
    tenant_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    with pytest.raises(ValidationError):
        TrustedReviewerContext.model_validate(
            {
                "reviewer_id": str(reviewer_id),
                "tenant_id": str(tenant_id),
                "reviewer_role": "REVIEWER",
                "is_admin_override": True,  # Spoofed extra field!
            }
        )


def test_17_trusted_reviewer_context_immutable() -> None:
    """17. Security Test: TrustedReviewerContext model is frozen and immutable."""
    tenant_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    ctx = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    with pytest.raises(ValidationError):
        ctx.reviewer_role = ReviewerRole.APPROVAL_ADMIN  # Mutation forbidden!


def test_18_deterministic_authorization_fingerprint() -> None:
    """18. Test authorization fingerprint is deterministic across identical inputs."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    req = _make_sample_request(tenant_id, agent_id)
    reviewer = TrustedReviewerContext(
        reviewer_id=reviewer_id, tenant_id=tenant_id, reviewer_role=ReviewerRole.REVIEWER
    )

    svc = ReviewerAuthorizationService()
    res1 = svc.authorize_reviewer(reviewer, req)
    res2 = svc.authorize_reviewer(reviewer, req)

    assert res1.authorization_fingerprint == res2.authorization_fingerprint
