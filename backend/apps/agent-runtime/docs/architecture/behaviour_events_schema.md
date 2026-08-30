# AGENTPAY Behaviour Events Schema Architecture (Phase 054)

## Executive Summary

This document formalizes the architectural specification and schema layout for `behaviour_events` in **AGENTPAY** (`Phase 054`).

`behaviour_events` represents an append-only behavioral/audit signal generated during agentic commerce activity.

---

## 1. Schema Specifications (`behaviour_events`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_behaviour_events)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_behaviour_events_tenant_id)` | Multi-tenancy isolation key |
| `event_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_behaviour_events_tenant_id_event_reference)` | Tenant-scoped event reference |
| `event_type` | `VARCHAR(50)` | `NOT NULL` | `CHECK (event_type IN ('agent', 'authentication', 'authorization', 'policy', 'commerce', 'purchase', 'inventory', 'merchant', 'product', 'offer', 'transaction', 'system'))`, `INDEX (ix_behaviour_events_event_type)` | Event type classification |
| `event_action` | `VARCHAR(50)` | `NOT NULL` | `CHECK (event_action IN ('created', 'requested', 'approved', 'rejected', 'executed', 'completed', 'failed', 'cancelled', 'viewed', 'selected', 'initiated', 'updated', 'deleted', 'evaluated'))`, `INDEX (ix_behaviour_events_event_action)` | Specific action taken |
| `event_result` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'success'`, `CHECK (event_result IN ('success', 'failure', 'pending', 'skipped'))`, `INDEX (ix_behaviour_events_event_result)` | Result classification |
| `agent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_behaviour_events_agent_id_agents) REFERENCES agents(id) ON DELETE RESTRICT`, `INDEX (ix_behaviour_events_agent_id)` | Foreign key referencing agents |
| `merchant_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_behaviour_events_merchant_id_merchants) REFERENCES merchants(id) ON DELETE RESTRICT`, `INDEX (ix_behaviour_events_merchant_id)` | Foreign key referencing merchants |
| `product_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_behaviour_events_product_id_products) REFERENCES products(id) ON DELETE RESTRICT`, `INDEX (ix_behaviour_events_product_id)` | Foreign key referencing products |
| `offer_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_behaviour_events_offer_id_offers) REFERENCES offers(id) ON DELETE RESTRICT`, `INDEX (ix_behaviour_events_offer_id)` | Foreign key referencing offers |
| `purchase_intent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_behaviour_events_purchase_intent_id_purchase_intents) REFERENCES purchase_intents(id) ON DELETE RESTRICT`, `INDEX (ix_behaviour_events_purchase_intent_id)` | Foreign key referencing purchase_intents |
| `purchase_plan_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_behaviour_events_purchase_plan_id_purchase_plans) REFERENCES purchase_plans(id) ON DELETE RESTRICT`, `INDEX (ix_behaviour_events_purchase_plan_id)` | Foreign key referencing purchase_plans |
| `commerce_transaction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_behaviour_events_commerce_transaction_id_commerce_transactions) REFERENCES commerce_transactions(id) ON DELETE RESTRICT`, `INDEX (ix_behaviour_events_commerce_transaction_id)` | Foreign key referencing commerce_transactions |
| `policy_evaluation_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_behaviour_events_policy_evaluation_id_policy_evaluations) REFERENCES policy_evaluations(id) ON DELETE RESTRICT`, `INDEX (ix_behaviour_events_policy_evaluation_id)` | Foreign key referencing policy_evaluations |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_behaviour_events_request_id)` | Correlation request ID |
| `actor_type` | `VARCHAR(100)` | `NULLABLE` | — | Actor type (agent, user, system, merchant) |
| `actor_id` | `UUID` | `NULLABLE` | — | Actor UUID |
| `sequence_number` | `BIGINT` | `NOT NULL` | `CHECK (sequence_number >= 0)`, `UNIQUE (uq_behaviour_events_tenant_id_sequence_number)` | Tenant-scoped sequence number |
| `event_payload` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Non-secret event payload |
| `occurred_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_behaviour_events_occurred_at)` | Occurrence timestamp (UTC) |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |

---

## 2. Append-Only & Integrity Rules

- **Append-Only Structure**: `behaviour_events` includes `occurred_at` and `created_at`. `updated_at` and `deleted_at` are strictly prohibited.
- **Tenant Isolation**: `behaviour_event.tenant_id == merchant.tenant_id == agent.tenant_id`.
- **Foreign Key Protection**: `ON DELETE RESTRICT` prevents deletion of parent entities while event logs exist.
- **Zero Secrets**: Plaintext passwords, tokens, API keys, card numbers, or private keys MUST NOT be stored in `event_payload` or exposed in `__repr__`.
