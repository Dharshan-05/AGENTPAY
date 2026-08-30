"""Infrastructure layer exceptions package."""

from app.infrastructure.exceptions.base import (
    CacheError,
    DatabaseError,
    ExternalServiceError,
    InfrastructureError,
)

__all__ = [
    "InfrastructureError",
    "DatabaseError",
    "CacheError",
    "ExternalServiceError",
]
