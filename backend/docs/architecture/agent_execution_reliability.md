# Agent Execution Reliability Architecture (Phase 163)

## Overview
The Execution Reliability layer guarantees safe retry classification, circuit breaker fault tolerance, and financial reconciliation in AGENTPAY.

## Retry Safety Taxonomy
- **`SAFE_TO_RETRY`**: Transient network timeouts / 503 rate limits on idempotent queries.
- **`NOT_SAFE_TO_RETRY`**: Non-idempotent financial operations, auth errors, validation failures. Financial operations are NEVER blindly retried!
- **`REQUIRES_RECONCILIATION`**: Ambiguous gateway status or timeout during a financial charge requiring manual/automated settlement reconciliation.

## Circuit Breakers
Tracks downstream dependency health. Trips `OPEN` upon reaching failure threshold to block cascading system failures.
