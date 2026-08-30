# AGENTPAY — 40: Zero-Downtime Expand/Contract Database Migration Pattern

## 1. Expand/Contract Execution Phases

```
[ Phase 1: Expand ]  ──> Add new column `amount_minor_units` as NULLABLE.
                             │
[ Phase 2: Dual-Write] ──> Application writes to BOTH old and new columns.
                             │
[ Phase 3: Backfill ] ──> Background worker populates historical NULL values.
                             │
[ Phase 4: Contract ] ──> Application switches read path; old column dropped.
```
