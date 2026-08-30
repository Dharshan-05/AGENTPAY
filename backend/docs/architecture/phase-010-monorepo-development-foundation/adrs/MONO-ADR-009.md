# MONO-ADR-009: Environment Tier Separation Strategy

## Context & Problem Statement
Preventing development configuration settings from leaking into staging or production deployments.

## Decision
Maintain explicit environment tier defaults: `.env.example` (Tracked template), `.env.local` (Local developer overrides, gitignored), `.env.test` (CI integration test container settings).

## Consequences & Trade-Offs
* **Benefits**: Prevents developer environment credentials from polluting production environments.
* **Trade-Offs**: Requires keeping `.env.example` synchronized with configuration changes.
