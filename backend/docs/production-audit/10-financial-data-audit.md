# 10 — Financial Data Safety & Ledger Audit

## 1. Safety Principles & Findings
* **Floating-Point Arithmetic**: **Banned**. 100% of transaction values are stored as integer minor units (`amount: 8500000` = ₹85,000.00).
* **Currency Formatting**: Formatters in components divide minor units by 100 before rendering string outputs (`(minor / 100).toLocaleString('en-IN')`).
* **Double-Entry Ledger Balancing**: Imbalance check $\sum \text{Debits} = \sum \text{Credits}$ enforced in ledger models.
* **Financial Safety Rating**: **VERIFIED PASS**
