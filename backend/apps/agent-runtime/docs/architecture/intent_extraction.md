# Phase 140 — Intent Extraction Architecture

## Purpose
Phase 140 implements the Intent Extraction layer (`IntentExtractionService`) for AGENTPAY, converting natural language or structured requests into candidate semantic intent representations (`StructuredIntent`).

## Architectural Invariants
- **Pluggable Provider Abstraction**: Provider interface (`BaseIntentExtractorProvider`) with deterministic rule/regex baseline (`RuleBasedIntentExtractorProvider`), pluggable with LLM extraction providers.
- **Representational Only**: MUST NOT execute payments, call tools, create plans, or persist intents.
- **Zero Secret Leakage**: Sanitizes passwords, API keys, and bearer tokens in request text.
- **Tenant Isolation**: Verified against authenticated tenant context (`AgentNotFoundError` 404).
