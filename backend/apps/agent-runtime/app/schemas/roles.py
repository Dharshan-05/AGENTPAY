"""AGENTPAY Role Management API Schemas (Phase 112)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class RoleResponse(BaseModel):
    """Serialized role for API responses."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: str | None = None
    is_system: bool
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RoleCreateRequest(BaseModel):
    """Request body for creating a new role."""

    tenant_id: uuid.UUID = Field(..., description="Tenant scope for the new role.")
    name: str = Field(
        ..., min_length=1, max_length=100, description="Unique role name within tenant."
    )
    description: str | None = Field(None, max_length=500)


class RoleUpdateRequest(BaseModel):
    """Request body for updating an existing role."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    status: str | None = Field(None, pattern="^(active|inactive)$")


class UserRoleAssignRequest(BaseModel):
    """Request body for assigning a role to a user."""

    role_id: uuid.UUID = Field(..., description="Role UUID to assign.")


class UserRoleResponse(BaseModel):
    """Serialized user-role assignment for API responses."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    role_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
