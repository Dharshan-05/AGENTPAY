# SentinelX — AI Agent Reference

All agents implement a common contract: `run(input) → { output }` and `toTrace() → AgentTraceEntry`.

## AgentTraceEntry shape

```ts
interface AgentTraceEntry {
  agent: string;            // agent id
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED" | "SKIPPED";
  confidence: number;       // 0..1
  executionTimeMs: number;
  startedAt: string;        // ISO timestamp
  error?: string;
}
```

## 1. Inspector Agent (`agents/inspector.ts`)

- **Role**: classifies prompt intent and data sensitivity.
- **Signals**: prompt length, structured-data heuristics, sensitivity keyword scan.
- **Output**: `{ intent, sensitivity, riskMultiplier }`.
- **Trace**: baseline confidence ~0.9; drives the pipeline's initial risk weighting.

## 2. Secret Detection Agent (`agents/secret-detection.ts`)

- **Role**: deterministic pattern matching over the raw prompt.
- **Rules**: 30+ patterns — AWS access keys, Google API keys, MongoDB URIs, JWTs, credit cards (Luhn + CVV), phone numbers, emails, SSN/Aadhaar, IPs, etc.
- **Output**: `DetectedSecret[]` with match, redaction, position, severity, confidence.
- **Trace**: confidence = average of matched rule confidences.

## 3. Policy Engine (`agents/policy-engine.ts`)

- **Role**: map detected entities to regulation packs.
- **Packs**: GDPR (PII), HIPAA (PHI), PCI DSS (card data), SOC 2 (credentials/infra), ISO 27001 (code/secrets).
- **Output**: `PolicyViolation[]` — policy, regulation, category, severity, rule id, reason, recommendation.
- **Trace**: confidence reflects rule-match strength.

## 4. Risk Engine (`agents/risk-engine.ts`)

- **Role**: composite 0–100 risk score from secrets, violations, inspector sensitivity, and threat level.
- **Output**: `{ score, threatLevel }` (`SAFE/LOW/MEDIUM/HIGH/CRITICAL`).
- **Trace**: confidence ~0.95; score drives the decision matrix.

## 5. Prompt Rewriter (`agents/rewriter.ts`)

- **Role**: intent-preserving sanitisation — replace each match with a redaction token.
- **Output**: `{ changed, rewritten }`.
- **Trace**: confidence reflects coverage of detected entities.

## 6. LLM Adapter (`agents/llm-adapter.ts`)

- **Role**: simulated multi-provider gateway (OpenAI / Gemini / Claude / Ollama / OpenRouter).
- **Behaviour**: SKIPPED when the decision is BLOCK; otherwise returns a canned provider response + latency.
- **Trace**: latency models real provider behaviour.

## 7. Audit Logger (`agents/audit-logger.ts`)

- **Role**: commits a tamper-evident record to the audit store (pipeline id, prompt hash, decision, risk, secrets, violations, trace).
- **Output**: `{ id }` audit log id.
- **Trace**: confidence 1.0.

## 8. Memory Agent (`agents/memory.ts`)

- **Role**: stores session/behavioural context keyed by user; used for future risk weighting.
- **Trace**: confidence 1.0.

## Decision matrix (`agents/pipeline.ts`)

| Condition | Decision |
|---|---|
| Threat CRITICAL or any CRITICAL secret | **BLOCK** |
| HIGH threat with ≥2 violations | **BLOCK** |
| HIGH or MEDIUM threat | **REWRITE** |
| LOW threat | **FLAG** |
| Otherwise | **ALLOW** |
