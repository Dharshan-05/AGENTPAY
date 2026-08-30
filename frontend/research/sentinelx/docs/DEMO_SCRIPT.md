# SentinelX — Demo Script (5-Minute Judge Presentation)

> The goal: judges understand the **problem** (Shadow AI), see the **solution** (8-agent governance gateway) and believe it is **production-ready**. The demo runs itself — your job is narration, not clicking.
>
> Timing assumes **Judge Mode** (`/demo` → **▶ Judge Mode**): voice narration ON, 0.55× pace, ~2 minutes for the 6-attack sequence. Remaining time is yours for setup, story, and Q&A.

---

## The 5-Minute Structure

| 0:00–0:30 | 0:30–1:30 | 1:30–3:30 | 3:30–4:00 | 4:00–5:00 |
| --- | --- | --- | --- | --- |
| Hook & problem | Why it matters | Live demo (Judge Mode) | Explainability deep-dive | Numbers, closing, CTA |

---

## Script

### 0:00–0:30 — Hook (before clicking anything)

**What to say:**
> "Every company has a data leak it can't see. Employees paste credentials, source code, patient records, and customer data into AI chat tools every single day — and security teams have zero visibility into it. That's Shadow AI. SentinelX is the firewall for that gap."

**Do:** Stand beside the screen, gesture toward the Executive Command Center. No clicking yet.

### 0:30–1:30 — Why it matters (Executive Command Center, `/executive`)

**What to say:**
> "This is what the CEO sees. A live security score, compliance posture across GDPR, HIPAA, PCI DSS, and SOC 2, financial exposure — and a risk forecast. One number executives can understand: how much sensitive data stayed inside the company today."

**Do:** Hover the security score and the Compliance Trend chart. Mention the financial exposure panel. One sentence each. Do not read the screen.

### 1:30–3:30 — Live demo (Demo Mode, `/demo` → **▶ Judge Mode**)

**What to say (the app narrates; you add color):**
> "This is one click. Six real attacks — an AWS access key, a JWT, HR salary data, a credit card, source code, a patient record. Watch the pipeline: Inspector Agent classifies it, Secret Detection finds the credential, the Policy Engine applies the regulation, the Risk Engine scores it, and the Rewriter strips it before it ever reaches a model."

**Do:** Click once. Point at the stage animation, then at the RiskGauge when the first result lands. Let voice narration carry the rest. When the report auto-opens at the end: "…and every decision is summarized in an exportable protection report."

### 3:30–4:00 — Explainability deep-dive (`/explain` or incident workspace)

**What to say:**
> "Security teams need more than a block. Every decision is explainable — which agent found what, which policy was triggered, and the reasoning timeline. This is what makes it deployable in a regulated enterprise."

**Do:** Navigate with ⌘K → `G Q` (explainability) or open an incident from `/incidents`. Show the decision graph and reasoning timeline. One pass, no scrolling.

### 4:00–5:00 — Numbers, closing, CTA

**What to say:**
> "SentinelX runs with zero external dependencies — no API keys, no database, no internet — it is judge-ready from a fresh checkout. 8 agents, 42 detection rules, 7 policy packs, an immutable audit trail, and a full command center. We govern the prompt before the model ever sees it."

**Close:** "SentinelX: every prompt, every model, zero secrets leaking. Thank you — happy to demo more or walk through the architecture."

---

## Judge talking points (if there is Q&A)

- **Why not just block AI?** Blocking creates shadow IT. Governance keeps productivity and adds safety.
- **How is this different from DLP?** DLP secures stored data; SentinelX governs the AI conversation boundary in real time, with model-aware decisions and rewrites.
- **Latency?** The pipeline runs in ~240 ms per stage with simulated providers; real providers add model latency only.
- **What about agents talking to agents?** Memory agent + presence are the first layer; agent-to-agent guardrails are on the roadmap.
- **Persistence?** PostgreSQL + Prisma in production; in-memory demo mode for zero-config judging.
- **RBAC?** 7 roles — SECURITY_ADMIN, SECURITY_ANALYST, COMPLIANCE_OFFICER, AUDITOR, EMPLOYEE, and more, enforced across the UI.

## Transitions (scripted beats)

1. Executive board → demo: "Now let's watch it work."
2. Demo → explainability: "Any security tool can block. Here's the part that makes it deployable."
3. Explainability → close: "That's the whole loop — detect, decide, explain, report."

## What NOT to say

- Do not mention "hackathon" unless asked; let the product speak.
- Do not apologize for missing features or say "it's just a demo".
- Do not claim production deployment stats you don't have (no real customers, no real money).
- Do not read the screen verbatim; paraphrase in one-liners.
- Do not click around during the demo — Judge Mode runs itself; extra clicks break the illusion.

## Recovery plan if the demo fails

| Failure | Recovery (under 30 seconds) |
| --- | --- |
| API not running | Terminal 1: `cd apps/api && npx tsx src/server.ts` → wait for "listening" → refresh `/demo` |
| Web not running | Terminal 2: `cd apps/web && npm run dev` → wait for "Ready" → open http://localhost:3000 |
| Judge Mode freezes | Press **Stop demo** → **Run full demo** again (state resets fully) |
| Voice narration missing | Click **Voice narration** toggle once (browser may require a click first); captions still appear |
| Scan returns errors | Check API terminal for red logs; `/api/health` should return `ok` + `mode: memory` |
| Browser crashes | Relaunch browser → http://localhost:3000 (in-memory state persists for the session; incidents survive since API stays up) |
| Laptop freezes | See `docs/BACKUP_PLAN.md` — pre-warmed terminals + auto-start scripts |

## Pre-demo checklist (5 minutes before)

1. Both servers running and `/api/health` returns `ok`.
2. Open http://localhost:3000/demo, verify Judge Mode button present.
3. Test voice narration ONCE (click toggle) so the browser allows audio.
4. Close all other tabs; disable notifications.
5. Screen resolution check — see `docs/JUDGE_CHECKLIST.md`.
