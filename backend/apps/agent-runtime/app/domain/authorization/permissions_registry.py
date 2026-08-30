"""AGENTPAY Permission Registry — Canonical permission name constants (Phase 111).

Permission names follow the convention: resource:action
All permissions are defined here as typed string constants.
No client-supplied permission strings are ever trusted.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Identity & User Management
# ---------------------------------------------------------------------------
USERS_READ = "users:read"
USERS_CREATE = "users:create"
USERS_UPDATE = "users:update"
USERS_DELETE = "users:delete"
USERS_PROFILE_UPDATE = "users:profile_update"
USERS_PREFERENCES_READ = "users:preferences_read"
USERS_PREFERENCES_UPDATE = "users:preferences_update"


# ---------------------------------------------------------------------------
# Role Administration
# ---------------------------------------------------------------------------
ROLES_READ = "roles:read"
ROLES_CREATE = "roles:create"
ROLES_UPDATE = "roles:update"
ROLES_ASSIGN = "roles:assign"
ROLES_REVOKE = "roles:revoke"

# ---------------------------------------------------------------------------
# Permission Administration
# ---------------------------------------------------------------------------
PERMISSIONS_READ = "permissions:read"
PERMISSIONS_ASSIGN = "permissions:assign"
PERMISSIONS_REVOKE = "permissions:revoke"

# ---------------------------------------------------------------------------
# Payment Operations
# ---------------------------------------------------------------------------
PAYMENTS_READ = "payments:read"
PAYMENTS_CREATE = "payments:create"
PAYMENTS_UPDATE = "payments:update"
PAYMENTS_REFUND = "payments:refund"
PAYMENTS_CANCEL = "payments:cancel"

# ---------------------------------------------------------------------------
# Payment Transactions
# ---------------------------------------------------------------------------
TRANSACTIONS_READ = "transactions:read"

# ---------------------------------------------------------------------------
# Review Queue
# ---------------------------------------------------------------------------
REVIEWS_READ = "reviews:read"
REVIEWS_APPROVE = "reviews:approve"
REVIEWS_REJECT = "reviews:reject"

# ---------------------------------------------------------------------------
# Audit & Compliance
# ---------------------------------------------------------------------------
AUDIT_LOGS_READ = "audit_logs:read"

# ---------------------------------------------------------------------------
# Security Monitoring
# ---------------------------------------------------------------------------
SECURITY_EVENTS_READ = "security_events:read"

# ---------------------------------------------------------------------------
# Agent Management
# ---------------------------------------------------------------------------
AGENTS_READ = "agents:read"
AGENTS_CREATE = "agents:create"
AGENTS_UPDATE = "agents:update"
AGENTS_DELETE = "agents:delete"
AGENTS_EXECUTE = "agents:execute"
AGENTS_ACTIVATE = "agents:activate"
AGENTS_SUSPEND = "agents:suspend"
AGENTS_REVOKE = "agents:revoke"
AGENTS_CREDENTIAL_CREATE = "agents:credential_create"
AGENTS_CREDENTIAL_READ = "agents:credential_read"
AGENTS_SESSIONS_READ = "agents:sessions_read"
AGENTS_SESSIONS_CREATE = "agents:sessions_create"
AGENTS_SESSIONS_REVOKE = "agents:sessions_revoke"
AGENTS_PERMISSIONS_READ = "agents:permissions_read"
AGENTS_PERMISSIONS_ASSIGN = "agents:permissions_assign"
AGENTS_PERMISSIONS_REVOKE = "agents:permissions_revoke"
AGENTS_ROLES_READ = "agents:roles_read"
AGENTS_ROLES_ASSIGN = "agents:roles_assign"
AGENTS_ROLES_REVOKE = "agents:roles_revoke"
AGENTS_STATUS_READ = "agents:status_read"
AGENTS_STATUS_UPDATE = "agents:status_update"
AGENTS_PAUSE = "agents:pause"
AGENTS_RESUME = "agents:resume"
AGENTS_METADATA_READ = "agents:metadata_read"
AGENTS_METADATA_UPDATE = "agents:metadata_update"
AGENTS_AUDIT_READ = "agents:audit_read"
AGENTS_SECURITY_EVENTS_READ = "agents:security_events_read"
AGENTS_TRUST_READ = "agents:trust_read"
AGENTS_TRUST_UPDATE = "agents:trust_update"
AGENTS_BEHAVIOUR_READ = "agents:behaviour_read"
AGENTS_VELOCITY_READ = "agents:velocity_read"
AGENTS_MERCHANT_BEHAVIOUR_READ = "agents:merchant_behaviour_read"
AGENTS_CATEGORY_BEHAVIOUR_READ = "agents:category_behaviour_read"
AGENTS_INTENT_VALIDATE = "agents:intent_validate"
AGENTS_INTENT_NORMALIZE = "agents:intent_normalize"
AGENTS_INTENT_CREATE = "agents:intent_create"
AGENTS_INTENT_READ = "agents:intent_read"
AGENTS_PLANS_CREATE = "agents:plans_create"
AGENTS_PLANS_READ = "agents:plans_read"
AGENTS_PLANS_VALIDATE = "agents:plans_validate"
AGENTS_ORCHESTRATE = "agents:orchestrate"
AGENTS_ORCHESTRATION_READ = "agents:orchestration_read"
AGENTS_STATE_READ = "agents:state_read"
AGENTS_STATE_UPDATE = "agents:state_update"
AGENTS_EXECUTE = "agents:execute"
AGENTS_EXECUTION_READ = "agents:execution_read"
AGENTS_EXECUTION_CANCEL = "agents:execution_cancel"
AGENTS_CONTEXT_READ = "agents:context_read"
AGENTS_CONTEXT_ASSEMBLE = "agents:context_assemble"
AGENTS_MEMORY_READ = "agents:memory_read"
AGENTS_MEMORY_WRITE = "agents:memory_write"
AGENTS_MEMORY_DELETE = "agents:memory_delete"
AGENTS_TRANSACTION_ORCHESTRATE = "agents:transaction_orchestrate"
AGENTS_APPROVAL_REQUEST = "agents:approval_request"
AGENTS_APPROVAL_DECIDE = "agents:approval_decide"
AGENTS_RELIABILITY_READ = "agents:reliability_read"
AGENTS_RELIABILITY_RECOVER = "agents:reliability_recover"
AGENTS_IDENTITY_VERIFY = "agents:identity_verify"
AGENTS_AUTHORIZATION_CHECK = "agents:authorization_check"
AGENTS_PERMISSIONS_EVALUATE = "agents:permissions_evaluate"

# ---------------------------------------------------------------------------
# Policy Management & Evaluation (Phases 185–187)
# ---------------------------------------------------------------------------
POLICIES_READ = "policies:read"
POLICIES_CREATE = "policies:create"
POLICIES_UPDATE = "policies:update"
POLICIES_ACTIVATE = "policies:activate"
POLICIES_DEACTIVATE = "policies:deactivate"
POLICIES_ARCHIVE = "policies:archive"
POLICIES_EVALUATE = "policies:evaluate"

# ---------------------------------------------------------------------------
# Tool Management & Calling Framework (Phase 156/157)
# ---------------------------------------------------------------------------
TOOLS_READ = "tools:read"
TOOLS_REGISTER = "tools:register"
TOOLS_UPDATE = "tools:update"
TOOLS_ENABLE = "tools:enable"
TOOLS_DISABLE = "tools:disable"
TOOLS_EXECUTE = "tools:execute"

# ---------------------------------------------------------------------------
# Merchant Management
# ---------------------------------------------------------------------------
MERCHANTS_READ = "merchants:read"
MERCHANTS_CREATE = "merchants:create"
MERCHANTS_UPDATE = "merchants:update"
MERCHANTS_SUSPEND = "merchants:suspend"
MERCHANTS_ARCHIVE = "merchants:archive"

# ---------------------------------------------------------------------------
# Product Management (Phase 164)
# ---------------------------------------------------------------------------
PRODUCTS_READ = "products:read"
PRODUCTS_CREATE = "products:create"
PRODUCTS_UPDATE = "products:update"
PRODUCTS_ARCHIVE = "products:archive"

# ---------------------------------------------------------------------------
# FraudGuard ML & Risk Intelligence (Phases 261-265)
# ---------------------------------------------------------------------------
FRAUDGUARD_INFER = "fraudguard:infer"
FRAUDGUARD_RISK_READ = "fraudguard:risk_read"
FRAUDGUARD_XAI_READ = "fraudguard:xai_read"
FRAUDGUARD_EVALUATE = "fraudguard:evaluate"

# ---------------------------------------------------------------------------
# Risk & Decision Engine (Phases 283-284)
# ---------------------------------------------------------------------------
RISK_DECISIONS_EVALUATE = "risk_decisions:evaluate"
RISK_DECISIONS_READ = "risk_decisions:read"

# ---------------------------------------------------------------------------
# ALL_PERMISSIONS: complete canonical registry
# ---------------------------------------------------------------------------
ALL_PERMISSIONS: frozenset[str] = frozenset(
    {
        USERS_READ,
        USERS_CREATE,
        USERS_UPDATE,
        USERS_DELETE,
        USERS_PROFILE_UPDATE,
        USERS_PREFERENCES_READ,
        USERS_PREFERENCES_UPDATE,
        ROLES_READ,
        ROLES_CREATE,
        ROLES_UPDATE,
        ROLES_ASSIGN,
        ROLES_REVOKE,
        PERMISSIONS_READ,
        PERMISSIONS_ASSIGN,
        PERMISSIONS_REVOKE,
        PAYMENTS_READ,
        PAYMENTS_CREATE,
        PAYMENTS_UPDATE,
        PAYMENTS_REFUND,
        PAYMENTS_CANCEL,
        TRANSACTIONS_READ,
        REVIEWS_READ,
        REVIEWS_APPROVE,
        REVIEWS_REJECT,
        AUDIT_LOGS_READ,
        SECURITY_EVENTS_READ,
        AGENTS_READ,
        AGENTS_CREATE,
        AGENTS_UPDATE,
        AGENTS_DELETE,
        AGENTS_EXECUTE,
        AGENTS_ACTIVATE,
        AGENTS_SUSPEND,
        AGENTS_REVOKE,
        AGENTS_CREDENTIAL_CREATE,
        AGENTS_CREDENTIAL_READ,
        AGENTS_SESSIONS_READ,
        AGENTS_SESSIONS_CREATE,
        AGENTS_SESSIONS_REVOKE,
        AGENTS_PERMISSIONS_READ,
        AGENTS_PERMISSIONS_ASSIGN,
        AGENTS_PERMISSIONS_REVOKE,
        AGENTS_ROLES_READ,
        AGENTS_ROLES_ASSIGN,
        AGENTS_ROLES_REVOKE,
        AGENTS_STATUS_READ,
        AGENTS_STATUS_UPDATE,
        AGENTS_PAUSE,
        AGENTS_RESUME,
        AGENTS_METADATA_READ,
        AGENTS_METADATA_UPDATE,
        AGENTS_AUDIT_READ,
        AGENTS_SECURITY_EVENTS_READ,
        AGENTS_TRUST_READ,
        AGENTS_TRUST_UPDATE,
        AGENTS_BEHAVIOUR_READ,
        AGENTS_VELOCITY_READ,
        AGENTS_MERCHANT_BEHAVIOUR_READ,
        AGENTS_CATEGORY_BEHAVIOUR_READ,
        AGENTS_INTENT_VALIDATE,
        AGENTS_INTENT_NORMALIZE,
        AGENTS_INTENT_CREATE,
        AGENTS_INTENT_READ,
        AGENTS_PLANS_CREATE,
        AGENTS_PLANS_READ,
        AGENTS_PLANS_VALIDATE,
        AGENTS_ORCHESTRATE,
        AGENTS_ORCHESTRATION_READ,
        AGENTS_STATE_READ,
        AGENTS_STATE_UPDATE,
        AGENTS_EXECUTION_READ,
        AGENTS_EXECUTION_CANCEL,
        AGENTS_CONTEXT_READ,
        AGENTS_CONTEXT_ASSEMBLE,
        AGENTS_MEMORY_READ,
        AGENTS_MEMORY_WRITE,
        AGENTS_MEMORY_DELETE,
        AGENTS_TRANSACTION_ORCHESTRATE,
        AGENTS_APPROVAL_REQUEST,
        AGENTS_APPROVAL_DECIDE,
        AGENTS_RELIABILITY_READ,
        AGENTS_RELIABILITY_RECOVER,
        AGENTS_IDENTITY_VERIFY,
        AGENTS_AUTHORIZATION_CHECK,
        AGENTS_PERMISSIONS_EVALUATE,
        POLICIES_READ,
        POLICIES_CREATE,
        POLICIES_UPDATE,
        POLICIES_ACTIVATE,
        POLICIES_DEACTIVATE,
        POLICIES_ARCHIVE,
        POLICIES_EVALUATE,
        TOOLS_READ,
        TOOLS_REGISTER,
        TOOLS_UPDATE,
        TOOLS_ENABLE,
        TOOLS_DISABLE,
        TOOLS_EXECUTE,
        MERCHANTS_READ,
        MERCHANTS_CREATE,
        MERCHANTS_UPDATE,
        MERCHANTS_SUSPEND,
        MERCHANTS_ARCHIVE,
        PRODUCTS_READ,
        PRODUCTS_CREATE,
        PRODUCTS_UPDATE,
        PRODUCTS_ARCHIVE,
        FRAUDGUARD_INFER,
        FRAUDGUARD_RISK_READ,
        FRAUDGUARD_XAI_READ,
        FRAUDGUARD_EVALUATE,
        RISK_DECISIONS_EVALUATE,
        RISK_DECISIONS_READ,
    }
)


def is_valid_permission(name: str) -> bool:
    """Return True if name is a registered canonical permission."""
    return name in ALL_PERMISSIONS
