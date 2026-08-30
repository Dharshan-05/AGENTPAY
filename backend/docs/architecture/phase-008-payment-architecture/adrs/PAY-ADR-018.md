# PAY-ADR-018: Interactive Human-in-the-Loop Escalation Cards

## 1. Context & Problem Statement
High-value or ambiguous transactions require human oversight without terminating task workflows.

## 2. Decision
Push interactive escalation cards to the Approval Center UI with 15-minute TTLs for transactions evaluated as `REVIEW`.

## 3. Consequences & Trade-Offs
* **Benefits**: Combines autonomous velocity with human control.
* **Trade-Offs**: Unapproved transactions expire after 15 minutes.
