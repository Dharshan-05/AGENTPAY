# PAY-ADR-020: Fail-Closed Provider Outage & State Recovery Protocol

## 1. Context & Problem Statement
Gateway timeouts or 5xx provider outages must not result in duplicate retry payments.

## 2. Decision
Enforce fail-closed circuit breaking; transition unresponded transactions to `PAYMENT_STATUS_UNKNOWN`, requiring state verification before retry.

## 3. Consequences & Trade-Offs
* **Benefits**: Prevents double-charge scenarios during provider outages.
* **Trade-Offs**: Requires background verification jobs.
