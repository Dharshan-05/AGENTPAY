# AGENTPAY — 10: Distributed Timestamp Architecture (`TIMESTAMPTZ` in UTC)

## 1. Timestamp Standard

1. **PostgreSQL Type**: All timestamp columns use `TIMESTAMPTZ` (Timestamp with Time Zone), stored internally in UTC.
2. **Mandatory Timestamps**: Every relational table contains `created_at TIMESTAMPTZ DEFAULT NOW()` and `updated_at TIMESTAMPTZ DEFAULT NOW()`.
3. **Domain Event Timestamps**: `authorized_at`, `initiated_at`, `completed_at`, `expires_at`.
