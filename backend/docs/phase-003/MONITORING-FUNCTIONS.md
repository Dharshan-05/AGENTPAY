# AGENTPAY — Monitoring Functional Specifications

## 1. Overview

Monitoring functions specify real-time transaction telemetry streaming, velocity anomaly monitoring, security event tracking, and dashboard activity feed ingestion.

---

## 2. Specifications

### FR-MON-001: Real-time Transaction Telemetry Stream
* **FR ID**: `FR-MON-001`
* **Title**: Real-time Transaction Telemetry Aggregation & Activity Feed Stream
* **Source**: `REQ-MON-001`
* **Priority**: P0 | **MVP**: YES
* **Actor**: System Monitoring (`SYSTEM`)
* **Goal**: Aggregate intent evaluation metrics and stream live activity feeds to dashboard clients.
* **Preconditions**: Telemetry pipeline active.
* **Trigger**: Payment intent state transition or policy evaluation event.
* **Inputs**: Event payload (`intent_id`, `agent_id`, `amount`, `decision`, `risk_score`, `timestamp`).
* **Main Flow**:
  1. System publishes event payload to internal Redis Pub/Sub telemetry channel (`events:telemetry`).
  2. Telemetry service updates rolling 24-hour aggregate counters (Total Intents, Allowed Count, Blocked Count, Review Count, Total Spend).
  3. Telemetry service streams update to connected WebSocket clients.
* **Outputs**: WebSocket Live Activity Telemetry JSON stream.
* **Audit Events**: `EVENT_TELEMETRY_INGESTED`.
* **Acceptance Criteria**: `AC-MON-001`.
* **Dependencies**: None.
