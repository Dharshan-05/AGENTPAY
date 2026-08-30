"""SQLAlchemy DeclarativeBase module for AGENTPAY (Phase 019 + Phase 020).

Provides DeclarativeBase configured with deterministic MetaData naming conventions.
"""

from datetime import datetime

from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase

from app.infrastructure.database.naming import NAMING_CONVENTION

# Shared MetaData instance configured with mandatory naming conventions
metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Base(DeclarativeBase):
    """Canonical application DeclarativeBase subclass with naming conventions applied."""

    metadata = metadata
    type_annotation_map = {
        datetime: DateTime(timezone=True),
    }
