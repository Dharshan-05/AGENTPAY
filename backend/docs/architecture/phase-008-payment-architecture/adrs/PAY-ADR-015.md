# PAY-ADR-015: Dual Real-Time & Scheduled Reconciliation Architecture

## 1. Context & Problem Statement
Delayed or dropped webhooks can leave internal database state out of sync with Razorpay.

## 2. Decision
Deploy real-time webhook reconciliation plus a nightly batch reconciliation job (01:00 UTC) comparing 100% of gateway transactions.

## 3. Consequences & Trade-Offs
* **Benefits**: Detects missing or corrupted webhook signals automatically.
* **Trade-Offs**: Requires polling Razorpay settlement APIs nightly.
