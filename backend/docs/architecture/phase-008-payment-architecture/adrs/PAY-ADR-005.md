# PAY-ADR-005: Cryptographic Payment Authorization Context Tokens

## Context & Problem Statement
Payment execution requires proof of policy approval without persisting mutable permission flags.

## Decision
Issue a short-lived (15m), single-use HMAC-signed `PaymentAuthorizationContext` token upon passing AGENTGUARD policy checks.

## Consequences & Trade-Offs
* **Benefits**: Cryptographically binds approved amount, agent ID, and merchant ID.
* **Trade-Offs**: Requires token validation and single-use eviction logic in Redis.
