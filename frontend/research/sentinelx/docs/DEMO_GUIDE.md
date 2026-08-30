# SentinelX — Demo Guide

## Getting started

```bash
# terminal 1 — API
cd apps/api && npm run dev        # http://localhost:3001

# terminal 2 — web
cd apps/web && npm run dev        # http://localhost:3000
```

Open **http://localhost:3000** → the sidebar lists every product page.

## 2-minute walkthrough

| # | Route | What to show |
|---|-------|--------------|
| 1 | **/demo → Judge Mode** | One click: enters keynote presentation (larger type, faster animation, narration captions, presentation timer, auto-scroll, dev controls hidden) and auto-runs all six attacks: AWS key → JWT → HR database → credit card → source code → patient record. Ends in confetti + a downloadable protection report. |
| 2 | **/demo → Run demo** | Manual six-attack run with live stage and typed prompts (for normal walkthroughs). |
| 3 | **/scanner** | Paste any prompt, watch the 8-agent pipeline animate. After the scan, use **Pipeline Replay** (play/pause/step/speed) and **Export trace**. |
| 4 | **/incidents/[id]** | Open any incident: full decision chain, risk reasoning, matched patterns, alternative outcomes, report download. |
| 5 | **/copilot** | Ask "Why did threats increase this week?", "Compare today vs yesterday", "Generate an executive summary". |
| 6 | **/soc** | Global Threat Feed — 6 regions with pulse → routing → containment → resolved lifecycle, live counters. |
| 7 | **/twin** | Org risk graph — drag to pan, scroll/+− to zoom, click a department. |
| 8 | **/analytics** | Brush-zoom the monthly chart; export CSV or PNG. |
| 9 | **/settings** | Policy Builder, Notification Rules, API Tokens, Roles tabs. |

## Reliable demo scenarios

| Scenario | Prompt (paste into scanner) | Expected |
|---|---|---|
| AWS secret | `AKIAIOSFODNN7EXAMPLE` in a prompt | BLOCK, risk ~89 |
| Credit card | `4242 4242 4242 4242, expiry 09/28, CVV 321` | BLOCK, PCI DSS |
| Clean prompt | marketing copy | ALLOW, no violations |

## Demo tips

- Always run from **/demo** first — it needs no manual input and self-narrates.
- Use **Judge mode** for any audience ≥ 3 people; it is designed to read like a keynote.
- Export the protection report at the end as the closing artifact.
- Refresh the page between demo runs to reset the live telemetry.
