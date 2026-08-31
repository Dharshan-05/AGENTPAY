"""Unit tests for ATIM Cryptographic Compliance Evidence Service (Phase 20 / Group 10)."""

import uuid

import pytest

from app.application.services.atim_compliance_evidence_service import ATIMComplianceEvidenceService
from app.domain.governance.compliance_models import ComplianceEventCategory


@pytest.fixture
def compliance_service():
    return ATIMComplianceEvidenceService()


def test_01_record_compliance_evidence_hmac_signing(compliance_service):
    tenant_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    corr_id = "corr_test_01J123456"

    rec = compliance_service.record_evidence(
        tenant_id=tenant_id,
        actor_id=actor_id,
        category=ComplianceEventCategory.POLICY_TRANSITION,
        correlation_id=corr_id,
        details={"action": "ACTIVATE_POLICY", "policy_id": "pol_123"},
    )

    assert rec.tenant_id == tenant_id
    assert rec.actor_id == actor_id
    assert rec.category == ComplianceEventCategory.POLICY_TRANSITION
    assert rec.correlation_id == corr_id
    assert len(rec.signature) == 64

    # Verify signature
    assert compliance_service.verify_evidence_record(rec) is True


def test_02_forensic_summary_generation(compliance_service):
    tenant_id = uuid.uuid4()

    compliance_service.record_evidence(
        tenant_id=tenant_id,
        actor_id=uuid.uuid4(),
        category=ComplianceEventCategory.SECURITY_BLOCK,
        correlation_id="corr_01",
        details={"block_type": "PROMPT_INJECTION"},
    )
    compliance_service.record_evidence(
        tenant_id=tenant_id,
        actor_id=uuid.uuid4(),
        category=ComplianceEventCategory.RATE_LIMIT_VIOLATION,
        correlation_id="corr_02",
        details={"endpoint": "/analyze"},
    )

    summary = compliance_service.get_forensic_summary(tenant_id)
    assert summary.tenant_id == tenant_id
    assert summary.total_evidence_records == 2
    assert summary.categories_breakdown[ComplianceEventCategory.SECURITY_BLOCK.value] == 1
    assert summary.categories_breakdown[ComplianceEventCategory.RATE_LIMIT_VIOLATION.value] == 1
    assert summary.integrity_verified is True
