"""Security and Adversarial tests for ATIM Group 12 (Phase 23)."""

import uuid

import pytest

from app.application.services.atim_authorization_service import ATIMAuthorizationService
from app.application.services.atim_workflow_orchestrator import ATIMWorkflowOrchestrator
from app.domain.governance.compliance_models import ATIMSecurityContext


def test_01_cross_tenant_workflow_query_isolation():
    auth_service = ATIMAuthorizationService()
    orch = ATIMWorkflowOrchestrator()

    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()

    wf_a = orch.start_workflow(tenant_a, "PAYMENT_FLOW", "corr_sec_01")

    # Tenant B attempts to query Tenant A workflow
    sec_ctx_b = ATIMSecurityContext(user_id=uuid.uuid4(), tenant_id=tenant_b)

    with pytest.raises(PermissionError) as exc_info:
        auth_service.verify_tenant_boundary(sec_ctx_b, target_tenant_id=wf_a.tenant_id)

    assert "Cross-tenant operation is forbidden" in str(exc_info.value)
