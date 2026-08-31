# ATIM Phase 13 — Observability & Telemetry Sanitization Policy

## 1. Core Observability Rules
- **Non-Authoritative Telemetry**: Observability layers observe and record pipeline state. Telemetry **MUST NEVER** authorize financial transactions or override security decisions.
- **Fail Closed Sanitization**: If sanitization fails or encounters an unhandled exception, telemetry falls back to `[REDACTED_PAYLOAD_UNSANITIZED]` or omits the payload.

---

## 2. Redaction & PII Rules
| Data Category | Target Fields | Replacement Token |
|---|---|---|
| Authorization | Bearer Tokens, JWTs, API Keys, Private Keys | `[REDACTED_SECRET]` |
| Payment Secrets | Credit Card Number, CVV, UPI PIN, Bank Secrets | `[REDACTED_PAYMENT_SECRET]` |
| Financial PII | Account Number, PAN, Government ID, Email | `[REDACTED_PII]` |

---

## 3. Label Cardinality Rules
- High-cardinality values (**user prompt text, transaction IDs, free-form error messages, user IDs**) are **STRICTLY PROHIBITED** as Prometheus metric labels.
- Allowed metric labels: `provider`, `model`, `task_type`, `risk_level`, `status`, `error_category`.
