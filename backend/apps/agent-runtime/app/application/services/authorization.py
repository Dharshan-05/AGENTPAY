"""AGENTPAY Authorization Service (Phase 111–130).

Centralized authorization engine responsible for:
- Resolving user permissions via role membership
- Resolving agent permissions via direct permission assignment & role inheritance
- has_permission() / require_permission() policy evaluation
- Role CRUD and user/agent-role assignment
- Role-permission & agent-permission assignment
- Default-deny authorization (fail-closed)
- Tenant-isolated role and permission operations
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.authorization.context import AuthorizationContext
from app.domain.authorization.decision import AuthorizationDecision
from app.domain.authorization.permissions_registry import ALL_PERMISSIONS
from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    AgentPermissionAlreadyAssignedError,
    AgentPermissionAssignmentError,
    AgentPermissionNotFoundError,
    AgentRoleAlreadyAssignedError,
    AgentRoleAssignmentError,
    AgentRoleNotFoundError,
)
from app.domain.exceptions.auth_exceptions import PermissionDeniedError
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_permission import AgentPermission
from app.infrastructure.database.models.agent_role import AgentRole
from app.infrastructure.database.models.permission import Permission
from app.infrastructure.database.models.role import Role
from app.infrastructure.database.models.role_permission import RolePermission
from app.infrastructure.database.models.user_role import UserRole


class AuthorizationService:
    """Production-grade RBAC authorization engine.

    All methods are async and require an active database session.
    All operations enforce tenant isolation.
    Default-deny — missing permission implies deny.
    """

    # ------------------------------------------------------------------
    # Permission Resolution
    # ------------------------------------------------------------------

    async def resolve_permissions(
        self,
        db: AsyncSession,
        context: AuthorizationContext,
    ) -> frozenset[str]:
        """Resolve the complete set of permission names for the user in their tenant.

        Uses a single JOIN query to avoid N+1 lookups.
        user_roles(tenant_id=T, user_id=U) → roles(tenant_id=T) → role_permissions → permissions

        Returns:
            Frozenset of canonical permission name strings (e.g. "payments:read").
        """
        stmt = (
            select(Permission.name)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(
                UserRole,
                (UserRole.role_id == Role.id)
                & (UserRole.tenant_id == context.tenant_id)
                & (UserRole.user_id == context.user_id),
            )
            .where(
                or_(Role.tenant_id == context.tenant_id, Role.is_system.is_(True)),
                Role.status == "active",
                Role.deleted_at.is_(None),
            )
            .distinct()
        )
        result = await db.execute(stmt)
        return frozenset(row for row in result.scalars())

    async def resolve_agent_permissions(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> frozenset[str]:
        """Resolve effective permissions for an agent within tenant scope.

        Effective permissions = Direct AgentPermissions + Inherited RolePermissions.

        Returns:
            Frozenset of canonical permission name strings.
        """
        # 1. Direct permissions
        direct_stmt = (
            select(Permission.name)
            .join(AgentPermission, AgentPermission.permission_id == Permission.id)
            .where(
                AgentPermission.agent_id == agent_id,
                AgentPermission.tenant_id == tenant_id,
            )
        )
        direct_res = await db.execute(direct_stmt)
        direct_perms = set(direct_res.scalars().all())

        # 2. Inherited permissions via roles
        inherited_stmt = (
            select(Permission.name)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(
                AgentRole,
                (AgentRole.role_id == Role.id)
                & (AgentRole.tenant_id == tenant_id)
                & (AgentRole.agent_id == agent_id),
            )
            .where(
                or_(Role.tenant_id == tenant_id, Role.is_system.is_(True)),
                Role.status == "active",
                Role.deleted_at.is_(None),
            )
            .distinct()
        )
        inherited_res = await db.execute(inherited_stmt)
        inherited_perms = set(inherited_res.scalars().all())

        return frozenset(direct_perms | inherited_perms)

    async def has_permission(
        self,
        db: AsyncSession,
        context: AuthorizationContext,
        permission: str,
    ) -> AuthorizationDecision:
        """Evaluate whether the principal holds the required permission."""
        if not permission:
            return AuthorizationDecision.deny(
                permission=permission,
                reason="Empty permission string is never allowed.",
            )

        granted = await self.resolve_permissions(db, context)

        if permission in granted:
            return AuthorizationDecision.allow(permission=permission)

        return AuthorizationDecision.deny(
            permission=permission,
            reason=f"Principal does not hold permission '{permission}'.",
        )

    async def require_permission(
        self,
        db: AsyncSession,
        context: AuthorizationContext,
        permission: str,
    ) -> None:
        """Assert the principal holds the required permission or raise PermissionDeniedError."""
        decision = await self.has_permission(db, context, permission)
        if not decision.allowed:
            raise PermissionDeniedError(permission=permission)

    # ------------------------------------------------------------------
    # Role Management (Phase 112)
    # ------------------------------------------------------------------

    async def list_roles(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
    ) -> list[Role]:
        """List all active roles for the given tenant."""
        stmt = select(Role).where(
            or_(Role.tenant_id == tenant_id, Role.is_system.is_(True)),
            Role.deleted_at.is_(None),
        )
        result = await db.execute(stmt)
        return list(result.scalars())

    async def get_role(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        role_id: uuid.UUID,
    ) -> Role | None:
        """Retrieve a single role within tenant scope or system roles."""
        stmt = select(Role).where(
            Role.id == role_id,
            or_(Role.tenant_id == tenant_id, Role.is_system.is_(True)),
            Role.deleted_at.is_(None),
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_role(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        name: str,
        description: str | None = None,
    ) -> Role:
        """Create a new tenant-scoped role."""
        existing = await db.execute(
            select(Role).where(
                Role.tenant_id == tenant_id,
                Role.name == name,
                Role.deleted_at.is_(None),
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise ValueError(f"Role '{name}' already exists in this tenant.")

        role = Role(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=name,
            description=description,
            is_system=False,
            status="active",
        )
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role

    async def update_role(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        role_id: uuid.UUID,
        updates: dict[str, Any],
    ) -> Role:
        """Update allowed fields on a tenant-scoped role."""
        role = await self.get_role(db, tenant_id, role_id)
        if role is None:
            raise ValueError("Role not found.")
        if role.is_system:
            raise ValueError("System roles cannot be modified.")

        new_name = updates.get("name")
        if new_name and new_name != role.name:
            conflict = await db.execute(
                select(Role).where(
                    Role.tenant_id == tenant_id,
                    Role.name == new_name,
                    Role.deleted_at.is_(None),
                )
            )
            if conflict.scalar_one_or_none() is not None:
                raise ValueError(f"Role '{new_name}' already exists in this tenant.")
            role.name = new_name

        if "description" in updates:
            role.description = updates["description"]
        if "status" in updates:
            role.status = updates["status"]

        await db.commit()
        await db.refresh(role)
        return role

    async def assign_role_to_user(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
    ) -> UserRole:
        """Assign a tenant-scoped role to a user."""
        role = await self.get_role(db, tenant_id, role_id)
        if role is None:
            raise ValueError("Role not found in this tenant.")

        existing = await db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
                UserRole.tenant_id == tenant_id,
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise ValueError("Role is already assigned to this user.")

        user_role = UserRole(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            role_id=role_id,
        )
        db.add(user_role)
        await db.commit()
        await db.refresh(user_role)
        return user_role

    async def remove_role_from_user(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
    ) -> None:
        """Remove a role assignment from a user within tenant scope."""
        result = await db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
                UserRole.tenant_id == tenant_id,
            )
        )
        user_role = result.scalar_one_or_none()
        if user_role is None:
            raise ValueError("Role assignment not found.")

        await db.delete(user_role)
        await db.commit()

    async def list_user_roles(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> list[Role]:
        """List all roles assigned to a user within tenant scope."""
        stmt = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == user_id,
                UserRole.tenant_id == tenant_id,
                Role.tenant_id == tenant_id,
                Role.deleted_at.is_(None),
            )
        )
        result = await db.execute(stmt)
        return list(result.scalars())

    # ------------------------------------------------------------------
    # Permission Management (Phase 113)
    # ------------------------------------------------------------------

    async def list_permissions(
        self,
        db: AsyncSession,
    ) -> list[Permission]:
        """List all registered permissions."""
        stmt = select(Permission)
        result = await db.execute(stmt)
        return list(result.scalars())

    async def get_permission(
        self,
        db: AsyncSession,
        permission_id: uuid.UUID,
    ) -> Permission | None:
        """Retrieve a permission by ID."""
        stmt = select(Permission).where(Permission.id == permission_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def grant_role_permission(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        role_id: uuid.UUID,
        permission_id: uuid.UUID,
    ) -> RolePermission:
        """Assign a permission to a role within tenant scope."""
        role = await self.get_role(db, tenant_id, role_id)
        if role is None:
            raise ValueError("Role not found in this tenant.")

        perm = await self.get_permission(db, permission_id)
        if perm is None:
            raise ValueError("Permission not found.")

        existing = await db.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise ValueError("Permission is already assigned to this role.")

        rp = RolePermission(
            id=uuid.uuid4(),
            role_id=role_id,
            permission_id=permission_id,
        )
        db.add(rp)
        await db.commit()
        await db.refresh(rp)
        return rp

    async def revoke_role_permission(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        role_id: uuid.UUID,
        permission_id: uuid.UUID,
    ) -> None:
        """Remove a permission from a role."""
        role = await self.get_role(db, tenant_id, role_id)
        if role is None:
            raise ValueError("Role not found in this tenant.")

        result = await db.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
        )
        rp = result.scalar_one_or_none()
        if rp is None:
            raise ValueError("Permission assignment not found.")

        await db.delete(rp)
        await db.commit()

    async def list_role_permissions(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        role_id: uuid.UUID,
    ) -> list[Permission]:
        """List permissions assigned to a specific role within tenant scope."""
        role = await self.get_role(db, tenant_id, role_id)
        if role is None:
            return []

        stmt = (
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == role_id)
        )
        result = await db.execute(stmt)
        return list(result.scalars())

    # ------------------------------------------------------------------
    # Phase 128 — Agent Permission Assignment
    # ------------------------------------------------------------------

    async def list_agent_permissions(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> list[AgentPermission]:
        """List all direct permissions assigned to an agent within tenant scope."""
        # 1. IDOR check
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        if agent_res.scalar_one_or_none() is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        stmt = (
            select(AgentPermission)
            .options(selectinload(AgentPermission.permission))
            .where(
                AgentPermission.agent_id == agent_id,
                AgentPermission.tenant_id == tenant_id,
            )
            .order_by(AgentPermission.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def assign_permission_to_agent(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        permission_id: uuid.UUID,
    ) -> AgentPermission:
        """Assign a direct permission to an agent within tenant scope."""
        # 1. Verify agent exists in tenant
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        if agent_res.scalar_one_or_none() is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        # 2. Verify permission exists and is registered in canonical registry
        perm_stmt = select(Permission).where(Permission.id == permission_id)
        perm_res = await db.execute(perm_stmt)
        perm = perm_res.scalar_one_or_none()
        if perm is None or perm.name not in ALL_PERMISSIONS:
            raise AgentPermissionAssignmentError(
                f"Permission {permission_id} is invalid or not registered in canonical registry."
            )

        # 3. Check duplicate assignment
        dup_stmt = select(AgentPermission).where(
            AgentPermission.agent_id == agent_id,
            AgentPermission.permission_id == permission_id,
            AgentPermission.tenant_id == tenant_id,
        )
        dup_res = await db.execute(dup_stmt)
        if dup_res.scalar_one_or_none() is not None:
            raise AgentPermissionAlreadyAssignedError(
                f"Permission '{perm.name}' is already assigned to agent {agent_id}."
            )

        ap = AgentPermission(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            permission_id=permission_id,
        )
        db.add(ap)
        await db.flush()
        await db.refresh(ap, ["permission"])
        return ap

    async def revoke_permission_from_agent(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        permission_id: uuid.UUID,
    ) -> None:
        """Revoke a direct permission assignment from an agent."""
        # 1. Verify agent exists in tenant
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        if agent_res.scalar_one_or_none() is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        stmt = select(AgentPermission).where(
            AgentPermission.agent_id == agent_id,
            AgentPermission.permission_id == permission_id,
            AgentPermission.tenant_id == tenant_id,
        )
        res = await db.execute(stmt)
        ap = res.scalar_one_or_none()

        if ap is None:
            raise AgentPermissionNotFoundError(
                f"Permission assignment {permission_id} not found for agent {agent_id}."
            )

        await db.delete(ap)
        await db.flush()

    # ------------------------------------------------------------------
    # Phase 129 — Agent Role Assignment
    # ------------------------------------------------------------------

    async def list_agent_roles(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> list[AgentRole]:
        """List all roles assigned to an agent within tenant scope."""
        # 1. IDOR check
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        if agent_res.scalar_one_or_none() is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        stmt = (
            select(AgentRole)
            .options(selectinload(AgentRole.role))
            .where(
                AgentRole.agent_id == agent_id,
                AgentRole.tenant_id == tenant_id,
            )
            .order_by(AgentRole.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def assign_role_to_agent(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        role_id: uuid.UUID,
    ) -> AgentRole:
        """Assign a tenant-scoped or system role to an agent."""
        # 1. Verify agent exists in tenant
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        if agent_res.scalar_one_or_none() is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        # 2. Verify role exists in tenant or is system role
        role = await self.get_role(db, tenant_id, role_id)
        if role is None:
            raise AgentRoleAssignmentError(f"Role {role_id} not found or access denied.")

        # 3. Check duplicate assignment
        dup_stmt = select(AgentRole).where(
            AgentRole.agent_id == agent_id,
            AgentRole.role_id == role_id,
            AgentRole.tenant_id == tenant_id,
        )
        dup_res = await db.execute(dup_stmt)
        if dup_res.scalar_one_or_none() is not None:
            raise AgentRoleAlreadyAssignedError(
                f"Role '{role.name}' is already assigned to agent {agent_id}."
            )

        ar = AgentRole(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            role_id=role_id,
        )
        db.add(ar)
        await db.flush()
        await db.refresh(ar, ["role"])
        return ar

    async def remove_role_from_agent(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        role_id: uuid.UUID,
    ) -> None:
        """Remove a role assignment from an agent within tenant scope."""
        # 1. Verify agent exists in tenant
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        if agent_res.scalar_one_or_none() is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        stmt = select(AgentRole).where(
            AgentRole.agent_id == agent_id,
            AgentRole.role_id == role_id,
            AgentRole.tenant_id == tenant_id,
        )
        res = await db.execute(stmt)
        ar = res.scalar_one_or_none()

        if ar is None:
            raise AgentRoleNotFoundError(
                f"Role assignment {role_id} not found for agent {agent_id}."
            )

        await db.delete(ar)
        await db.flush()
