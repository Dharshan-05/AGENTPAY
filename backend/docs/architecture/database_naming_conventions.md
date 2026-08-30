# AGENTPAY Database Naming Conventions Architecture (Phase 019)

## Executive Summary

This document formalizes the authoritative PostgreSQL naming conventions for the **AGENTPAY** platform (`Phase 019`).

All database identifiers (tables, columns, primary keys, foreign keys, constraints, indexes, enums) must strictly follow predictable, lowercase `snake_case` patterns compatible with SQLAlchemy 2.0 and Alembic.

---

## 1. Naming Philosophy & Rules

- **Format**: All database object identifiers MUST use lowercase `snake_case`.
- **Prohibited Patterns**: CamelCase, PascalCase, mixedCase, hyphens, spaces, quoted identifiers (`"Users"`), and unapproved abbreviations.
- **Reserved Words Protection**: PostgreSQL reserved words (`user`, `order`, `group`, `role`, `transaction`, `table`, `select`) MUST NOT be used as unquoted table or column names.

---

## 2. Identifier Naming Matrix

| Object Category | Rule / Format | Example (GOOD) | Counter-Example (BAD) |
| :--- | :--- | :--- | :--- |
| **Tables** | Plural `snake_case` | `users`, `refresh_tokens` | `User`, `user-tokens`, `tbl_users` |
| **Columns** | Lowercase `snake_case` | `id`, `email_address`, `created_at` | `userId`, `CreatedAt`, `created-date` |
| **Primary Keys** | `id` (UUIDv7) | `id` | `user_id`, `uid`, `pk_id` |
| **Foreign Keys** | `<referenced_entity>_id` | `user_id`, `role_id`, `agent_id` | `user_fk`, `fk_user`, `userId` |
| **PK Constraints** | `pk_<table>` | `pk_users`, `pk_agents` | `users_pk`, `PRIMARY` |
| **FK Constraints** | `fk_<table>_<col>_<ref_table>` | `fk_user_roles_user_id_users` | `user_roles_fk1` |
| **Unique Constraints** | `uq_<table>_<col_or_cols>` | `uq_users_email_address` | `unique_email` |
| **Check Constraints** | `ck_<table>_<meaningful_rule>` | `ck_transactions_amount_positive` | `check_1` |
| **Indexes** | `ix_<table>_<col_or_cols>` | `ix_users_tenant_id` | `idx_tenant` |
| **Enums** | Lowercase `snake_case` | `agent_status`, `user_status` | `UserStatus`, `USER_STATUS` |

---

## 3. SQLAlchemy 2.0 MetaData Integration

In `app.infrastructure.database.naming`, MetaData naming conventions are configured:

```python
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
```
