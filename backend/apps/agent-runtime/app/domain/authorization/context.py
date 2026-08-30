"""AGENTPAY RBAC Authorization Context (Phase 111).

AuthorizationContext is an immutable value object carrying the complete
principal context required to make an authorization decision.

It is constructed once per request from the authenticated principal and
passed to AuthorizationService for evaluation. It MUST NOT be mutated
or reconstructed from client-supplied data.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class AuthorizationContext:
    """Immutable authorization context for a single authenticated request.

    Attributes:
        user_id:    The authenticated user's UUID (from verified JWT/session).
        tenant_id:  The tenant scope bound to this request (from verified JWT/session).
        session_id: The active session UUID (from verified JWT/session).
    """

    user_id: uuid.UUID
    tenant_id: uuid.UUID
    session_id: uuid.UUID

    def __post_init__(self) -> None:
        """Validate that no field is a zero-value UUID."""
        if self.user_id == uuid.UUID(int=0):
            raise ValueError("AuthorizationContext: user_id must not be zero UUID.")
        if self.tenant_id == uuid.UUID(int=0):
            raise ValueError("AuthorizationContext: tenant_id must not be zero UUID.")
        if self.session_id == uuid.UUID(int=0):
            raise ValueError("AuthorizationContext: session_id must not be zero UUID.")

    def __repr__(self) -> str:
        """Safe developer representation — no secrets emitted."""
        return f"<AuthorizationContext user_id={self.user_id} tenant_id={self.tenant_id}>"
