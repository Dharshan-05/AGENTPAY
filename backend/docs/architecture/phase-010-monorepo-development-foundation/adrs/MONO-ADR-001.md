# MONO-ADR-001: Selection of PNPM Workspaces for Monorepo Package Management

## Context & Problem Statement
Managing multiple applications and shared packages requires strict dependency hoisting control and fast installation speeds.

## Decision
Adopt PNPM Workspaces (`pnpm-workspace.yaml`) as the primary monorepo package manager.

## Consequences & Trade-Offs
* **Benefits**: Hardened symlinking prevents phantom dependencies; sub-second install caching.
* **Trade-Offs**: Requires developers to have `pnpm` installed globally.
