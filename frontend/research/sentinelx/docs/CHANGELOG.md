# SentinelX — Changelog

All notable changes to the SentinelX platform. Phases build on each other; nothing from a previous phase is removed.

## Final Quality Sprint (2026-08-03)

**Theme:** continuous hardening loop — runtime stability, accessibility, and API edge cases.

- **Hydration safety** — `new Date()` calls removed from server-rendered JSX (header live clock, dashboard "updated X ago", executive briefing timestamps, reports modal) to eliminate client/server text-mismatch warnings; rendered from post-mount state instead.
- **Command palette** — ArrowDown on empty results no longer drops selection to -1; dialog gets `role="dialog" aria-modal` and input gets an accessible name.
- **Input accessibility** — `aria-label` added to scanner prompt textarea, provider route select, copilot chat textarea, audit search, and settings threshold sliders.
- **API hardening** — `/api/scan` returns 413 for prompts over 50,000 characters; 9 unused declarations removed so `tsc --noUnusedLocals --noUnusedParameters` exits clean on both apps.
- **Demo narration accuracy** — JWT / HR / patient narration lines now match the actual BLOCK decisions (was "rewrite initiated" for hard-blocked requests).
- **Robustness** — report download revokes the object URL after the click settles; copilot typing timer is cleared on unmount.
- **Copy accuracy** — landing hero now claims "real-time inline interception" instead of an unverifiable latency figure.

## Phase 12 — Judge Mode (live demo experience) (2026-08-02)

**Theme:** turn the demo into a rehearsed keynote.

### Judge Mode upgrades (`/demo`)
- **Voice narration** — browser speech synthesis speaks every narration caption as the 8 pipeline stages advance; toggle chip (Volume2/VolumeX) in header; auto-cancelled on stop / error / unmount; enabled automatically by Judge Mode.
- **Live threat activity strip** — animated risk-per-request bars in the progress card; critical bars glow red, latest result pulses.
- **Auto-generated report** — Judge Mode now auto-opens the Protection Report at finish and smooth-scrolls to it.
- **Accessibility** — narration caption is `aria-live`; voice toggle exposes `aria-pressed`.
- One-click Judge Mode now enables voice narration with a single entry point.

## Phase 11 — Enterprise Excellence & Judge Experience (2026-08-02)

**Theme:** the judge-facing surface — everything a panel would poke at.

- **Incident workspace** — related prompts (same-user / same-department / repeat-attempt / cleaned), resolution workflow stepper (Triage → Assign → Investigate → Contain → Resolve) with next-action hints.
- **Live collaboration** — `LiveNotifications` toasts on new incidents; `LiveCursorLayer` with 5 simulated analyst cursors over the SOC world map.
- **Executive board** — financial exposure (loss averted / fine exposure / breach cost), compliance score trend (5 quarters), risk forecast (14-day projection), `CountUp` gains `format` prop.
- **AI Executive Summary** — ExecutiveBriefing auto-loads `/api/compliance/summary` (real LLM with simulated fallback + model badge).
- **Risk simulator** — 4 sliders (policy strictness, employee awareness, threat volume, prompt sensitivity) recompute risk/blocked/violations/compliance live.
- **Digital twin** — named policy list + per-user risk scores per department.
- P4 (threat intel), P5 (AI memory), P8 (interactive explainability) audited as already complete.

## Phase 10 — Production Readiness (2026-08-02)

**Theme:** no more "hackathon" tells — branded error states, real health checks, clean logging.

- Branded `error.tsx` (Next 16 `unstable_retry`), `global-error.tsx`, `not-found.tsx`, dashboard `loading.tsx`.
- `icon.svg`, `manifest.ts`, `robots.ts`, full metadata + viewport (theme color, OG/Twitter cards).
- `validateEnv()` startup warnings; expanded `.env.example`.
- `/api/health` with `mode`, `providers`, and `database/redis/llm` checks; request logging with credential redaction; `/api/_dbg` removed.
- Silent `catch {}` removed from incident mutations (inline errors surfaced to the UI).

## Phase 9 — Enterprise Excellence (2026-08-02)

