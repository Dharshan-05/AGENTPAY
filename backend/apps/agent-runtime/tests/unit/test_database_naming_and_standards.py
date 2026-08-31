"""Unit tests for Phase 019 Database Naming Conventions & Phase 020 Database Schema Standards."""

import ast
from pathlib import Path

from app.infrastructure.database import (
    NAMING_CONVENTION,
    Base,
    metadata,
    validate_column_name,
    validate_constraint_name,
    validate_fk_delete_policy,
    validate_money_standard,
    validate_primary_key_standard,
    validate_table_name,
    validate_tenant_standard,
    validate_timestamp_standard,
)

# ============================================================================
# PHASE 019: DATABASE NAMING CONVENTIONS TESTS
# ============================================================================


def test_naming_convention_dictionary_structure() -> None:
    """Verify MetaData naming convention dictionary matches mandatory prefix standards."""
    assert metadata.naming_convention == NAMING_CONVENTION
    assert NAMING_CONVENTION["pk"] == "pk_%(table_name)s"
    assert NAMING_CONVENTION["fk"] == "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
    assert NAMING_CONVENTION["uq"] == "uq_%(table_name)s_%(column_0_N_name)s"
    assert NAMING_CONVENTION["ck"] == "ck_%(table_name)s_%(constraint_name)s"
    assert NAMING_CONVENTION["ix"] == "ix_%(table_name)s_%(column_0_N_name)s"


def test_table_name_validation_rules() -> None:
    """Verify table naming rules enforce lowercase snake_case and block reserved words."""
    assert validate_table_name("users") is True
    assert validate_table_name("user_profiles") is True
    assert validate_table_name("refresh_tokens") is True

    # Invalid names
    assert validate_table_name("Users") is False
    assert validate_table_name("user-profiles") is False
    assert validate_table_name("user") is False  # Reserved word
    assert validate_table_name("select") is False  # Reserved word


def test_column_name_validation_rules() -> None:
    """Verify column naming rules enforce lowercase snake_case and block reserved words."""
    assert validate_column_name("id") is True
    assert validate_column_name("tenant_id") is True
    assert validate_column_name("email_address") is True

    # Invalid names
    assert validate_column_name("userId") is False
    assert validate_column_name("created-at") is False
    assert validate_column_name("user") is False  # Reserved word


def test_constraint_prefix_validation_rules() -> None:
    """Verify constraint naming rules enforce mandatory pk_, fk_, uq_, ck_, ix_ prefixes."""
    assert validate_constraint_name("pk", "pk_users") is True
    assert validate_constraint_name("fk", "fk_user_roles_user_id_users") is True
    assert validate_constraint_name("uq", "uq_users_email") is True
    assert validate_constraint_name("ck", "ck_transactions_amount_positive") is True
    assert validate_constraint_name("ix", "ix_users_tenant_id") is True

    # Invalid prefixes
    assert validate_constraint_name("pk", "users_pk") is False
    assert validate_constraint_name("fk", "user_fk") is False


# ============================================================================
# PHASE 020: DATABASE SCHEMA STANDARDS TESTS
# ============================================================================


def test_primary_key_standard_validation() -> None:
    """Verify primary key standard requires 'id' column name and UUID type."""
    assert validate_primary_key_standard("id", "UUID") is True
    assert validate_primary_key_standard("id", "UUIDv7") is True
    assert validate_primary_key_standard("user_id", "UUID") is False
    assert validate_primary_key_standard("id", "BIGINT") is False


def test_tenant_standard_validation() -> None:
    """Verify tenant isolation standard requires 'tenant_id' UUID NOT NULL."""
    assert validate_tenant_standard("tenant_id", "UUID", nullable=False) is True
    assert validate_tenant_standard("tenant_id", "UUID", nullable=True) is False
    assert validate_tenant_standard("tenant", "UUID", nullable=False) is False


def test_timestamp_standard_validation() -> None:
    """Verify timestamp standard requires timezone-aware TIMESTAMPTZ."""
    assert validate_timestamp_standard("created_at", "TIMESTAMPTZ") is True
    assert validate_timestamp_standard("updated_at", "TIMESTAMP WITH TIME ZONE") is True
    assert validate_timestamp_standard("deleted_at", "TIMESTAMPTZ") is True

    # Invalid timestamp types
    assert validate_timestamp_standard("created_at", "TIMESTAMP WITHOUT TIME ZONE") is False
    assert validate_timestamp_standard("created_at", "VARCHAR") is False


def test_money_standard_validation() -> None:
    """Verify financial monetary standard requires NUMERIC/DECIMAL and rejects FLOAT/REAL."""
    assert validate_money_standard("NUMERIC(20, 8)") is True
    assert validate_money_standard("DECIMAL(18, 4)") is True
    assert validate_money_standard("FLOAT") is False
    assert validate_money_standard("REAL") is False


def test_fk_delete_policy_validation() -> None:
    """Verify foreign key delete policy enforces RESTRICT on financial/audit records."""
    assert validate_fk_delete_policy("RESTRICT", is_financial_or_audit=True) is True
    assert validate_fk_delete_policy("NO ACTION", is_financial_or_audit=True) is True
    assert validate_fk_delete_policy("CASCADE", is_financial_or_audit=True) is False


