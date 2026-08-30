# SEC-ADR-007: Webhook Signature Verification & Idempotency

## Context & Problem Statement
External payment providers dispatch webhook callbacks to confirm transaction settlements.

## Threat Analysis
Fake webhook payloads could trick the system into updating transaction states to `RECONCILED` without actual settlement.

## Decision
Mandate HMAC-SHA256 signature verification (`X-Razorpay-Signature`) using constant-time string comparison, combined with Razorpay Event ID idempotency deduplication.

## Consequences & Trade-Offs
* **Benefits**: Prevents webhook forgery and duplicate event processing.
* **Trade-Offs**: Requires maintaining Razorpay webhook signing secrets in Vault.