**Theme:** turn the security platform into an operations platform — incidents, intelligence, presence, memory, RBAC.

- **Incidents engine** — full incident lifecycle (`/api/incidents`, `GET/POST/PATCH`): seed incidents with SLA status (`CRITICAL 2h` / `HIGH 8h` / `MEDIUM 48h` / `LOW 96h`), note threads, severity + assignee mutations, workspaces.
- **Incident Response Center** — queue (filters, SLA clocks, severity) + workspace (evidence, risk reasoning, explainable AI, decision tree, alternative outcomes, report download).
- **Threat intelligence** — `/api/threat-intel` feed of 8 advisories from CISA, MITRE, OWASP, GitHub, OpenAI, Microsoft (CVSS, status, affected, mitigation, relevance).
- **Live presence** — Socket.io `presence:update` (6 analysts, 4 states) + presence panel in SOC; `incident:new` events.
- **Executive Copilot memory** — `/api/copilot/memory`: recall + write of conversation facts (`{count, recalled}`), memory chips in chat.
- **RBAC** — 7 roles (SECURITY_ADMIN, SECURITY_ANALYST, COMPLIANCE_OFFICER, AUDITOR, EMPLOYEE + 2 more) enforced across the platform.
- **Digital Twin upgrades** — department detail panels with incidents, violations, improvements.
- **Simulators** — Risk Simulator (policy strictness/awareness), Breach Cost Simulator.
- SLA fix: thresholds aligned (0 breached); 12/12 pages + endpoints verified.

## Phase 8 — Intelligence & Real AI (2026-08-02)

**Theme:** wire real LLMs in while keeping the zero-config demo path.

- Unified provider layer (`apps/api/src/llm/`) — OpenAI, OpenRouter, Gemini, Claude, Ollama with graceful simulation fallback.
- Token & cost tracking (`tiktoken`) → `/api/llm/usage`; LLM Gateway Usage panel on Analytics.
- AI-powered policy recommendations (`POST /api/policies/recommend`), AI compliance summaries (`GET /api/compliance/summary`), executive insights (`GET /api/executive/insights`), per-decision AI reasoning (`/api/explain/:id/ai-reasoning`), copilot AI intent + answer enhancement, env-gated AI rewrite + adaptive risk agent, `/api/llm/status`.

## Phase 7 — Enterprise Intelligence & Production Experience (2026-08-01)

### New: AI Explainability Center
- New page `/explain` (sidebar "Explainability", ⌘K `G Q`).
- New endpoint `GET /api/explain` — a decision corpus with per-decision agent contributions, risk/policy factors, reasoning timelines, confidence, and final recommendations.
- Expandable decision cards with an **animated SVG decision graph**, risk-contribution bars, policy-contribution chips, a 5-step reasoning timeline, and a recommendation panel.
- Confidence distribution gauges, decision-mix breakdown, and BLOCK/REWRITE/FLAG/ALLOW filters.

### Executive Copilot — rich cards
- Copilot now renders **rich data cards** under answers (`CopilotDataCards` component): department risk bars, highest-risk prompt lists, policy trigger frequency, detection categories, rewritten before/after, today-vs-yesterday KPI compare, and executive summary KPI grids.
- Fixed handler ordering so "Compare today vs yesterday" returns the comparison (was shadowed by the generic trend handler).

### Live Security Command Center (SOC)
- **Threat ticker**: scrolling live-feed marquee of recent events with decision badges.
- **Pipeline Throughput**: animated SVG sparkline of prompts/minute with a moving live marker (memoized component).
- Existing mission-control surfaces (world map, live counters, global threat feed, agent activity, incident queue, investigations, live attack stream, system health) remain intact.
- `GET /api/soc` extended with `throughput` (24-point series) and `ticker` (recent events).

### Enterprise Analytics
- **Risk Trend Forecast** — 14-day projection chart with actual/forecast/upper/lower bounds.
- **Incident Heatmap** — 7 days × 24 hours animated grid.
- **Policy Effectiveness** — detected vs prevented stacked bars with effectiveness %.
- **Detection Accuracy** — 12-month accuracy trend.
- **Compliance Score Trend** — quarterly score area chart.
- CSV export extended with all new datasets.

