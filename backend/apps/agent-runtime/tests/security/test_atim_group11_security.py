"""Security and Adversarial tests for ATIM Group 11 (Phases 21 & 22)."""

import uuid

import pytest

from app.application.services.atim_authorization_service import ATIMAuthorizationService
from app.application.services.atim_idempotency_service import ATIMIdempotencyService
from app.domain.governance.compliance_models import ATIMSecurityContext


def test_01_cross_tenant_idempotency_isolation():
    idempotency_service = ATIMIdempotencyService()
    auth_service = ATIMAuthorizationService()

    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    key = "same_textual_key_123"
    op = "EXECUTE_PAYMENT"
    payload = {"amount": "100.00"}

    # Tenant A registers key
    idempotency_service.process_idempotent_request(tenant_a, op, key, payload)

    # Tenant B registers same textual key -> treated as separate key due to server-side tenant scoping
    is_dup_b, rec_b = idempotency_service.process_idempotent_request(tenant_b, op, key, payload)

    assert is_dup_b is False
    assert rec_b.tenant_id == tenant_b

    # User B attempting cross-tenant access to Tenant A's key fails closed
    sec_ctx_b = ATIMSecurityContext(user_id=uuid.uuid4(), tenant_id=tenant_b)

    with pytest.raises(PermissionError) as exc_info:
        auth_service.verify_tenant_boundary(sec_ctx_b, target_tenant_id=tenant_a)

    assert "Cross-tenant operation is forbidden" in str(exc_info.value)
