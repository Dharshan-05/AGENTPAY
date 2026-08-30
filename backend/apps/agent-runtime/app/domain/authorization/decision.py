"""AGENTPAY RBAC Authorization Decision (Phase 111).

AuthorizationDecision is an immutable value object representing the outcome
of an authorization evaluation.

All authorization decisions are:
- Deterministic
- Fail-closed (default deny)
- Explicit allow
- Never implicit
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthorizationDecision:
    """Immutable result of an authorization check.

    Attributes:
        allowed:    True if access is granted. False is the default (fail-closed).
        reason:     Human-readable rationale (never surfaced externally).
        permission: The permission that was evaluated.
    """

    allowed: bool
    reason: str
    permission: str

    @classmethod
    def allow(cls, permission: str, reason: str = "Permission granted.") -> AuthorizationDecision:
        """Construct an explicit allow decision."""
        return cls(allowed=True, reason=reason, permission=permission)

    @classmethod
    def deny(cls, permission: str, reason: str = "Permission denied.") -> AuthorizationDecision:
        """Construct an explicit deny decision (default)."""
        return cls(allowed=False, reason=reason, permission=permission)

    def __repr__(self) -> str:
        """Safe developer representation."""
        return f"<AuthorizationDecision allowed={self.allowed} permission='{self.permission}'>"