### Digital Twin
- Department roster now: Engineering, Finance, Human Resources, Sales, Legal, Operations.
- Each department now reports a **policies** count shown in cards and the detail panel.

### Enterprise Settings
- New **Branding** tab: organization name, accent color picker, theme toggle, support contact, footer note, with a **live preview** card.
- New **Export** tab: format toggles (PDF/CSV/JSON/PNG), scheduled digest frequency, prompt-text/PII inclusion controls, and an export-policy panel.
- **Quick-start Policy Templates** added to the Policy Builder (HIPAA/PCI/GDPR one-click prefill).
- Existing overview, policy builder, notifications, API tokens, and roles tabs unchanged.

### Presentation Mode 3.0 — Judge Mode
- New one-click **Judge Mode** button on `/demo`: enters judge presentation mode (larger type, 0.55× pacing, narration, auto-scroll, hidden developer controls) and starts the 6-attack sequence automatically.
- Judge Mode 2.0 features (narration captions, timer, confetti, protection report export) retained.

### Performance
- Memoized: `CopilotDataCards`, `MemoThroughput`, `MemoIncidentHeatmap`, `MemoDecisionGraph`.
- Derived data kept in `useMemo`; existing lazy/skeleton patterns preserved.

### Navigation
- Sidebar, command palette, and `G Q` keyboard shortcut for the Explainability Center.

### Quality
- `tsc --noEmit` clean on `apps/web` and `apps/api`.
- `next build` clean — 23 routes (22 static + 1 dynamic).
- 20/20 pages and 15/15 API endpoints verified 200; no console/server warnings.

### Documentation
- New: `docs/PHASE_7_COMPLETION_REPORT.md`, `docs/CHANGELOG.md`.
- README updated (Phase 7 section, Explainability page, keyboard shortcuts, repo layout).

---

## Phase 6 — Production Experience & Judge WOW (2026-08-01)

- Premium **Toast** system (5 kinds, auto-dismiss progress, spring layout) + **Magnetic** hover wrapper.
- **SOC Global Threat Feed** — 6 regions with pulse→routing→containing→resolved lifecycle + live counters.
- **Executive Copilot** — telemetry-grounded answers (threats, posture, GDPR, today-vs-yesterday, executive summary) + markdown table rendering.
- **Interactive Pipeline** (scanner) — replay controls (play/pause/step/speed 0.5–4×), animated data packet, trace export.
- **Demo Mode + Judge Presentation Mode** — 6-scenario auto-run, typing prompt, narration captions, timer, confetti, protection report with JSON export.
- **Incident Workspace** — report download + Alternative Outcome / What Rule Fired / How-Decided explainability cards.
- **Enterprise Settings** — 5 tabs (Overview, Policy Builder, Notifications, API Tokens, Roles).
- **Analytics exports** — PNG (SVG→canvas), CSV (10 datasets), brush zoom.
- **Digital Twin** — zoomable/pannable org graph.
- **Documentation** — 8 files including `FINAL_VERIFICATION_REPORT.md`.

## Phase 5 — Enterprise Platform Build (earlier)

- Executive Command Center, Mission Control (SOC) with world threat map, Organization Digital Twin, Explainable AI on every decision, Enterprise Analytics suite, Presentation Mode 2.0 (confetti + report), System & Infrastructure page, accessibility pass (reduced-motion, focus states, keyboard nav).

## Phases 1–4 — Core Foundation

- 8-agent AI governance pipeline (inspector, secret detection, policy engine, risk engine, rewriter, LLM adapter, audit logger, memory).
- 42 detection rules (Luhn-validated PAN, API keys, JWT, PII, credentials), 7 policy packs (GDPR, HIPAA, PCI DSS, SOC 2, ISO 27001, Internal, Secrets).
- Composite risk scoring → ALLOW / REWRITE / BLOCK / FLAG.
- Fastify API + Next.js dashboard, in-memory demo store with optional PostgreSQL/Redis.
