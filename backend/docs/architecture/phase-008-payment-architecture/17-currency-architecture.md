# AGENTPAY — 17: Currency Architecture, Validation & Multi-Currency Rules

## 1. Currency Validation Rules

* **Default Currency**: Indian Rupee (`INR`) ISO 4217 standard currency code.
* **Implicit Conversion Forbidden**: Automatic, hidden currency conversions are prohibited. Any multi-currency settlement requires an explicit, auditable exchange rate record.
* **Minor Unit Multipliers**: INR = 100 (paise), USD = 100 (cents), JPY = 1 (yen).
