"""Policy Management & CRUD Application Service for AGENTPAY (Phase 185–186)."""

from __future__ import annotations

import inspect
import logging
import re
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.policy_exceptions import (
    PolicyAlreadyExistsError,
    PolicyNotFoundError,
)
from app.infrastructure.database.models.security_policy import SecurityPolicy
from app.schemas.policies import (
    PolicyCreateRequest,
    PolicyListResponse,
    PolicyResponse,
    PolicyUpdateRequest,
)

logger = logging.getLogger("agentguard.security.policy_service")


class PolicyService:
    """Production service for Security Policy CRUD & lifecycle management (Phase 186)."""

    async def create_policy(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        request: PolicyCreateRequest,
        user_id: uuid.UUID | None = None,
    ) -> PolicyResponse:
        """Create a new Security Policy within tenant scope (Phase 186)."""
        slug = re.sub(r"[^a-z0-9]+", "-", request.name.lower()).strip("-") or "policy"
        slug = slug[:100]

        # 1. Duplicate slug check in tenant scope
        dup_stmt = select(SecurityPolicy).where(
            SecurityPolicy.tenant_id == tenant_id,
            SecurityPolicy.slug == slug,
            SecurityPolicy.deleted_at.is_(None),
        )
        res = db.execute(dup_stmt)
        if inspect.isawaitable(res):
            res = await res
        existing = res.scalars().first() if hasattr(res, "scalars") else None

        if existing:
            raise PolicyAlreadyExistsError(f"Policy with slug '{slug}' already exists in tenant.")

        now = datetime.now(UTC)
        policy = SecurityPolicy(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=request.name,
            slug=slug,
            description=request.description,
            status="draft",
            policy_type=request.policy_type.lower(),
            priority=request.priority,
            enforcement_mode=request.enforcement_mode.lower(),
            version=1,
            starts_at=request.starts_at,
            ends_at=request.ends_at,
            configuration=request.configuration,
            created_at=now,
            updated_at=now,
        )
        db.add(policy)
        db.commit()

        return self._to_policy_response(policy)

    async def get_policy(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        policy_id: uuid.UUID,
    ) -> PolicyResponse:
        """Get a single policy within tenant boundary fail-closed (Phase 186)."""
        policy = await self._fetch_policy(db, tenant_id, policy_id)
        return self._to_policy_response(policy)

    async def list_policies(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        *,
        status_filter: str | None = None,
        policy_type_filter: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> PolicyListResponse:
        """List policies in tenant scope with optional filtering and pagination (Phase 186)."""  # noqa: E501
        offset = (page - 1) * size

        stmt = select(SecurityPolicy).where(
            SecurityPolicy.tenant_id == tenant_id,
            SecurityPolicy.deleted_at.is_(None),
        )
        if status_filter:
            stmt = stmt.where(SecurityPolicy.status == status_filter.lower())
        if policy_type_filter:
            stmt = stmt.where(SecurityPolicy.policy_type == policy_type_filter.lower())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        c_res = db.execute(count_stmt)
        if inspect.isawaitable(c_res):
            c_res = await c_res
        total = c_res.scalar_one() if hasattr(c_res, "scalar_one") else 0

        stmt = (
            stmt.order_by(
                SecurityPolicy.priority.desc(), SecurityPolicy.name.asc(), SecurityPolicy.id.asc()
            )
            .offset(offset)
            .limit(size)
        )

        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res
        policies = res.scalars().all() if hasattr(res, "scalars") else []

        items = [self._to_policy_response(p) for p in policies]
        return PolicyListResponse(items=items, total=total, page=page, size=size)

    async def update_policy(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        policy_id: uuid.UUID,
        request: PolicyUpdateRequest,
    ) -> PolicyResponse:
        """Update policy mutable attributes, incrementing version (Phase 186)."""
        policy = await self._fetch_policy(db, tenant_id, policy_id)

        if request.name is not None:
            policy.name = request.name
        if request.description is not None:
            policy.description = request.description
        if request.priority is not None:
            policy.priority = request.priority
        if request.enforcement_mode is not None:
            policy.enforcement_mode = request.enforcement_mode.lower()
        if request.starts_at is not None:
            policy.starts_at = request.starts_at
        if request.ends_at is not None:
            policy.ends_at = request.ends_at
        if request.configuration is not None:
            policy.configuration = request.configuration

        policy.version += 1
        policy.updated_at = datetime.now(UTC)
        db.commit()

        return self._to_policy_response(policy)

    async def activate_policy(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        policy_id: uuid.UUID,
    ) -> PolicyResponse:
        """Activate a policy (Phase 186)."""
        policy = await self._fetch_policy(db, tenant_id, policy_id)
        policy.status = "active"
        policy.version += 1
        policy.updated_at = datetime.now(UTC)
        db.commit()
        return self._to_policy_response(policy)

    async def deactivate_policy(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        policy_id: uuid.UUID,
    ) -> PolicyResponse:
        """Deactivate a policy to inactive state (Phase 186)."""
        policy = await self._fetch_policy(db, tenant_id, policy_id)
        policy.status = "inactive"
        policy.version += 1
        policy.updated_at = datetime.now(UTC)
        db.commit()
        return self._to_policy_response(policy)

    async def archive_policy(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        policy_id: uuid.UUID,
    ) -> PolicyResponse:
        """Soft delete/archive a policy (Phase 186)."""
        policy = await self._fetch_policy(db, tenant_id, policy_id)
        now = datetime.now(UTC)
        policy.status = "archived"
        policy.deleted_at = now
        policy.updated_at = now
        db.commit()
        return self._to_policy_response(policy)

    async def _fetch_policy(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        policy_id: uuid.UUID,
    ) -> SecurityPolicy:
        """Helper fetching policy in tenant scope or raising 404 PolicyNotFoundError."""
        stmt = select(SecurityPolicy).where(
            SecurityPolicy.id == policy_id,
            SecurityPolicy.tenant_id == tenant_id,
            SecurityPolicy.deleted_at.is_(None),
        )
        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res
        policy = res.scalars().first() if hasattr(res, "scalars") else None

        if not policy:
            raise PolicyNotFoundError(f"Policy '{policy_id}' not found in tenant.")
        return policy

    def _to_policy_response(self, p: SecurityPolicy) -> PolicyResponse:
        """Map ORM entity to Pydantic transport model."""
        return PolicyResponse(
            id=p.id,
            tenant_id=p.tenant_id,
            name=p.name,
            slug=p.slug,
            description=p.description,
            status=p.status,
            policy_type=p.policy_type,
            priority=p.priority,
            enforcement_mode=p.enforcement_mode,
            version=p.version,
            starts_at=p.starts_at,
            ends_at=p.ends_at,
            configuration=p.configuration or {},
            created_at=p.created_at or datetime.now(UTC),
            updated_at=p.updated_at or datetime.now(UTC),
        )
