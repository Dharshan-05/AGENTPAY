# MONO-ADR-005: Shared Package Scope Taxonomy (`@agentpay/<name>`)

## Context & Problem Statement
Preventing name collisions and ambiguous internal imports.

## Decision
Prefix all internal workspace packages with `@agentpay/` scope (e.g. `@agentpay/types`, `@agentpay/database`).

## Consequences & Trade-Offs
* **Benefits**: Standardizes package resolution across tsconfig paths and package.json manifests.
* **Trade-Offs**: Requires configuring NPM scope aliases in root build scripts.
