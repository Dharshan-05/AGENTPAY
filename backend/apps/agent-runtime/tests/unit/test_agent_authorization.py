"""Unit and Security Tests for Agent Authorization Subsystem (Phase 183)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.agent_authorization_service import AgentAuthorizationService
from app.schemas.agent_identity_verification import AgentIdentityVerificationResult


@pytest.fixture
def service() -> AgentAuthorizationService:
    service = AgentAuthorizationService()
    service.identity_service.verify_agent_identity = AsyncMock()  # type: ignore[method-assign]
    service.authz_service.resolve_agent_permissions = AsyncMock()  # type: ignore[method-assign]
    service.authz_service.resolve_permissions = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_authorize_agent_action_success(
    service: AgentAuthorizationService,
) -> None:
    """1. Test successful agent action authorization when permissions present."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    principal_id = uuid.uuid4()

    service.identity_service.verify_agent_identity.return_value = (  # type: ignore[attr-defined]
        AgentIdentityVerificationResult(
            agent_id=agent_id,
            tenant_id=tenant_id,
            authenticated_principal_id=principal_id,
            verified=True,
            agent_status="active",
            verification_reason="OK",
            verified_at=datetime.now(UTC),
        )
    )
    service.authz_service.resolve_agent_permissions.return_value = frozenset(  # type: ignore[attr-defined]  # noqa: E501
        ["tools:execute", "products:read"]
    )
    service.authz_service.resolve_permissions.return_value = frozenset()  # type: ignore[attr-defined]  # noqa: E501

    mock_db = MagicMock()
    res = await service.authorize_agent_action(
        mock_db,
        tenant_id,
        agent_id,
        principal_id,
        action="tools:execute",
        required_permissions=["tools:execute"],
    )
    assert res.allowed is True
    assert res.agent_id == agent_id


@pytest.mark.asyncio
async def test_02_authorize_agent_action_denied_missing_permission(
    service: AgentAuthorizationService,
) -> None:
    """2. Test authorization denied when required permission is missing."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    principal_id = uuid.uuid4()

    service.identity_service.verify_agent_identity.return_value = (  # type: ignore[attr-defined]
        AgentIdentityVerificationResult(
            agent_id=agent_id,
            tenant_id=tenant_id,
            authenticated_principal_id=principal_id,
            verified=True,
            agent_status="active",
            verification_reason="OK",
            verified_at=datetime.now(UTC),
        )
    )
    service.authz_service.resolve_agent_permissions.return_value = frozenset(  # type: ignore[attr-defined]  # noqa: E501
        ["products:read"]
    )
    service.authz_service.resolve_permissions.return_value = frozenset()  # type: ignore[attr-defined]  # noqa: E501

    mock_db = MagicMock()
    res = await service.authorize_agent_action(
        mock_db,
        tenant_id,
        agent_id,
        principal_id,
        action="payments:create",
        required_permissions=["payments:create"],
    )
    assert res.allowed is False
    assert "missing" in res.decision_reason
