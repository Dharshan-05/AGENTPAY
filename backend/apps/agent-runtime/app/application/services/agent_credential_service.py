"""Agent Credential application service for AGENTPAY (Phase 122).

Responsibilities:
    - Cryptographically secure secret generation using `secrets.token_urlsafe`
    - One-way SHA-256 cryptographic digest storage (never storing raw secrets)
    - Single-delivery raw secret return ONCE upon creation
    - Safe credential metadata retrieval (strictly excluding secret_hash and raw_secret)
    - Constant-time secret verification using `secrets.compare_digest`
    - Strict multi-tenancy isolation (`WHERE tenant_id = :tenant_id`)

Security Invariants:
    - Raw secrets are never saved in database records, logs, exception tracebacks, or repr()
    - Credential verification uses constant-time digest comparison to prevent timing attacks
    - All queries enforce tenant scope to prevent cross-tenant credential leaks
"""

from __future__ import annotations

import logging
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tokens import hash_token
from app.domain.exceptions.agent_exceptions import (
    AgentCredentialAlreadyExistsError,
    AgentCredentialNotFoundError,
    AgentNotFoundError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_credential import AgentCredential
from app.schemas.agents import AgentCredentialCreateRequest

logger = logging.getLogger("agentpay.agent.credential.service")


def generate_agent_secret(prefix: str = "ap_ag_") -> str:
    """Generate a cryptographically secure URL-safe secret token.

    Example format: `ap_ag_x8F2k9...`
    Uses Python's secrets module (CSPRNG). Never uses random, UUIDs, or timestamps.
    """
    raw_random = secrets.token_urlsafe(32)
    return f"{prefix}{raw_random}"


class AgentCredentialService:
    """Application service for managing AgentCredential domain entities and secret lifecycle."""

    async def create_credential(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        request: AgentCredentialCreateRequest,
    ) -> tuple[AgentCredential, str]:
        """Issue a new secure credential for an agent within the authenticated tenant.

        Behavior:
            - Verifies agent exists in tenant (IDOR check)
            - Generates cryptographically secure raw secret
            - Stores one-way SHA-256 digest in `secret_hash`
            - Returns (credential_record, raw_secret) for one-time client delivery

        Raises:
            AgentNotFoundError: if agent is not found or belongs to another tenant.
            AgentCredentialAlreadyExistsError: if credential_identifier collides within tenant.
        """
        # 1. Verify agent exists in tenant (IDOR protection)
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        res = await db.execute(agent_stmt)
        if res.scalar_one_or_none() is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        # 2. Generate secret and compute one-way digest
        raw_secret = generate_agent_secret()
        digest = hash_token(raw_secret)

        # 3. Generate or validate lookup identifier
        identifier = request.credential_identifier or f"ag_key_{uuid.uuid4().hex[:12]}"

        # 4. Check identifier collision within tenant
        ident_stmt = select(AgentCredential).where(
            AgentCredential.tenant_id == tenant_id,
            AgentCredential.credential_identifier == identifier,
            AgentCredential.status == "active",
        )
        ident_res = await db.execute(ident_stmt)
        if ident_res.scalar_one_or_none() is not None:
            raise AgentCredentialAlreadyExistsError(
                f"Credential identifier '{identifier}' already exists in tenant."
            )

        # 5. Compute expiration timestamp
        expires_at: datetime | None = None
        if request.expires_in_days is not None:
            expires_at = datetime.now(UTC) + timedelta(days=request.expires_in_days)

        # 6. Instantiate & save ORM record
        credential = AgentCredential(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            credential_type=request.credential_type.strip(),
            credential_identifier=identifier,
            secret_hash=digest,
            status="active",
            expires_at=expires_at,
        )
        db.add(credential)
        await db.flush()
        await db.refresh(credential)

        logger.info(
            "Agent credential issued successfully",
            extra={
                "credential_id": str(credential.id),
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "credential_type": credential.credential_type,
            },
        )
        return credential, raw_secret

    async def get_credential(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        credential_id: uuid.UUID,
    ) -> AgentCredential:
        """Retrieve safe credential metadata by ID (strictly excluding secret_hash).

        Raises:
            AgentCredentialNotFoundError: if credential does not exist or cross-tenant.
        """
        stmt = select(AgentCredential).where(
            AgentCredential.id == credential_id,
            AgentCredential.agent_id == agent_id,
            AgentCredential.tenant_id == tenant_id,
        )
        result = await db.execute(stmt)
        cred = result.scalar_one_or_none()
        if cred is None:
            raise AgentCredentialNotFoundError(
                f"Credential {credential_id} not found for agent {agent_id}."
            )
        return cred

    async def list_credentials(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> list[AgentCredential]:
        """List active/historical credential metadata records for an agent within tenant scope."""
        stmt = (
            select(AgentCredential)
            .where(
                AgentCredential.agent_id == agent_id,
                AgentCredential.tenant_id == tenant_id,
            )
            .order_by(AgentCredential.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def verify_credential_secret(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        credential_identifier: str,
        raw_secret: str,
    ) -> bool:
        """Verify a provided raw secret against the stored one-way secret_hash in constant time.

        Returns:
            True if verification succeeds and credential is active & unexpired; False otherwise.
        """
        stmt = select(AgentCredential).where(
            AgentCredential.tenant_id == tenant_id,
            AgentCredential.agent_id == agent_id,
            AgentCredential.credential_identifier == credential_identifier,
            AgentCredential.status == "active",
        )
        res = await db.execute(stmt)
        cred = res.scalar_one_or_none()
        if cred is None:
            return False

        # Check expiration
        now = datetime.now(UTC)
        if cred.expires_at is not None and now > cred.expires_at:
            return False

        # Constant-time hash verification
        computed_hash = hash_token(raw_secret)
        return secrets.compare_digest(computed_hash, cred.secret_hash)
