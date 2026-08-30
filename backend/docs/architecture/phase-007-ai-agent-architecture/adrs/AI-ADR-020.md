# AI-ADR-020: Non-Negotiable Autonomous Payment Execution Boundary

## Context & Problem Statement
Direct interaction between an AI model and external payment provider APIs (Razorpay) creates unacceptable financial safety hazards.

## Decision
Enforce a non-negotiable architectural boundary: The LLM generates structured intent proposals only. Payment execution is strictly reserved for the Payment Orchestrator after passing deterministic AGENTGUARD authorization.

## Consequences & Trade-Offs
* **Benefits**: 100% protection against autonomous model financial execution bypasses.
* **Trade-Offs**: Requires multi-step intent proposal and authorization pipeline.
