"""Unit tests for ATIM Cryptographic Audit Lock Service (Phase 15 / Group 8)."""

from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest

from app.application.services.atim_audit_lock_service import ATIMAuditLockService


@pytest.fixture
def audit_lock():
    return ATIMAuditLockService()


def test_01_generate_and_verify_audit_signature_success(audit_lock):
    tenant_id = uuid.uuid4()
    request_id = uuid.uuid4()
    payload = {
        "tenant_id": str(tenant_id),
        "request_id": str(request_id),
        "model": "openai/gpt-4o",
        "decision": "PROPOSAL_GENERATED",
        "amount_usd": "150.00",
    }

    record = audit_lock.generate_audit_signature(
        tenant_id=tenant_id,
        request_id=request_id,
        record_type="EXECUTION_PROPOSAL",
        payload=payload,
    )

    assert record.tenant_id == tenant_id
    assert record.request_id == request_id
    assert len(record.signature) == 64

    # Verify signature passes
    result = audit_lock.verify_audit_signature(
        request_id=request_id,
        payload=payload,
        expected_signature=record.signature,
    )

    assert result.is_valid is True
    assert result.status == "VALID"


def test_02_verify_audit_signature_tamper_detection(audit_lock):
    tenant_id = uuid.uuid4()
    request_id = uuid.uuid4()
    payload = {
        "tenant_id": str(tenant_id),
        "request_id": str(request_id),
        "model": "openai/gpt-4o",
        "amount_usd": "150.00",
    }

    record = audit_lock.generate_audit_signature(
        tenant_id=tenant_id,
        request_id=request_id,
        record_type="EXECUTION_PROPOSAL",
        payload=payload,
    )

    # Tamper with payload (change amount to $1500.00)
    tampered_payload = dict(payload)
    tampered_payload["amount_usd"] = "1500.00"

    result = audit_lock.verify_audit_signature(
        request_id=request_id,
        payload=tampered_payload,
        expected_signature=record.signature,
    )

    assert result.is_valid is False
    assert result.status == "TAMPER_DETECTED"
