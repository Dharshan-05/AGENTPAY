# API-ADR-006: Zod Ingress Payload Validation & Strict Field Sanitization

## Context & Problem Statement
Unvalidated JSON payloads risk mass-assignment security vulnerabilities and invalid data injection.

## Decision
Mandate Zod schema validation (`.strict()`) on 100% of API controllers, stripping unexpected body parameters.

## Consequences & Trade-Offs
* **Benefits**: Prevents parameter pollution and mass-assignment exploits.
* **Trade-Offs**: Requires defining strict Zod schemas for every endpoint.
