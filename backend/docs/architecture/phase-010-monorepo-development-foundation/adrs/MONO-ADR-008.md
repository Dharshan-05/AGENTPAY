# MONO-ADR-008: Centralized Typed Configuration Architecture

## Context & Problem Statement
Scattering `process.env.VARIABLE` checks throughout application controllers risks silent runtime failures when variables are missing.

## Decision
Centralize environment variable parsing and Zod schema validation in `@agentpay/config`.

## Consequences & Trade-Offs
* **Benefits**: Guarantees application microservices fail fast at boot if required environment variables are invalid.
* **Trade-Offs**: Requires updating `@agentpay/config` when adding new environment variables.
