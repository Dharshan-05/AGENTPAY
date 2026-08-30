# PAY-ADR-019: Server-Side Multi-Tier Payment Emergency Kill Switch

## 1. Context & Problem Statement
Security incidents require immediately stopping payment processing without server redeployments.

## 2. Decision
Deploy multi-tier (Global, Tenant, Agent, Merchant) emergency kill switches propagating via Redis in $< 100\text{ ms}$.

## 3. Consequences & Trade-Offs
* **Benefits**: Instant threat isolation and financial containment.
* **Trade-Offs**: Requires privileged admin authorization to trigger.
