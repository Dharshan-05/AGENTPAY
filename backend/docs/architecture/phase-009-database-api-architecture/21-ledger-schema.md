# AGENTPAY — 21: `ledger_accounts`, `ledger_transactions`, `ledger_entries`

## 1. Accounting Ledger DDL

```sql
CREATE TABLE ledger_accounts (
    account_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(tenant_id),
    name VARCHAR(128) NOT NULL,
    type VARCHAR(32) NOT NULL, -- 'ASSET', 'LIABILITY', 'EQUITY', 'EXPENSE', 'REVENUE'
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE ledger_transactions (
    transaction_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(tenant_id),
    reference_type VARCHAR(32) NOT NULL, -- 'PAYMENT', 'REFUND'
    reference_id VARCHAR(64) NOT NULL,
    description TEXT NOT NULL,
    posted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE ledger_entries (
    entry_id VARCHAR(64) PRIMARY KEY,
    transaction_id VARCHAR(64) NOT NULL REFERENCES ledger_transactions(transaction_id),
    account_id VARCHAR(64) NOT NULL REFERENCES ledger_accounts(account_id),
    debit NUMERIC(18,4) NOT NULL DEFAULT 0 CHECK (debit >= 0),
    credit NUMERIC(18,4) NOT NULL DEFAULT 0 CHECK (credit >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_ledger_debit_credit_mutually_exclusive CHECK (
        (debit > 0 AND credit = 0) OR (debit = 0 AND credit > 0)
    )
);
```
