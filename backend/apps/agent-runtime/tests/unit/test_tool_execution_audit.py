"""Unit and Security Tests for Tool Execution Audit Subsystem (Phase 159)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.application.services.tool_audit_service import ToolAuditService, _sanitize_tool_metadata
from app.infrastructure.database.models.tool_execution_audit import ToolExecutionAudit


@pytest.fixture
def service() -> ToolAuditService:
    return ToolAuditService()


@pytest.mark.asyncio
async def test_01_secret_metadata_redaction() -> None:
    """1. Verify sensitive keys (passwords, tokens, API keys) are redacted from metadata."""
    raw_metadata = {
        "password": "SuperSecretPassword123!",
        "access_token": "bearer-token-abc-123",
        "normal_key": "safe_value",
        "nested": {
            "api_key": "secret-api-key-999",
            "user_id": "usr_123",
        },
    }

    clean = _sanitize_tool_metadata(raw_metadata)
    assert clean["password"] == "[REDACTED]"
    assert clean["access_token"] == "[REDACTED]"
    assert clean["normal_key"] == "safe_value"
    assert clean["nested"]["api_key"] == "[REDACTED]"
    assert clean["nested"]["user_id"] == "usr_123"


@pytest.mark.asyncio
async def test_02_record_tool_execution_audit_success(
    service: ToolAuditService,
) -> None:
    """2. Test recording append-only immutable tool execution audit entry."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    user_id = uuid.uuid4()
    exec_id = uuid.uuid4()

    mock_db = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.add = MagicMock()

    res = await service.record_tool_execution_audit(
        mock_db,
        tenant_id=tenant_id,
        agent_id=agent_id,
        tool_id="currency_converter",
        execution_state="SUCCEEDED",
        user_id=user_id,
        execution_id=exec_id,
        duration_ms=42.5,
        payload_metadata={"amount": 100, "password": "hidden"},
    )

    assert res.tenant_id == tenant_id
    assert res.agent_id == agent_id
    assert res.tool_id == "currency_converter"
    assert res.execution_state == "SUCCEEDED"
    assert res.duration_ms == 42.5
    assert res.payload_metadata["password"] == "[REDACTED]"


@pytest.mark.asyncio
async def test_03_list_tool_execution_audits_tenant_isolated(
    service: ToolAuditService,
) -> None:
    """3. Test tenant-isolated audit log listing."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    audit_entry = MagicMock(spec=ToolExecutionAudit)
    audit_entry.id = uuid.uuid4()
    audit_entry.tenant_id = tenant_id
    audit_entry.agent_id = agent_id
    audit_entry.user_id = None
    audit_entry.execution_id = uuid.uuid4()
    audit_entry.request_id = "req_123"
    audit_entry.correlation_id = "corr_123"
    audit_entry.tool_id = "payment_initiation"
    audit_entry.tool_version = "1.0.0"
    audit_entry.permission_decision = "ALLOW"
    audit_entry.approval_state = "NOT_REQUIRED"
    audit_entry.execution_state = "SUCCEEDED"
    audit_entry.risk_classification = "MEDIUM"
    audit_entry.duration_ms = 15.0
    audit_entry.error_code = None
    audit_entry.environment = "production"
    audit_entry.payload_metadata = {}
    audit_entry.created_at = datetime.now(UTC)

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = [audit_entry]

    res = await service.list_tool_execution_audits(mock_db, tenant_id=tenant_id, agent_id=agent_id)
    assert res.tenant_id == tenant_id
    assert res.total_count == 1
    assert res.audits[0].tool_id == "payment_initiation"
