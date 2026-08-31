"""Security and Adversarial tests for ATIM Group 10 (Phases 19 & 20)."""

import uuid

import pytest

from app.application.services.atim_authorization_service import ATIMAuthorizationService
from app.application.services.atim_compliance_evidence_service import ATIMComplianceEvidenceService
from app.domain.governance.compliance_models import (
    ATIMSecurityContext,
    ComplianceEventCategory,
    SecurityPermission,
)


def test_01_cross_tenant_evidence_query_isolation():
    auth_service = ATIMAuthorizationService()
    comp_service = ATIMComplianceEvidenceService()

    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    user_a = uuid.uuid4()

    # Record evidence for Tenant A
    comp_service.record_evidence(
        tenant_id=tenant_a,
        actor_id=user_a,
        category=ComplianceEventCategory.SECURITY_BLOCK,
        correlation_id="corr_01",
        details={"reason": "Prompt injection detected"},
    )

    # User A tries to query Tenant B evidence
    security_ctx_a = ATIMSecurityContext(user_id=user_a, tenant_id=tenant_a, permissions=[SecurityPermission.ATIM_POLICY_AUDIT])

    with pytest.raises(PermissionError) as exc_info:
        auth_service.verify_tenant_boundary(security_ctx_a, target_tenant_id=tenant_b)

    assert "Cross-tenant operation is forbidden" in str(exc_info.value)

    # Forensic summary for Tenant B has zero records
    summary_b = comp_service.get_forensic_summary(tenant_b)
    assert summary_b.total_evidence_records == 0


def test_02_decision_precedence_security_block_takes_highest_precedence():
    comp_service = ATIMComplianceEvidenceService()
    tenant_id = uuid.uuid4()

    rec = comp_service.record_evidence(
        tenant_id=tenant_id,
        actor_id=uuid.uuid4(),
        category=ComplianceEventCategory.SECURITY_BLOCK,
        correlation_id="corr_precedence_check",
        details={"decision": "DENY"},
    )

    assert rec.decision_precedence == "SECURITY BLOCK > PLAN INVALID > AGENTGUARD DENY > FRAUDGUARD BLOCK > HITL REQUIRED > ALLOW"
