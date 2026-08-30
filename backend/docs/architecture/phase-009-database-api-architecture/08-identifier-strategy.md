# AGENTPAY — 08: Identifier Strategy (UUID v4 / ULID vs Provider Identifiers)

## 1. Primary Identifier Standard

* **Internal Entities**: Primary keys use cryptographically secure 128-bit UUID v4 identifiers (or time-sortable ULID strings), formatted with domain prefix prefixes (e.g. `pay_7f8a9b0c-1d2e-3f4a`).
* **Provider Identifiers**: External IDs (e.g. Razorpay `pay_K123456789`) are stored in distinct indexed columns (`provider_payment_id`).
* **Enumeration Resistance**: Sequential integer IDs (`SERIAL`, `BIGSERIAL`) are strictly banned for public API entities to prevent enumeration attacks.
