# PAY-ADR-012: Webhook Signature Verification & Deduplication

## 1. Context & Problem Statement
Unauthenticated webhooks can inject fake payment success signals.

## 2. Decision
Verify Razorpay HMAC-SHA256 signatures synchronously; enforce 7-day event ID deduplication in Redis.

## 3. Consequences & Trade-Offs
* **Benefits**: Blocks forged webhooks and replay attacks.
* **Trade-Offs**: Requires maintaining provider webhook secrets.
