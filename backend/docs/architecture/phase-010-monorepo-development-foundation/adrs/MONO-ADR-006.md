# MONO-ADR-006: Strict Package Dependency Hierarchy & Circular Dependency Ban

## Context & Problem Statement
Preventing circular imports between packages causing runtime initialization bugs.

## Decision
Enforce strict layered dependency direction: `apps` $\rightarrow$ `domain packages` $\rightarrow$ `primitive packages` (`types`/`config`). Prohibit circular dependencies.

## Consequences & Trade-Offs
* **Benefits**: Guarantees deterministic module load order.
* **Trade-Offs**: Requires refactoring shared models into lower-level packages.
