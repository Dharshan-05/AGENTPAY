"""Correlation ID and Context propagation module for ATIM (Phase 13 / Group 7)."""

import contextvars
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

_correlation_context_var: contextvars.ContextVar[Optional["CorrelationContext"]] = (
    contextvars.ContextVar("correlation_context", default=None)
)


@dataclass
class CorrelationContext:
    """Correlation ID and tracing context container."""

    correlation_id: str = field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:16]}")
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    tenant_id: Optional[uuid.UUID] = None
    agent_id: Optional[uuid.UUID] = None
    model_id: Optional[str] = None
    provider: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


def set_correlation_context(ctx: CorrelationContext) -> contextvars.Token[Optional[CorrelationContext]]:
    """Set current async context correlation context."""
    return _correlation_context_var.set(ctx)


def get_correlation_context() -> CorrelationContext:
    """Retrieve or create current async correlation context."""
    ctx = _correlation_context_var.get()
    if ctx is None:
        ctx = CorrelationContext()
        _correlation_context_var.set(ctx)
    return ctx


def clear_correlation_context(token: Optional[contextvars.Token[Optional[CorrelationContext]]] = None) -> None:
    """Reset current correlation context."""
    if token:
        _correlation_context_var.reset(token)
    else:
        _correlation_context_var.set(None)
