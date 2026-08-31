"""Unit tests for ATIM Distributed Idempotency Service (Phase 21 / Group 11)."""

import uuid

import pytest

from app.application.services.atim_idempotency_service import ATIMIdempotencyService
from app.domain.governance.idempotency_models import IdempotencyState


@pytest.fixture
def idempotency_service():
    return ATIMIdempotencyService()


def test_01_first_time_idempotency_registration(idempotency_service):
    tenant_id = uuid.uuid4()
    op = "EXECUTE_PAYMENT"
    key = "idem_key_01"
    payload = {"amount": "100.00", "currency": "INR"}

    is_duplicate, record = idempotency_service.process_idempotent_request(
        tenant_id=tenant_id,
        operation=op,
        idempotency_key=key,
        payload=payload,
    )

    assert is_duplicate is False
    assert record.tenant_id == tenant_id
    assert record.idempotency_key == key
    assert record.state == IdempotencyState.PROCESSING


def test_02_duplicate_request_returns_saved_result(idempotency_service):
    tenant_id = uuid.uuid4()
    op = "EXECUTE_PAYMENT"
    key = "idem_key_02"
    payload = {"amount": "250.00", "currency": "INR"}

    # Register first time
    idempotency_service.process_idempotent_request(tenant_id, op, key, payload)

    # Complete request
    idempotency_service.complete_idempotent_request(
        tenant_id=tenant_id,
        operation=op,
        idempotency_key=key,
        state=IdempotencyState.SUCCEEDED,
        response_code=200,
        response_body={"status": "PAID", "payment_id": "pay_987654"},
    )

    # Second identical call -> returns duplicate saved record
    is_dup, saved_rec = idempotency_service.process_idempotent_request(tenant_id, op, key, payload)

    assert is_dup is True
    assert saved_rec.state == IdempotencyState.SUCCEEDED
    assert saved_rec.response_body["payment_id"] == "pay_987654"


def test_03_payload_mismatch_raises_error(idempotency_service):
    tenant_id = uuid.uuid4()
    op = "EXECUTE_PAYMENT"
    key = "idem_key_03"
    p1 = {"amount": "100.00"}
    p2 = {"amount": "500.00"}  # Modified payload with same key

    idempotency_service.process_idempotent_request(tenant_id, op, key, p1)

    with pytest.raises(ValueError) as exc_info:
        idempotency_service.process_idempotent_request(tenant_id, op, key, p2)

    assert "Payload mismatch" in str(exc_info.value)


def test_04_concurrent_request_in_progress_raises_error(idempotency_service):
    tenant_id = uuid.uuid4()
    op = "EXECUTE_PAYMENT"
    key = "idem_key_04"
    payload = {"amount": "100.00"}

    # Request 1 starts (in PROCESSING state)
    idempotency_service.process_idempotent_request(tenant_id, op, key, payload)

    # Concurrent Request 2 arrives while Request 1 is still PROCESSING
    with pytest.raises(PermissionError) as exc_info:
        idempotency_service.process_idempotent_request(tenant_id, op, key, payload)

    assert "currently in progress" in str(exc_info.value)
