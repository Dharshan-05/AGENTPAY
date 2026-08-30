# MONO-ADR-019: Autonomous Agent Microservice Boundary (`apps/agent-runtime`)

## 1. Context & Problem Statement
Isolating non-deterministic AI LLM reasoning loops from deterministic financial payment processing APIs.

## 2. Decision
House autonomous agent reasoning loops, prompt templates, and tool handlers inside a separate `apps/agent-runtime` service.

## 3. Consequences & Trade-Offs
* **Benefits**: Prevents LLM framework memory usage or CPU spikes from affecting payment gateway throughput.
* **Trade-Offs**: Requires HTTP REST communication between API gateway and agent runtime.