def test_all_application_tables_registered_in_metadata() -> None:
    """Verify all 53 expected application tables exist in Base.metadata (Scope Lock)."""
    expected = {
        "users",
        "user_profiles",
        "roles",
        "permissions",
        "role_permissions",
        "user_roles",
        "sessions",
        "refresh_tokens",
        "authentication_security",
        "login_security_events",
        "agents",
        "agent_identities",
        "agent_credentials",
        "agent_sessions",
        "agent_permissions",
        "agent_roles",
        "agent_lifecycle",
        "agent_metadata",
        "agent_trust",
        "agent_audit",
        "merchants",
        "products",
        "product_categories",
        "inventory",
        "inventory_events",
        "offers",
        "purchase_intents",
        "purchase_plans",
        "commerce_transactions",
        "commerce_events",
        "security_policies",
        "policy_rules",
        "policy_evaluations",
        "behaviour_events",
        "security_violations",
        "risk_signals",
        "fraud_predictions",
        "xai_explanations",
        "payment_orders",
        "payment_transactions",
        "payment_events",
        "razorpay_webhook_events",
        "refunds",
        "cancellations",
        "payment_idempotency_keys",
        "review_queue",
        "approval_requests",
        "approval_decisions",
        "reviewer_activity",
        "audit_logs",
        "security_events",
        "attack_simulations",
        "risk_decision_audits",
        "user_preferences",
        "agent_memories",
        "tool_definitions",
        "tool_execution_audits",
        "atim_execution_telemetry",
        "atim_model_versions",
        "atim_governance_decisions",
        "atim_cost_budgets",
        "atim_task_performance_stats",
        "atim_audit_signatures",
        "atim_threat_intel_logs",
        "atim_governance_policies",
        "atim_quota_usages",
        "atim_compliance_evidence",
        "atim_idempotency_records",
        "atim_transactional_outbox",
        "atim_workflow_instances",
        "atim_workflow_step_executions",
    }
    assert set(Base.metadata.tables.keys()) == expected


def test_migrations_in_versions_directory() -> None:
    """Verify all migration scripts exist in alembic/versions/ (Scope Lock)."""
    versions_dir = Path(__file__).parent.parent.parent / "alembic" / "versions"
    py_migrations = sorted([p.name for p in versions_dir.glob("*.py")])
    assert len(py_migrations) == 47


    assert py_migrations[0] == "001_identity_create_users_and_user_profiles.py"
    assert py_migrations[1] == "002_roles_and_permissions.py"
    assert py_migrations[2] == "003_rbac_role_permission_and_user_role.py"
    assert py_migrations[3] == "004_auth_sessions_and_refresh_tokens.py"
    assert py_migrations[4] == "005_authentication_security_and_login_events.py"
    assert py_migrations[5] == "006_agents_and_agent_identity.py"
    assert py_migrations[6] == "007_agent_credentials_and_sessions.py"
    assert py_migrations[7] == "008_agent_permissions_and_roles.py"
    assert py_migrations[8] == "009_agent_lifecycle_and_metadata.py"
    assert py_migrations[9] == "010_agent_trust_and_audit.py"
    assert py_migrations[10] == "011_merchants_and_products.py"
    assert py_migrations[11] == "012_product_categories_and_inventory.py"
    assert py_migrations[12] == "013_inventory_events_and_offers.py"
    assert py_migrations[13] == "014_purchase_intents_and_plans.py"
    assert py_migrations[14] == "015_commerce_transactions_and_events.py"
    assert py_migrations[15] == "016_security_policies_and_policy_rules.py"
    assert py_migrations[16] == "017_policy_evaluation_and_behaviour_events.py"
    assert py_migrations[17] == "018_security_violations_and_risk_signals.py"
    assert py_migrations[18] == "019_fraud_predictions.py"
    assert py_migrations[19] == "020_xai_explanations.py"
    assert py_migrations[20] == "021_payment_orders.py"
    assert py_migrations[21] == "022_payment_transactions.py"
    assert py_migrations[22] == "023_payment_events.py"
    assert py_migrations[23] == "024_razorpay_webhook_events.py"
    assert py_migrations[24] == "025_refunds.py"
    assert py_migrations[25] == "026_cancellations.py"
    assert py_migrations[26] == "027_payment_idempotency_keys.py"
    assert py_migrations[27] == "028_review_queue.py"
    assert py_migrations[28] == "029_approval_requests.py"
    assert py_migrations[29] == "030_approval_decisions.py"
    assert py_migrations[30] == "031_reviewer_activity.py"
    assert py_migrations[31] == "032_global_audit_logs.py"
    assert py_migrations[32] == "033_security_events.py"
    assert py_migrations[33] == "034_attack_simulations.py"
    assert py_migrations[34] == "035_risk_decision_audits.py"
    assert py_migrations[35] == "036_database_indexing_strategy.py"


def test_domain_layer_has_zero_infrastructure_database_imports() -> None:
    """Verify domain layer files contain zero infrastructure database imports."""
    domain_dir = Path(__file__).parent.parent.parent / "app" / "domain"
    if not domain_dir.exists():
        return

    py_files = [p for p in domain_dir.rglob("*.py") if p.is_file()]
    for py_file in py_files:
        content = py_file.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("app.infrastructure.database"), (
                        f"Forbidden import '{alias.name}' in {py_file.name}"
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert not node.module.startswith("app.infrastructure.database"), (
                        f"Forbidden import '{node.module}' in {py_file.name}"
                    )
