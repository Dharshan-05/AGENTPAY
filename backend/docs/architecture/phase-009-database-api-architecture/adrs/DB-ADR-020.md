# DB-ADR-020: Restricted Database Role Privileges & Zero Superuser App Access

## Context & Problem Statement
Connecting applications using database superuser roles risks severe SQL injection privilege escalation.

## Decision
Restrict application connection pools to `agentpay_app` roles lacking DDL schema privileges and prohibited from deleting ledger rows.

## Consequences & Trade-Offs
* **Benefits**: Defense-in-depth against SQL injection data destruction.
* **Trade-Offs**: Requires running migrations with a separate `agentpay_migrator` role.
