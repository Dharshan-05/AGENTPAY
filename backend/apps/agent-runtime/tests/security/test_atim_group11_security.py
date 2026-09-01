"""Security and Adversarial tests for ATIM Group 11 (Phases 21 & 22)."""

import uuid
import pytest

from app.application.services.atim_authorization_service import ATIMAuthorizationService
from app.application.services.atim_idempotency_service import ATIMIdempotencyService
from app.domain.governance.compliance_models import ATIMSecurityContext
from app.domain.governance.idempotency_models import IdempotencyState


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


def test_02_idempotency_payload_tampering_rejected():
    idempotency_service = ATIMIdempotencyService()
    tenant_id = uuid.uuid4()
    key = "tamper_test_key_555"
    op = "EXECUTE_PAYMENT"

    payload_orig = {"amount": "100.00", "currency": "INR"}
    payload_altered = {"amount": "10000.00", "currency": "INR"}

    # 1. Register original request
    idempotency_service.process_idempotent_request(tenant_id, op, key, payload_orig)
    idempotency_service.complete_idempotent_request(
        tenant_id, op, key, IdempotencyState.SUCCEEDED, 200, {"status": "SUCCESS"}
    )

    # 2. Replay with altered payload -> MUST be rejected (ValueError)
    with pytest.raises(ValueError) as exc_info:
        idempotency_service.process_idempotent_request(tenant_id, op, key, payload_altered)

    assert "Payload mismatch" in str(exc_info.value)


def test_03_concurrent_idempotency_request_rejected():
    idempotency_service = ATIMIdempotencyService()
    tenant_id = uuid.uuid4()
    key = "concurrent_key_999"
    op = "EXECUTE_PAYMENT"
    payload = {"amount": "250.00"}

    # Request 1 -> PROCESSING state
    idempotency_service.process_idempotent_request(tenant_id, op, key, payload)

    # Request 2 with same key while request 1 is PROCESSING -> MUST raise PermissionError
    with pytest.raises(PermissionError) as exc_info:
        idempotency_service.process_idempotent_request(tenant_id, op, key, payload)

    assert "in progress" in str(exc_info.value)

