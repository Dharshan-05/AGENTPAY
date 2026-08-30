# AGENTPAY — 11: Financial Precision Model (Integer Minor Units / `NUMERIC(18,4)`)

## 1. Storage & Precision Standard

* **API & Service Memory**: Represented strictly as 64-bit integer minor units (e.g. ₹100.50 = `10050` paise).
* **Relational Database**: Stored using PostgreSQL `NUMERIC(18,4)` column type, allowing up to 14 integer digits and 4 decimal places with exact mathematical precision.
* **Floating-Point Ban**: `FLOAT`, `DOUBLE PRECISION`, and `REAL` types are strictly prohibited in financial schemas.
