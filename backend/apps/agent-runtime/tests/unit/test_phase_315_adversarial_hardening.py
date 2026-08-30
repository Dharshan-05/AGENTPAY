"""Unit & Security Test Suite for Phase 315 — Adversarial Security Hardening."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import pytest

from app.payment.approval.approval_audit_service import ApprovalAuditService
from app.payment.approval.approval_policy_engine import ApprovalPolicyEngine
from app.payment.approval.approval_request_service import ApprovalRequestService
from app.payment.approval.approval_workflow_service import ApprovalWorkflowService
from app.payment.approval.approved_payment_continuation_service import (
    ApprovedPaymentContinuationService,
)
from app.payment.approval.human_approval_service import (
    HumanApprovalError,
    HumanApprovalIntegrationService,
)
from app.payment.approval.reviewer_authorization_service import ReviewerAuthorizationService
from app.schemas.approval_request import ApprovalRequestRecord
from app.schemas.human_approval import HumanApprovalCommand, HumanReviewerContext
from app.schemas.payment import SupportedCurrency
from app.schemas.risk_engine import FinalRiskDecision, FinalRiskDecisionResult, RiskThresholdBand


@pytest.fixture
def test_setup() -> dict[str, Any]:
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
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()
    return {
        "req_svc": req_svc,
        "human_svc": human_svc,
        "audit_svc": audit_svc,
        "tenant_id": tenant_id,
        "agent_id": agent_id,
        "reviewer_id": reviewer_id,
    }


def _create_sample_request(
    req_svc: ApprovalRequestService, tenant_id: uuid.UUID, agent_id: uuid.UUID
) -> ApprovalRequestRecord:
    engine = ApprovalPolicyEngine()
    risk = FinalRiskDecisionResult(
        evaluation_id=uuid.uuid4(),
        decision_id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_adv_315",
        prediction_timestamp=datetime.now(UTC),
        decision=FinalRiskDecision.REVIEW,
        decision_reason="HIGH_RISK_REVIEW",
        composite_risk_score=80.0,
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
        decision_fingerprint="fp_dec_315",
        created_at=datetime.now(UTC),
    )
    eval_res = engine.evaluate_approval_requirement(
        risk, Decimal("25000.00"), SupportedCurrency.INR
    )
    res = req_svc.create_approval_request(
        risk,
        eval_res,
        idempotency_key="idemp_adv_315",
    )
    return res.request_record


def test_01_self_approval_adversarial_rejection(test_setup: dict[str, Any]) -> None:
    """Test 1: Originating agent attempting self-approval raises SELF_APPROVAL_FORBIDDEN."""
    req = _create_sample_request(
        test_setup["req_svc"], test_setup["tenant_id"], test_setup["agent_id"]
    )
    reviewer_ctx = HumanReviewerContext(
        reviewer_id=test_setup["agent_id"],  # Same as originating agent!
        tenant_id=test_setup["tenant_id"],
        reviewer_email="agent@agentpay.com",
        is_human_verified=True,
    )
    cmd = HumanApprovalCommand(
        approval_request_id=req.approval_request_id,
        tenant_id=req.tenant_id,
        expected_approval_fingerprint=req.approval_fingerprint,
        idempotency_key="idemp_self_app",
    )
    with pytest.raises(HumanApprovalError) as exc_info:
        test_setup["human_svc"].execute_human_approval(cmd, reviewer_ctx)
    assert exc_info.value.error_code == "SELF_APPROVAL_FORBIDDEN"


def test_02_bot_reviewer_identity_rejection(test_setup: dict[str, Any]) -> None:
    """Test 2: Reviewer identity containing 'bot' keyword raises AUTOMATED_REVIEWER_FORBIDDEN."""
    req = _create_sample_request(
        test_setup["req_svc"], test_setup["tenant_id"], test_setup["agent_id"]
    )
    reviewer_ctx = HumanReviewerContext(
        reviewer_id=test_setup["reviewer_id"],
        tenant_id=test_setup["tenant_id"],
        reviewer_email="bot.service@company.com",
        is_human_verified=True,
    )
    cmd = HumanApprovalCommand(
        approval_request_id=req.approval_request_id,
        tenant_id=req.tenant_id,
        expected_approval_fingerprint=req.approval_fingerprint,
        idempotency_key="idemp_bot_rev",
    )
    with pytest.raises(HumanApprovalError) as exc_info:
        test_setup["human_svc"].execute_human_approval(cmd, reviewer_ctx)
    assert exc_info.value.error_code == "AUTOMATED_REVIEWER_FORBIDDEN"


def test_03_unverified_human_context_rejection(test_setup: dict[str, Any]) -> None:
    """Test 3: Unverified human context raises error."""
    with pytest.raises(ValueError):
        HumanReviewerContext(
            reviewer_id=test_setup["reviewer_id"],
            tenant_id=test_setup["tenant_id"],
            is_human_verified=False,
        )


def test_04_cross_tenant_access_anti_enumeration(test_setup: dict[str, Any]) -> None:
    """Test 4: Discrepant tenant context raises CROSS_TENANT_ACCESS."""
    req = _create_sample_request(
        test_setup["req_svc"], test_setup["tenant_id"], test_setup["agent_id"]
    )
    reviewer_ctx = HumanReviewerContext(
        reviewer_id=test_setup["reviewer_id"],
        tenant_id=uuid.uuid4(),  # Different tenant!
        reviewer_email="human@agentpay.com",
        is_human_verified=True,
    )
    cmd = HumanApprovalCommand(
        approval_request_id=req.approval_request_id,
        tenant_id=req.tenant_id,
        expected_approval_fingerprint=req.approval_fingerprint,
        idempotency_key="idemp_cross_tenant",
    )
    with pytest.raises(HumanApprovalError) as exc_info:
        test_setup["human_svc"].execute_human_approval(cmd, reviewer_ctx)
    assert exc_info.value.error_code == "CROSS_TENANT_ACCESS"


def test_05_fingerprint_tampering_defense(test_setup: dict[str, Any]) -> None:
    """Test 5: Expected approval fingerprint tampering raises error."""
    req = _create_sample_request(
        test_setup["req_svc"], test_setup["tenant_id"], test_setup["agent_id"]
    )
    reviewer_ctx = HumanReviewerContext(
        reviewer_id=test_setup["reviewer_id"],
        tenant_id=test_setup["tenant_id"],
        reviewer_email="human@agentpay.com",
        is_human_verified=True,
    )
    cmd = HumanApprovalCommand(
        approval_request_id=req.approval_request_id,
        tenant_id=req.tenant_id,
        expected_approval_fingerprint="invalid_tampered_fingerprint",
        idempotency_key="idemp_tampered_fp",
    )
    with pytest.raises(HumanApprovalError):
        test_setup["human_svc"].execute_human_approval(cmd, reviewer_ctx)
