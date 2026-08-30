# API-ADR-011: Razorpay HMAC-SHA256 Webhook Verification Pipeline

## 1. Context & Problem Statement
Preventing unauthenticated third parties from forging Razorpay payment success webhooks.

## 2. Decision
Verify Razorpay HMAC-SHA256 signatures synchronously before queuing event payloads.

## 3. Consequences & Trade-Offs
* **Benefits**: Blocks fake webhook injection attacks.
* **Trade-Offs**: Requires keeping webhook secret keys secure in HashiCorp Vault.
