# AI-ADR-003: LangGraph State Machine Graph Orchestration

## Context & Problem Statement
Agent execution loops require deterministic state transitions, step counters, and checkpoint persistence to prevent infinite loops.

## Decision
Use LangGraph to model agent task execution as a deterministic state machine graph with explicit state checkpoints and hard loop boundaries (`max_steps = 10`).

## Consequences & Trade-Offs
* **Benefits**: Prevents infinite loops and enables task state restoration during model failover.
* **Trade-Offs**: Requires defining graph nodes and edge conditions in TypeScript code.
