# SentinelX — Pitch Deck (10 Slides)

> Source for the presentation. Each slide includes a **title**, **speaker notes**, and **visual suggestions**. Export to PowerPoint/Canva in Phase 14. Use `docs/DEMO_SCRIPT.md` for the live-demo beats.

---

## Slide 1 — The Problem: Shadow AI

**Title:** Every company is leaking data to AI — and nobody can see it

**Speaker notes:**
- Employees paste credentials, source code, customer PII, and patient records into public AI chat tools daily.
- Security teams have no visibility at the AI boundary: no detection, no policy, no audit.
- Blocking AI doesn't work — it creates shadow IT.

**Visual:** Split screen — left: employee pasting into a chat box; right: dark "no visibility" void. A single red highlight over the paste button.

---

## Slide 2 — The Market

**Title:** Every company that uses AI is a customer

**Speaker notes:**
- AI adoption in the enterprise is at an all-time high; governance spend follows within 12–24 months.
- Regulators (GDPR, HIPAA, PCI DSS, SOC 2, ISO 27001) now require demonstrable controls over data flowing to AI.
- Breach costs average millions; one leaked credential or patient record can mean fines and headlines.

**Visual:** 3 stat cards: "AI adoption ↑", "Regulated data → AI ↑", "Breach cost $M". Keep numbers as ranges, not fake precision.

---

## Slide 3 — The Solution

**Title:** SentinelX — an AI governance firewall

**Speaker notes:**
- SentinelX sits between employees and every LLM: a security gateway for AI traffic.
- It intercepts every prompt, detects secrets/PII/PHI, enforces policy, scores risk, and blocks, rewrites, or allows before the model ever sees the data.
- Executives finally get a number: sensitive data kept out of third-party AI.

**Visual:** Diagram: Employee → SentinelX gateway → LLM. Arrow labeled "ALLOW / REWRITE / BLOCK".

---

## Slide 4 — Architecture

**Title:** Monorepo, zero external dependencies

**Speaker notes:**
- Fastify 5 API + Next.js 16 dashboard, TypeScript strict throughout.
- PostgreSQL/Prisma in production; zero-config in-memory demo mode for judging.
- Real-time Socket.io telemetry (agent updates, presence, live cursors).

**Visual:** Two-box diagram (API / Web) with data layer icons; a "works with zero config" badge.

---

## Slide 5 — The AI Pipeline

**Title:** 8 agents, one decision

**Speaker notes:**
- Inspector normalizes the prompt → Secret Detection (42 rules, Luhn-validated cards) → Policy Engine (7 packs) → Risk Engine scores → Rewriter sanitizes → LLM adapter routes → Audit Logger records → Memory learns.
- Every decision is explainable: which agent, which policy, which evidence.

**Visual:** Horizontal 8-node pipeline graphic with ALLOW/REWRITE/BLOCK output. Live version: `/scanner` replay.

---

## Slide 6 — Live Demo

**Title:** Judge Mode — one click

**Speaker notes:**
- Run the 6-attack sequence live (AWS key → JWT → HR → credit card → source → patient).
- Watch detection, scoring, rewriting, explanation, and the auto-generated protection report.
- Voice narration carries the story.

**Visual:** Live demo. Fallback slide: screenshot of Judge Mode with the 6 scenario chips.

---

## Slide 7 — Security Model

**Title:** Explainable, auditable, role-controlled

**Speaker notes:**
- AI Explainability Center: decision graph, agent contributions, reasoning timeline, confidence.
- Immutable audit trail, 7 RBAC roles, credential redaction in logs, secrets never stored.
- Incident Response Center with resolution workflows and related-prompt linking.

**Visual:** Three cards: Explain / Audit / RBAC. Screenshots from `/explain`, `/audit`, `/settings`.

---

## Slide 8 — Business Model

**Title:** Per-seat SaaS with enterprise add-ons

**Speaker notes:**
- Per-seat licensing per protected employee; premium packs for compliance evidence and advanced rules.
- Deployment options: cloud gateway, on-prem, or bring-your-own LLM.
- Natural expansion: guardrails-as-code, browser extension, agent-to-agent governance.

**Visual:** Pricing card mockup (3 tiers) — clearly labeled "proposed model".

---

## Slide 9 — The Future

**Title:** Governance is the next firewall

**Speaker notes:**
- Guardrails-as-code: policies in Git, PR-reviewed.
- On-device detection: local embeddings, nothing leaves the laptop.
- Agent-to-agent guardrails: govern AI systems talking to AI systems.
- Marketplace for community rules and policy packs.

**Visual:** 4 future tiles with icons + timeline arrow.

---

## Slide 10 — Closing

**Title:** Every prompt. Every model. Zero secrets leaking.

**Speaker notes:**
- 8 agents · 42 detection rules · 7 policy packs · full command center — running with zero config.
- Judge-ready from a fresh checkout: no API keys, no database, no internet.
- "We govern the prompt before the model ever sees it."
- Thank you — happy to demo more or walk the architecture.

**Visual:** Final hero shot (Executive Command Center) + tagline. Contact/team line if applicable.

---

## Deck production tips (Phase 14)

- Export slides to PowerPoint/Canva using the visual suggestions; keep the dark theme (#09090B) and teal accent (#0B827A) consistent with the app.
- Use the README hero screenshot for Slide 1 and 10 backgrounds.
- Demo slide (6) must open the app — rehearse the live transition; have the fallback screenshot preloaded in the deck.
