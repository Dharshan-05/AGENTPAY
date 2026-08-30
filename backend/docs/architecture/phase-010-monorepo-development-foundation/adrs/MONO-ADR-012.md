# MONO-ADR-012: Migration Tooling Workflows (`pnpm db:migrate`)

## Context & Problem Statement
Standardizing database schema migration commands across local development and production CI/CD pipelines.

## Decision
Provide root monorepo scripts (`pnpm db:migrate`, `pnpm db:migrate:status`, `pnpm db:seed`).

## Consequences & Trade-Offs
* **Benefits**: Simplifies developer onboarding and guarantees consistent migration execution order.
* **Trade-Offs**: Requires database container to be healthy before executing scripts.
