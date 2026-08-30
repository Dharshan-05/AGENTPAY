# AI-ADR-018: Fail-Closed Security Control Outage Fallback

## Context & Problem Statement
Microservice outages in Python risk containers or external LLM APIs must not jeopardize financial security.

## Decision
Enforce a Fail-Closed strategy: if LLM or risk scoring microservices fail, the system defaults to static deterministic rules and assigns `MEDIUM_RISK`, escalating to human review. The system NEVER defaults to `ALLOW`.

## Consequences & Trade-Offs
* **Benefits**: Guarantees zero payment leakage during component outages.
* **Trade-Offs**: May cause temporary execution delays during upstream provider outages.
