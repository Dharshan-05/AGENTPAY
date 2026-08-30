# API-ADR-016: Untrusted AI Agent Request Pipeline Isolation

## 1. Context & Problem Statement
Preventing malicious prompt injection payloads or hallucinated agent JSON from overriding server security policies.

## 2. Decision
Treat all AI agent API payloads as untrusted input; route through Zod validation, AGENTGUARD policy engine, and FRAUDGUARD ML risk evaluation before domain execution.

## Consequences & Trade-Offs
* **Benefits**: 100% protection against autonomous model policy bypasses.
* **Trade-Offs**: Requires multi-step request evaluation pipeline.
