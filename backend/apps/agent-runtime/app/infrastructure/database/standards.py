"""Database schema standards module for AGENTPAY (Phase 020).

Defines machine-validatable schema standards for primary keys (UUIDv7), tenant isolation,
timestamps (TIMESTAMPTZ UTC), financial precision (NUMERIC), and FK delete policies.
"""

from typing import Final

# Canonical Primary Key Column Name & Type Standard
PRIMARY_KEY_COLUMN_NAME: Final[str] = "id"
PRIMARY_KEY_TYPE_STANDARD: Final[str] = "UUID"

# Multi-Tenancy Tenant Identifier Standard
TENANT_COLUMN_NAME: Final[str] = "tenant_id"
TENANT_TYPE_STANDARD: Final[str] = "UUID"

# Approved Timestamps
TIMESTAMPTZ_STANDARD: Final[set[str]] = {
    "TIMESTAMPTZ",
    "TIMESTAMP WITH TIME ZONE",
    "TIMESTAMP(6) WITH TIME ZONE",
    "DATETIME(TIMEZONE=TRUE)",
}


def validate_primary_key_standard(column_name: str, type_str: str) -> bool:
    """Verify primary key column uses canonical 'id' name and UUID type."""
    if column_name != PRIMARY_KEY_COLUMN_NAME:
        return False
    return type_str.upper().startswith(PRIMARY_KEY_TYPE_STANDARD)


def validate_tenant_standard(column_name: str, type_str: str, nullable: bool) -> bool:
    """Verify multi-tenancy column uses 'tenant_id' name, UUID type, and NOT NULL constraint."""
    if column_name != TENANT_COLUMN_NAME:
        return False
    if nullable:
        return False
    return type_str.upper().startswith(TENANT_TYPE_STANDARD)


def validate_timestamp_standard(column_name: str, type_str: str) -> bool:
    """Verify timestamp columns use timezone-aware TIMESTAMPTZ."""
    if column_name not in {"created_at", "updated_at", "deleted_at"}:
        return False
    return type_str.upper() in TIMESTAMPTZ_STANDARD


def validate_money_standard(type_str: str) -> bool:
    """Verify financial monetary columns use exact NUMERIC or DECIMAL types."""
    type_upper = type_str.upper()
    if type_upper.startswith(("FLOAT", "REAL", "DOUBLE")):
        return False
    return type_upper.startswith(("NUMERIC", "DECIMAL"))


def validate_fk_delete_policy(policy_str: str, is_financial_or_audit: bool = False) -> bool:
    """Verify foreign key delete policies enforce RESTRICT/NO ACTION for critical records."""
    policy_upper = policy_str.upper().strip()
    if is_financial_or_audit:
        return policy_upper in {"RESTRICT", "NO ACTION"}
    return policy_upper in {"RESTRICT", "NO ACTION", "CASCADE", "SET NULL"}
