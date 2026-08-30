# AI-ADR-004: Multi-Provider LLM Abstraction Layer

## Context & Problem Statement
Relying on a single LLM vendor exposes the system to outages and price inflation.

## Decision
Implement an abstract `ILLMProvider` interface supporting OpenAI, Anthropic, and local self-hosted models with automatic sub-5s failover.

## Consequences & Trade-Offs
* **Benefits**: High availability and zero vendor lock-in.
* **Trade-Offs**: Output formatting must enforce standardized Pydantic JSON schemas.
