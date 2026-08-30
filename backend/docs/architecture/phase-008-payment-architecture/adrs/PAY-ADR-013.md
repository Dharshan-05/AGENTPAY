# PAY-ADR-013: Cumulative Partial Refund Tracking & Over-Refund Guard

## 1. Context & Problem Statement
Multiple partial refunds risk exceeding original payment amounts if unconstrained.

## 2. Decision
Track cumulative settled and pending refunds, rejecting requests where requested amount exceeds remaining refundable balance.

## 3. Consequences & Trade-Offs
* **Benefits**: 100% protection against over-refunding.
* **Trade-Offs**: Requires transactional calculation of refundable balance.
