# MONO-ADR-013: Shared API Contracts Package (`@agentpay/api-contracts`)

## Context & Problem Statement
Preventing schema drift between backend REST API request validators and frontend form handlers.

## Decision
Publish shared Zod validation schemas for requests, responses, and errors in `@agentpay/api-contracts`.

## Consequences & Trade-Offs
* **Benefits**: Single source of truth for API validation across frontend and backend applications.
* **Trade-Offs**: Requires updating the package when API request structures evolve.
