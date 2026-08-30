# SentinelX — The Story

## How SentinelX protects enterprises

Shadow AI is the data breach that doesn't make the news — until it does. A developer pastes a production credential into a chat box to debug a deploy. A sales rep pastes a customer list to draft an email. A nurse pastes a patient record to summarize a chart. One paste, one model, one leak. No firewall on earth was watching that conversation — because the conversation was the firewall's blind spot.

SentinelX changes that. It sits between the employee and the model — a **security gateway for AI traffic**. Every prompt is intercepted and run through an **8-agent pipeline**:

1. **Inspector Agent** normalizes and chunks the prompt.
2. **Secret Detection Agent** matches 42 patterns — AWS keys, JWTs, credit cards (Luhn-validated), credentials, PII, PHI, API keys.
3. **Policy Engine Agent** applies 7 packs: GDPR, HIPAA, PCI DSS, SOC 2, ISO 27001, Internal, Secrets.
4. **Risk Engine Agent** scores composite risk — SAFE, MEDIUM, HIGH, CRITICAL.
5. **Rewriter Agent** strips the sensitive content while preserving the employee's intent.
6. **LLM Adapter Agent** routes the safe prompt to the model (5 providers, or a simulation fallback).
7. **Audit Logger Agent** records an immutable, explainable trace.
8. **Memory Agent** keeps short- and long-term context so the system learns how the organization actually works.

The decision is `ALLOW`, `REWRITE`, `BLOCK`, or `FLAG` — made before the model ever sees the data.

## Why companies need it

- **Invisible risk.** DLP secures stored files; SentinelX secures the AI conversation — the fastest-growing data exfiltration channel that security teams cannot see.
- **Regulatory proof.** GDPR, HIPAA, PCI DSS, SOC 2 and ISO 27001 all demand demonstrable controls over regulated data. SentinelX produces the evidence: policy-trigger logs, rewrite records, and an audit trail.
- **Culture-safe.** Blocking AI creates shadow IT. SentinelX lets people use AI productively while the organization stays safe — governance instead of prohibition.

## How the AI agents collaborate

This is not a single classifier — it is a **team of specialists**. Each agent runs, reports its findings, and hands off to the next. Their work is visible live in Mission Control: agent by agent, confidence by confidence, duration by duration. When a credit card prompt arrives, Secret Detection finds the PAN, the Policy Engine cites PCI DSS, the Risk Engine scores it critical, and the Rewriter drops the card number — the employee still gets a travel plan, and no card number ever reaches the model. When the demo ends, the **AI Explainability Center** replays the reasoning: which agent found what, which policy fired, and the confidence of every decision.

Executives get a copilot that speaks their language — department risk, threat drivers, today vs. yesterday — grounded in the same telemetry, with memory of past conversations.

## How it saves millions

- **Breach avoidance.** The average cost of a data breach runs into the millions. SentinelX blocks the channel before the leak, not after.
- **Fine avoidance.** PCI DSS violations, HIPAA exposures, and GDPR processing violations carry direct regulatory penalties. Every blocked prompt is a fine not paid.
- **Productivity preservation.** Rewrites keep the work moving — employees aren't blocked from using AI, they are protected while using it.
- **Security efficiency.** One platform replaces a patchwork of point tools: detection, policy, risk, rewrite, audit, and reporting in a single command center.

**SentinelX: every prompt, every model, zero secrets leaking.**
