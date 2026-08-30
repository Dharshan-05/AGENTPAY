# PAY-ADR-010: Integer Minor Unit Financial Precision

## 1. Context & Problem Statement
Floating-point arithmetic introduces cumulative precision errors in financial calculations.

## 2. Decision
Represent monetary amounts strictly as 64-bit integer minor units in domain logic and PostgreSQL `NUMERIC(18,4)` in database tables.

## 3. Consequences & Trade-Offs
* **Benefits**: Zero floating-point rounding drift.
* **Trade-Offs**: Requires converting amounts to display units in UI.
