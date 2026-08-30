# AI-ADR-009: Centralized Tool Registry & Schema Validation

## Context & Problem Statement
Exposing arbitrary functions to AI models introduces remote code execution and parameter tampering risks.

## Decision
Register all callable tools in a centralized Tool Registry with strict Zod JSON Schema validation for both inputs and outputs.

## Consequences & Trade-Offs
* **Benefits**: Rejects malformed arguments before execution.
* **Trade-Offs**: Requires registering schemas for every tool.
