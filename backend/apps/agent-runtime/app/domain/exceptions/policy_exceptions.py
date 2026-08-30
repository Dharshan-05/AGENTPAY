"""Domain exceptions for AGENTGUARD Policy Management & Evaluation (Phases 185–187)."""

from __future__ import annotations

from app.exceptions.base import AgentPayError


class PolicyError(AgentPayError):
    """Base exception for all Policy domain errors."""


class PolicyNotFoundError(PolicyError):
    """Raised when a requested policy does not exist within the tenant boundary."""


class PolicyAlreadyExistsError(PolicyError):
    """Raised when creating a policy with a duplicate name/slug within tenant."""


class PolicyValidationError(PolicyError):
    """Raised when policy configuration or state transition is invalid."""


class PolicyConflictError(PolicyError):
    """Raised when conflicting policy rules cannot be resolved."""
