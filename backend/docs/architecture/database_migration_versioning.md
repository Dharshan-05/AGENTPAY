# AGENTPAY Database Migration Versioning Strategy (Phase 018)

## Executive Summary

This document specifies the migration versioning rules, revision naming conventions, revision graph integrity verification, downgrade policies, and immutability standards for **AGENTPAY** database schema migrations (`Phase 018`).

---

## 1. Revision Identification & Naming Rules

Every database migration script in `alembic/versions/` must conform to the standard naming template:

$$\text{file\_template} = \text{<revision>\_<slug>.py}$$

### Examples
- `001_identity_create_users_table.py`
- `002_agent_create_agents_table.py`

### Mandated Script Attributes
Every migration script must explicitly define:
- `revision: str`: Unique revision identifier string.
- `down_revision: Union[str, None]`: Parent revision identifier string (`None` for initial baseline).
- `def upgrade() -> None:`: Transactional schema upgrade logic.
- `def downgrade() -> None:`: Reversible schema downgrade logic.

---

## 2. Linear Revision Graph & Single-Head Invariant

To guarantee deterministic database schema state across deployments:
1. **Single-Head Invariant**: The migration revision graph must remain strictly linear with exactly **one** head.
2. **Branching Prohibition**: Unintended split heads (multiple migration heads) are prohibited.
3. **CI Graph Verification**: CI pipelines execute `verify_migration_graph()` (`app/infrastructure/database/migration.py`) to validate graph linearity before deployment.

---

## 3. Migration Immutability Policy

- **Applied Revisions are Immutable**: Once a migration revision has been applied to any shared environment (`staging` or `production`), editing the revision file is strictly prohibited.
- **Correct Rollforward Procedure**: To modify or undo a schema change, create a **new** revision script using `alembic revision -m "description"`.

---

## 4. Reversibility & Downgrade Guarantees

Every migration script must include a fully tested `downgrade()` implementation:
- If a migration contains non-reversible data operations (e.g. dropping a column with historical transaction data), the `downgrade()` handler must raise an explicit exception describing why the operation is irreversible rather than failing silently.
