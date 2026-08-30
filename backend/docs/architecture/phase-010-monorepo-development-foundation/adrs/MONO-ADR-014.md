# MONO-ADR-014: OpenAPI Specification Tooling & Spectral Governance

## Context & Problem Statement
Preventing undocumented API endpoints or broken OpenAPI specification contracts.

## Decision
Generate `openapi.json` automatically from `@agentpay/api-contracts` and enforce Spectral linting in CI.

## Consequences & Trade-Offs
* **Benefits**: Guarantees 100% accurate API documentation conforming to OpenAPI 3.0 standards.
* **Trade-Offs**: Requires running Spectral lint checks on every API pull request.
