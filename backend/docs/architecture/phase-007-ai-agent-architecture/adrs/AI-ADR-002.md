# AI-ADR-002: Agent Principal Identity Separation from LLM Models

## Context & Problem Statement
Coupling an agent's security identity directly to an LLM provider or model name creates security risks and vendor lock-in.

## Decision
Decouple Agent Identity (`agent_id`) from LLM models. An agent is a persistent principal in PostgreSQL with assigned cryptographic keys and capability scopes, treating LLMs as interchangeable reasoning engines.

## Consequences & Trade-Offs
* **Benefits**: Swapping LLM models does not alter agent security policies or audit logs.
* **Trade-Offs**: Requires explicitly binding `agent_id` context to all model inference prompts.
