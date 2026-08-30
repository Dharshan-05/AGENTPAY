# DB-ADR-006: ISO 4217 Currency Code Standard & Exchange Conversion Rule

## Context & Problem Statement
Implicit currency conversions cause accounting loss and ambiguity in multi-currency settlements.

## Decision
Enforce ISO 4217 standard currency codes; require explicit `exchange_rate` records for multi-currency settlements.

## Consequences & Trade-Offs
* **Benefits**: Prevents unauthorized exchange rate drift.
* **Trade-Offs**: Requires validating currency codes on all orders and intents.
