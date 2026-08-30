# PAY-ADR-011: Strict Currency Validation & Ban on Implicit Conversions

## 1. Context & Problem Statement
Implicit currency conversions lead to exchange rate loss and accounting discrepancies.

## 2. Decision
Enforce ISO 4217 currency validation; ban implicit currency conversion. Multi-currency transactions require explicit rate records.

## 3. Consequences & Trade-Offs
* **Benefits**: Prevents unauthorized currency exchange losses.
* **Trade-Offs**: Requires validating currency code matching at ingress.
