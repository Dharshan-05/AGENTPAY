# API-ADR-012: OpenAPI 3.0 Contract Governance & Automated Linting

## 1. Context & Problem Statement
Preventing undocumented endpoints or breaking API contract changes from deploying to production.

## 2. Decision
Mandate OpenAPI 3.0 specification files linted automatically via Spectral in CI/CD pipelines.

## 3. Consequences & Trade-Offs
* **Benefits**: 100% accurate API documentation matching production contracts.
* **Trade-Offs**: Developer must update `openapi.yaml` when modifying routes.
