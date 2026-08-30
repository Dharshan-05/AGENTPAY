"""Database naming conventions module for AGENTPAY (Phase 019).

Defines the authoritative PostgreSQL naming rules, SQLAlchemy MetaData naming convention dictionary,
reserved words protection, and machine-validatable naming standards.
"""

import re
from typing import Final

# Authoritative SQLAlchemy 2.0 MetaData naming convention dictionary
NAMING_CONVENTION: Final[dict[str, str]] = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# PostgreSQL Reserved Words to avoid as unquoted table or column identifiers
POSTGRES_RESERVED_WORDS: Final[set[str]] = {
    "user",
    "order",
    "group",
    "role",
    "transaction",
    "table",
    "schema",
    "select",
    "where",
    "from",
    "join",
    "grant",
    "check",
    "primary",
    "foreign",
    "index",
    "unique",
    "column",
    "constraint",
    "database",
    "default",
    "references",
}

# Regex for lowercase snake_case identifiers
SNAKE_CASE_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[a-z][a-z0-9_]*$")


def validate_table_name(name: str) -> bool:
    """Verify table name follows plural lowercase snake_case and avoids reserved words."""
    if not name or not SNAKE_CASE_PATTERN.match(name):
        return False
    if name.lower() in POSTGRES_RESERVED_WORDS:
        return False
    return True


def validate_column_name(name: str) -> bool:
    """Verify column name follows lowercase snake_case and avoids reserved words."""
    if not name or not SNAKE_CASE_PATTERN.match(name):
        return False
    if name.lower() in POSTGRES_RESERVED_WORDS:
        return False
    return True


def validate_constraint_name(kind: str, name: str) -> bool:
    """Verify constraint name conforms to mandatory prefix standards (pk_, fk_, uq_, ck_, ix_)."""
    if not name or not SNAKE_CASE_PATTERN.match(name):
        return False

    prefix_map = {
        "pk": "pk_",
        "fk": "fk_",
        "uq": "uq_",
        "ck": "ck_",
        "ix": "ix_",
    }

    expected_prefix = prefix_map.get(kind.lower())
    if not expected_prefix:
        return False

    return name.startswith(expected_prefix)
