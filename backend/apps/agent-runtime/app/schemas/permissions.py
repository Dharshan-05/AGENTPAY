"""AGENTPAY Permission Management API Schemas (Phase 113)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PermissionResponse(BaseModel):
    """Serialized permission for API responses."""

    id: uuid.UUID
    name: str
    resource: str
    action: str
    description: str | None = None
    is_system: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RolePermissionAssignRequest(BaseModel):
    """Request body for assigning a permission to a role."""

    permission_id: uuid.UUID = Field(..., description="Permission UUID to assign.")


class RolePermissionResponse(BaseModel):
    """Serialized role-permission assignment for API responses."""

    id: uuid.UUID
    role_id: uuid.UUID
    permission_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
