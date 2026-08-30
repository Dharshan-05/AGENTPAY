# Phase 142 — Structured Intent Schema Architecture

## Purpose
Phase 142 defines the canonical structured intent representation (`StructuredIntent`, `ExtractedEntities`, `StructuredIntentResponse`) in `app/schemas/agents.py`.

## Contract Specification
- **Strict Pydantic Validation**: All intent models enforce `extra="forbid"`.
- **Financial Precision**: Monetary amounts MUST use `Decimal` (binary floating-point floats strictly forbidden).
- **Explicit Currency**: Explicit currency code representation (e.g. `INR`, `USD`, `EUR`).
- **Server-Controlled Identifiers**: `agent_id` and `tenant_id` are server-populated from authenticated security context; client injection of security-sensitive context is strictly forbidden.
- **Contract Boundary**: Serves as the stable contract interface for future validation, normalization, storage, and planning phases.
