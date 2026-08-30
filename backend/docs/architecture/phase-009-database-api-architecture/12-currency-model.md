# AGENTPAY — 12: ISO 4217 Currency Validation & Settlement Precision Rules

## 1. Currency Validation Rules

* **ISO 4217 Compliance**: Standard 3-character uppercase string (e.g. `INR`, `USD`, `EUR`).
* **Default Currency**: Indian Rupee (`INR`).
* **Post-Authorization Immutability**: Currency code cannot be updated once a `PaymentAuthorization` token is issued.
* **Implicit Conversion Banned**: Multi-currency transactions mandate explicit exchange rate records (`exchange_rate NUMERIC(12,6)`).
