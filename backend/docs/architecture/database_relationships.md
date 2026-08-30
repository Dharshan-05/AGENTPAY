# AGENTPAY Database Relationships Architecture (Phase 059)

## Executive Summary

This document formalizes the database relationship topology across all **38 application tables** in **AGENTPAY** (`Phase 059`).

---

## 1. Domain Relationship Graph

```
identity (users, user_profiles, roles, permissions, role_permissions, user_roles, sessions, refresh_tokens, auth_sec, login_events)
  ↓
agents / merchants (agents, agent_identities, agent_credentials, agent_sessions, agent_permissions, agent_roles, agent_lifecycle, agent_metadata, agent_trust, agent_audit, merchants)
  ↓
products / inventory / offers (products, product_categories, inventory, inventory_events, offers)
  ↓
purchase_intents → purchase_plans → commerce_transactions → commerce_events
  ↓
security_policies → policy_rules → policy_evaluations → behaviour_events
  ↓
security_violations → risk_signals → fraud_predictions → xai_explanations
```

---

## 2. Integrity & Deletion Rules

1. **Foreign Key Deletion Policy**: All foreign key relationships across the 38 application tables strictly use `ON DELETE RESTRICT`. `CASCADE` and `SET NULL` are prohibited on relational links.
2. **Tenant Isolation**: Foreign key references across entities require strict tenant matching (`entity_a.tenant_id == entity_b.tenant_id`).
3. **Index Enforcement**: Every foreign key column in the database is covered by an index (`ix_<table>_<fk_column>`).
4. **ORM Mapping**: Every relationship is paired with explicit `back_populates` or explicit uni-directional relationships.
