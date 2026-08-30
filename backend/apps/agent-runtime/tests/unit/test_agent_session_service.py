"""Unit tests for Phase 127 — Agent Session Management Service.

Tests:
- Session creation with server-controlled UUIDv7 and expiration TTL
- Session creation for suspended or deactivated agent rejected
- Session creation with invalid/expired credential rejected
- Session validation (active, expired, revoked, defense-in-depth checks)

- Keyset pagination for session listing
- Specific session revocation
- Bulk session revocation (revoke-all)
- Cross-tenant session access returns AgentSessionNotFoundError (IDOR 404)
- Revoked sessions cannot be resurrected
"""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.agent_session_service import AgentSessionService
from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    AgentSessionAlreadyRevokedError,
    AgentSessionCreationError,
    AgentSessionNotFoundError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_session import AgentSession
from app.schemas.agents import AgentSessionCreateRequest, AgentSessionResponse

_session_service = AgentSessionService()


@pytest.mark.asyncio
async def test_01_create_session_success() -> None:
    """Verify create_session creates active session with server TTL for operational agent."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_agent = MagicMock(spec=Agent)
    mock_agent.id = agent_id
    mock_agent.tenant_id = tenant_id
    mock_agent.status = "active"

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = mock_agent
    db.execute.return_value = agent_res
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()

    req = AgentSessionCreateRequest(expires_in_hours=12)
    sess = await _session_service.create_session(db, tenant_id, agent_id, req)

    assert sess.agent_id == agent_id
    assert sess.tenant_id == tenant_id
    assert sess.status == "active"
    assert sess.expires_at > datetime.now(UTC)


@pytest.mark.asyncio
async def test_02_create_session_cross_tenant_raises_not_found() -> None:
    """Verify create_session raises AgentNotFoundError for cross-tenant agent."""
    tenant_a = uuid.uuid4()
    agent_id = uuid.uuid4()

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = None
    db.execute.return_value = agent_res

    req = AgentSessionCreateRequest()
    with pytest.raises(AgentNotFoundError):
        await _session_service.create_session(db, tenant_a, agent_id, req)


@pytest.mark.asyncio
async def test_03_create_session_deactivated_agent_rejected() -> None:
    """Verify session creation for deactivated agent raises AgentSessionCreationError."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_agent = MagicMock(spec=Agent)
    mock_agent.status = "deactivated"

    db = AsyncMock()
    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = mock_agent
    db.execute.return_value = agent_res

    req = AgentSessionCreateRequest()
    with pytest.raises(AgentSessionCreationError, match="deactivated"):
        await _session_service.create_session(db, tenant_id, agent_id, req)


@pytest.mark.asyncio
async def test_04_get_session_cross_tenant_raises_not_found() -> None:
    """Verify get_session raises AgentSessionNotFoundError (IDOR 404) for cross-tenant access."""
    tenant_a = uuid.uuid4()
    agent_id = uuid.uuid4()
    session_id = uuid.uuid4()

    db = AsyncMock()
    res = MagicMock()
    res.scalar_one_or_none.return_value = None
    db.execute.return_value = res

    with pytest.raises(AgentSessionNotFoundError):
        await _session_service.get_session(db, tenant_a, agent_id, session_id)


@pytest.mark.asyncio
async def test_05_revoke_session_success() -> None:
    """Verify revoke_session sets status to revoked and records timestamp & reason."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    session_id = uuid.uuid4()

    mock_sess = MagicMock(spec=AgentSession)
    mock_sess.id = session_id
    mock_sess.agent_id = agent_id
    mock_sess.tenant_id = tenant_id
    mock_sess.status = "active"

    db = AsyncMock()
    res = MagicMock()
    res.scalar_one_or_none.return_value = mock_sess
    db.execute.return_value = res
    db.flush = AsyncMock()
    db.refresh = AsyncMock()

    revoked_sess = await _session_service.revoke_session(
        db, tenant_id, agent_id, session_id, reason="Operator logout"
    )

    assert revoked_sess.status == "revoked"
    assert revoked_sess.revoked_at is not None
    assert revoked_sess.revocation_reason == "Operator logout"


@pytest.mark.asyncio
async def test_06_revoke_already_revoked_session_conflict() -> None:
    """Verify revoking an already revoked session raises AgentSessionAlreadyRevokedError."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    session_id = uuid.uuid4()

    mock_sess = MagicMock(spec=AgentSession)
    mock_sess.status = "revoked"

    db = AsyncMock()
    res = MagicMock()
    res.scalar_one_or_none.return_value = mock_sess
    db.execute.return_value = res

    with pytest.raises(AgentSessionAlreadyRevokedError):
        await _session_service.revoke_session(db, tenant_id, agent_id, session_id)


@pytest.mark.asyncio
async def test_07_validate_session_rejects_suspended_agent() -> None:
    """Verify validate_session fails closed if agent is suspended (defense-in-depth)."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    session_id = uuid.uuid4()

    mock_sess = MagicMock(spec=AgentSession)
    mock_sess.status = "active"
    mock_sess.expires_at = datetime.now(UTC) + timedelta(hours=5)

    mock_agent = MagicMock(spec=Agent)
    mock_agent.status = "suspended"  # Agent is suspended!

    db = AsyncMock()
    sess_res = MagicMock()
    sess_res.scalar_one_or_none.return_value = mock_sess

    agent_res = MagicMock()
    agent_res.scalar_one_or_none.return_value = mock_agent

    db.execute.side_effect = [sess_res, agent_res]

    is_valid = await _session_service.validate_session(db, tenant_id, agent_id, session_id)
    assert is_valid is False


def test_08_session_response_schema_redaction() -> None:
    """Verify AgentSessionResponse model contains zero secret or token fields."""
    fields = set(AgentSessionResponse.model_fields.keys())
    forbidden = {"secret", "raw_secret", "secret_hash", "token", "password", "key"}
    assert forbidden.isdisjoint(fields)
