# API-ADR-002: Explicit URI Path Versioning (`/api/v1/...`)

## Context & Problem Statement
Modifying API payload contracts risks breaking existing mobile or client integrations.

## Decision
Enforce URI path versioning (`/api/v1/...`) across all public endpoints.

## Consequences & Trade-Offs
* **Benefits**: Guarantees zero breaking changes on existing version paths.
* **Trade-Offs**: Requires maintaining legacy major version routes when v2 launches.
