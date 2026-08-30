# AI-ADR-012: Hybrid AI Planning + Deterministic Rules Architecture

## Context & Problem Statement
Relying solely on probabilistic LLMs for security decisions is unsafe; relying solely on rigid code scripts lacks conversational flexibility.

## Decision
Combine probabilistic LLM reasoning for task decomposition and product discovery with deterministic TypeScript business rules and Python XGBoost ML for fraud risk scoring.

## Consequences & Trade-Offs
* **Benefits**: Combines conversational adaptability with sub-millisecond mathematical policy enforcement.
* **Trade-Offs**: Requires orchestrating hybrid microservice tiers.
