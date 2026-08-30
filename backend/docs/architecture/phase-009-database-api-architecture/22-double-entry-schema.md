# AGENTPAY — 22: Double-Entry Accounting Engine Invariants ($\sum \text{Debit} = \sum \text{Credit}$)

## 1. Mathematical Accounting Invariants

Every `ledger_transaction` posted to the database requires that the sum of debit entries equals the sum of credit entries:

$$\sum_{i=1}^n \text{debit}_i = \sum_{j=1}^m \text{credit}_j$$

```sql
CREATE OR REPLACE FUNCTION verify_ledger_transaction_balance() 
RETURNS TRIGGER AS $$
DECLARE
    total_debit NUMERIC(18,4);
    total_credit NUMERIC(18,4);
BEGIN
    SELECT COALESCE(SUM(debit), 0), COALESCE(SUM(credit), 0)
    INTO total_debit, total_credit
    FROM ledger_entries
    WHERE transaction_id = NEW.transaction_id;

    IF total_debit <> total_credit THEN
        RAISE EXCEPTION 'Ledger Transaction % Imbalance: Debits (%) != Credits (%)',
            NEW.transaction_id, total_debit, total_credit;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```
