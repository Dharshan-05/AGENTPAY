# AGENTPAY — 16: Financial Precision (PostgreSQL `NUMERIC` / Minor Units)

## 1. Zero Floating-Point Rule

IEEE 754 floating-point arithmetic (e.g. `0.1 + 0.2 = 0.30000000000000004`) is strictly forbidden for financial calculations.

* **API & Domain Layers**: Amounts are represented as 64-bit integer minor units (e.g. ₹2,500.50 = `250050` paise).
* **Database Layer**: Amounts are stored using PostgreSQL `NUMERIC(18,4)` for exact 4-decimal precision.
