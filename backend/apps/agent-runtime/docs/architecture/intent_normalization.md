# Phase 144 — Intent Normalization Architecture

## Purpose
Phase 144 introduces deterministic intent normalization (`IntentNormalizationService`) for AGENTPAY, mapping validated `StructuredIntent` instances into one canonical format.

## Normalization Rules
- **100% Determinism**: `normalize(intent) == normalize(intent)`. Zero randomness, zero network or LLM dependencies.
- **Action Mapping**: Maps variants (`pay`, `send money`, `transfer`) to canonical action identifiers (`payment`).
- **Currency Casing**: Upper-cases currency codes (`usd` -> `USD`, `inr` -> `INR`).
- **Text Casing & Whitespace**: Trims leading/trailing whitespace and lower-cases dictionary keys in parameters/constraints.
- **Decimal Precision**: Preserves exact `Decimal` representation without conversion to float.
- **No Semantic Inference**: MUST NOT guess or invent missing values.
