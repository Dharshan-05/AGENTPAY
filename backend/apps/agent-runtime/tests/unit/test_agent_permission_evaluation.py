"""Unit and Security Tests for Agent Permission Evaluation Subsystem (Phase 184)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.agent_permission_evaluation_service import (
    AgentPermissionEvaluationService,
)
from app.schemas.agent_identity_verification import AgentIdentityVerificationResult


@pytest.fixture
def service() -> AgentPermissionEvaluationService:
    service = AgentPermissionEvaluationService()
    service.identity_service.verify_agent_identity = AsyncMock()  # type: ignore[method-assign]
    service.authz_service.resolve_agent_permissions = AsyncMock()  # type: ignore[method-assign]
    service.authz_service.resolve_permissions = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_evaluate_permissions_granted(
    service: AgentPermissionEvaluationService,
) -> None:
    """1. Test evaluation returns GRANTED when all requested permissions are present."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    now = datetime.now(UTC)

    service.identity_service.verify_agent_identity.return_value = (  # type: ignore[attr-defined]
        AgentIdentityVerificationResult(
            agent_id=agent_id,
            tenant_id=tenant_id,
            authenticated_principal_id=None,
            verified=True,
            agent_status="active",
            verification_reason="OK",
            verified_at=now,
        )
    )
    service.authz_service.resolve_agent_permissions.return_value = frozenset(  # type: ignore[attr-defined]  # noqa: E501
        ["products:read", "tools:execute"]
    )

    mock_db = MagicMock()
    res = await service.evaluate_agent_permissions(
        mock_db, tenant_id, agent_id, requested_permissions=["products:read", "tools:execute"]
    )
    assert res.decision == "GRANTED"
    assert res.reason_code == "PERMISSION_GRANTED"
    assert len(res.missing_permissions) == 0


@pytest.mark.asyncio
async def test_02_evaluate_permissions_denied(
    service: AgentPermissionEvaluationService,
) -> None:
    """2. Test evaluation returns DENIED when a requested permission is missing."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    now = datetime.now(UTC)

    service.identity_service.verify_agent_identity.return_value = (  # type: ignore[attr-defined]
        AgentIdentityVerificationResult(
            agent_id=agent_id,
            tenant_id=tenant_id,
            authenticated_principal_id=None,
            verified=True,
            agent_status="active",
            verification_reason="OK",
            verified_at=now,
        )
    )
    service.authz_service.resolve_agent_permissions.return_value = frozenset(  # type: ignore[attr-defined]  # noqa: E501
        ["products:read"]
    )

    mock_db = MagicMock()
    res = await service.evaluate_agent_permissions(
        mock_db, tenant_id, agent_id, requested_permissions=["products:read", "payments:create"]
    )
    assert res.decision == "DENIED"
    assert res.reason_code == "PERMISSION_MISSING"
    assert "payments:create" in res.missing_permissions
