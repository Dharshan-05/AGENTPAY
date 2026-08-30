# AI-ADR-005: Task-Based Dynamic Model Router

## Context & Problem Statement
Using large reasoning models for simple classification wastes token budgets and increases API latency.

## Decision
Deploy a dynamic Model Router that assigns lightweight models to simple tasks, reasoning models to complex planning, and deterministic Python/XGBoost services to policy and risk scoring.

## Consequences & Trade-Offs
* **Benefits**: Optimizes token costs and sub-100ms internal latency budgets.
* **Trade-Offs**: Requires task classification logic at ingress.
