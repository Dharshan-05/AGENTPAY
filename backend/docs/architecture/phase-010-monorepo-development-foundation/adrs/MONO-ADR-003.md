# MONO-ADR-003: Monorepo Directory Organization Standard (`apps/` vs `packages/`)

## Context & Problem Statement
Preventing code duplication by separating runnable microservices from shared internal utility modules.

## Decision
Enforce top-level `/apps` for runnable services (`web`, `api`, `agent-runtime`, `agentguard`, `worker`) and `/packages` for shared domain modules.

## Consequences & Trade-Offs
* **Benefits**: Clear boundary between entrypoints and reusable libraries.
* **Trade-Offs**: Requires registering all shared modules in `pnpm-workspace.yaml`.
