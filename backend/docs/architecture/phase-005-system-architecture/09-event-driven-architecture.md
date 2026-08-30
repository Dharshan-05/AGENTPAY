# AGENTPAY — 09: Asynchronous Event Bus & Worker Architecture

## 1. Event Broker Architecture

AGENTPAY handles heavy background tasks (audit archiving, notification dispatch, webhook reconciliation, telemetry indexing) asynchronously via Redis Pub/Sub channels and worker queues.

```mermaid
graph TD
    subgraph Event Producers
        P1[API Gateway Endpoint]
        P2[AGENTGUARD Policy Engine]
        P3[Payment Orchestrator]
        P4[Razorpay Webhook Listener]
    end

    subgraph Event Broker (Redis Pub/Sub & Worker Queues)
        TOPIC_INTENTS[Topic: events:intents]
        TOPIC_ALERTS[Topic: events:alerts]
        TOPIC_WEBHOOKS[Topic: events:webhooks]
        QUEUE_DLQ[Queue: dead_letter_queue]
    end

    subgraph Event Consumers / Workers
        W_AUDIT[Audit Archiver Worker]
        W_NOTIFY[Push Notification Worker]
        W_RECONCILE[Razorpay Reconciliation Worker]
        W_METRICS[Prometheus Metrics Worker]
    end

    P1 & P2 & P3 --> TOPIC_INTENTS
    P2 & P3 --> TOPIC_ALERTS
    P4 --> TOPIC_WEBHOOKS

    TOPIC_INTENTS --> W_AUDIT & W_METRICS
    TOPIC_ALERTS --> W_NOTIFY
    TOPIC_WEBHOOKS --> W_RECONCILE

    W_NOTIFY & W_RECONCILE -->|On 3 Failed Retries| QUEUE_DLQ
```

---

## 2. Dead-Letter Queue (DLQ) & Retry Policy

* **Retry Policy**: Failed background worker tasks retry up to 3 times using exponential backoff with full jitter ($1\text{s}, 2\text{s}, 4\text{s}$).
* **DLQ Routing**: After 3 failed attempts, poison-pill tasks are moved to `dead_letter_queue` table and trigger an immediate operational alert to security operators.
