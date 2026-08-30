# SentinelX — Security Model

## Core principle

Sensitive data never reaches an LLM. SentinelX inspects, classifies, scores, and either blocks, sanitizes, or flags every prompt before transmission — and records everything immutably.

## Defense layers

1. **Pattern detection** — 30+ deterministic rules (AWS keys, JWT, credit cards, PHI, PII, credentials).
2. **Policy enforcement** — GDPR, HIPAA, PCI DSS, SOC 2, ISO 27001 packs map entities to regulatory obligations.
3. **Risk scoring** — composite 0–100 score; thresholds: 80 critical, 50 high, 35 medium.
4. **Decision enforcement** — critical → hard block; high/medium → rewrite; low → flag.
5. **Audit logging** — every request is committed with a prompt hash, decision, risk, and full agent trace.
6. **Runtime guardrails** — gateway rate limiting (300 req/min), simulated MFA/SSO, TLS 1.3, AES-256 at rest.

## Explainability

Every decision must answer:

- **Why?** — the reasoning chain (risk contributions, threats).
- **How?** — the evaluation chain (inspect → detect → evaluate → score → decide → audit).
- **What rule?** — exact detection patterns and policy rule IDs that fired.
- **What confidence?** — per-agent confidence values in the trace.
- **Alternative outcome?** — what the decision would have been at lower risk bands.
- **Business impact?** — policy/compliance impact and recommended action.

## Data handling

- Prompt text is stored for audit (retention configurable: 90d / 365d / 2y / 10y).
- Sensitive matches are stored alongside their redaction for verification.
- No secrets or keys are ever written to the repository or logs.
- Demo mode runs fully in-memory — no external data leaves the process.

## Integrity

- Audit records are treated as tamper-evident: append-only in the store, keyed by prompt hash.
- Every incident view renders the original, sanitized, and rewritten prompt for side-by-side verification.

## Threat model coverage

- Accidental credential/PII leakage in prompts (primary).
- Regulated-data exposure (PHI, card data, HR records).
- Prompt-injection content embedded in scanned text.
- Rogue model routing (gateway controls provider per policy).

## Non-goals (explicit)

- This is a demonstration platform: the LLM gateway is simulated, and "intelligence" is rule-based for deterministic, repeatable demo behavior.
