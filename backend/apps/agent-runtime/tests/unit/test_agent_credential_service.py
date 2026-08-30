"""Unit tests for Phase 122 — Agent Credential Service.

Tests:
- CSPRNG secret generation format
- Credential creation issues raw secret ONCE
- One-way cryptographic digest storage (raw secret NOT persisted)
- Credential metadata retrieval (strictly excludes secret hash)
- Constant-time secret verification
- Tenant isolation (cross-tenant credential lookup raises AgentCredentialNotFoundError)
- Duplicate credential identifier conflict handling
- Redaction verification (repr, schemas)
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.agent_credential_service import (
    AgentCredentialService,
    generate_agent_secret,
)
from app.core.tokens import hash_token
from app.domain.exceptions.agent_exceptions import (
    AgentCredentialAlreadyExistsError,
    AgentCredentialNotFoundError,
    AgentNotFoundError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_credential import AgentCredential
from app.schemas.agents import AgentCredentialCreateRequest, AgentCredentialResponse

_cred_service = AgentCredentialService()


def test_01_secret_generation_format() -> None:
    """Verify generate_agent_secret produces cryptographically secure prefixed string."""
    secret1 = generate_agent_secret()
    secret2 = generate_agent_secret()
    assert secret1.startswith("ap_ag_")
    assert secret2.startswith("ap_ag_")
    assert secret1 != secret2
    assert len(secret1) > 30


@pytest.mark.asyncio
async def test_02_create_credential_returns_raw_secret_once() -> None:
    """Verify create_credential generates raw secret and stores one-way hash."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_agent = MagicMock(spec=Agent)
    mock_agent.id = agent_id
    mock_agent.tenant_id = tenant_id

    db = AsyncMock()
    # Mock agent exists
    agent_result = MagicMock()
    agent_result.scalar_one_or_none.return_value = mock_agent
    # Mock no existing identifier conflict
    ident_result = MagicMock()
    ident_result.scalar_one_or_none.return_value = None

    db.execute.side_effect = [agent_result, ident_result]
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()

    req = AgentCredentialCreateRequest(credential_type="api_key")
    cred, raw_secret = await _cred_service.create_credential(db, tenant_id, agent_id, req)

    assert cred.agent_id == agent_id
    assert cred.tenant_id == tenant_id
    assert raw_secret.startswith("ap_ag_")
    assert cred.secret_hash == hash_token(raw_secret)
    assert cred.secret_hash != raw_secret  # Secret is hashed!


@pytest.mark.asyncio
async def test_03_create_credential_agent_not_found_idor() -> None:
    """Verify create_credential raises AgentNotFoundError if agent is missing or cross-tenant."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    db = AsyncMock()
    agent_result = MagicMock()
    agent_result.scalar_one_or_none.return_value = None
    db.execute.return_value = agent_result

    req = AgentCredentialCreateRequest()
    with pytest.raises(AgentNotFoundError):
        await _cred_service.create_credential(db, tenant_id, agent_id, req)


@pytest.mark.asyncio
async def test_04_create_credential_duplicate_identifier_conflict() -> None:
    """Verify duplicate credential_identifier in tenant raises AgentCredentialAlreadyExistsError."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_agent = MagicMock(spec=Agent)
    existing_cred = MagicMock(spec=AgentCredential)

    db = AsyncMock()
    agent_result = MagicMock()
    agent_result.scalar_one_or_none.return_value = mock_agent

    ident_result = MagicMock()
    ident_result.scalar_one_or_none.return_value = existing_cred

    db.execute.side_effect = [agent_result, ident_result]

    req = AgentCredentialCreateRequest(credential_identifier="duplicate-id")
    with pytest.raises(AgentCredentialAlreadyExistsError):
        await _cred_service.create_credential(db, tenant_id, agent_id, req)


@pytest.mark.asyncio
async def test_05_get_credential_cross_tenant_raises_not_found() -> None:
    """Verify get_credential raises AgentCredentialNotFoundError for cross-tenant access."""
    tenant_a = uuid.uuid4()
    agent_id = uuid.uuid4()
    credential_id = uuid.uuid4()

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    with pytest.raises(AgentCredentialNotFoundError):
        await _cred_service.get_credential(db, tenant_a, agent_id, credential_id)


@pytest.mark.asyncio
async def test_06_verify_credential_secret_success() -> None:
    """Verify verify_credential_secret verifies raw secret against stored hash."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    raw_secret = "ap_ag_test_secret_key_12345"

    mock_cred = MagicMock(spec=AgentCredential)
    mock_cred.status = "active"
    mock_cred.expires_at = None
    mock_cred.secret_hash = hash_token(raw_secret)

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = mock_cred
    db.execute.return_value = result

    is_valid = await _cred_service.verify_credential_secret(
        db, tenant_id, agent_id, "ag_key_ident", raw_secret
    )
    assert is_valid is True

    # Test invalid secret fails
    is_valid_wrong = await _cred_service.verify_credential_secret(
        db, tenant_id, agent_id, "ag_key_ident", "wrong_secret"
    )
    assert is_valid_wrong is False


def test_07_credential_response_schema_omits_secrets() -> None:
    """Verify AgentCredentialResponse model fields contain zero secret or hash attributes."""
    schema_fields = set(AgentCredentialResponse.model_fields.keys())
    forbidden = {"secret", "raw_secret", "secret_hash", "private_key", "password"}
    assert forbidden.isdisjoint(schema_fields)


def test_08_credential_repr_redacts_secret_hash() -> None:
    """Verify AgentCredential.__repr__ does not output secret_hash."""
    cred = AgentCredential(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        credential_type="api_key",
        secret_hash="sensitive_hash_digest_value",
        status="active",
    )
    repr_str = repr(cred)
    assert "sensitive_hash_digest_value" not in repr_str
    assert "secret_hash" not in repr_str
