# SentinelX — Screenshot Guide

> Captures for the README gallery, pitch deck, and GitHub social preview. Dark theme throughout; no browser chrome visible.

## Capture settings

| Setting | Value |
| --- | --- |
| Browser | Chrome (or Safari) — fullscreen, no bookmarks bar |
| Viewport | 1920×1080 (recommended); capture at 100% zoom |
| Dark mode | On (app is dark by default) |
| DevTools | Closed; hide cursor where possible (Cmd+Shift+X with a cursor-hider extension, or keyboard-only navigation) |
| Format | PNG 2× for README; JPG for deck backgrounds |

## Screenshot list

| # | Page | When to capture | What must appear |
| --- | --- | --- | --- |
| 1 | `/` (landing) | Immediately on load | Hero headline, architecture diagram, CTA — clean top fold |
| 2 | `/executive` | On load (before animations settle, ~1 s) | Security score, maturity gauge, compliance status, dept breakdown, financial exposure row |
| 3 | `/soc` | On load, ~3 s in | World threat map, live attack stream, incident queue, threat ticker running |
| 4 | `/twin` | On load, ~2 s in | Org risk graph (6 departments), department DNA panel on the right |
| 5 | `/analytics` | On load | 15-chart grid — risk forecast, incident heatmap, policy effectiveness, compliance trend |
| 6 | `/scanner` | Mid-run of any scenario | 8-agent radar mid-animation, data packet, running timers |
| 7 | `/demo` (Judge Mode) | During 2nd–3rd attack | Narration bar, stage steps, RiskGauge, threat-activity strip, LIVE badge |
| 8 | `/demo` (finished) | Right after "All threats neutralized" | Confetti + success banner + Protection Report table |
| 9 | `/explain` | On a card expanded | Decision graph, agent contributions, reasoning timeline, confidence ring |
| 10 | `/incidents/[id]` | On load | Evidence, risk reasoning, decision tree, resolution workflow stepper |
| 11 | `/copilot` | After asking a question | Rich visual answer card (dept risk, threat drivers, executive summary) |
| 12 | `/compliance` | On load | Regulatory status cards (GDPR, HIPAA, PCI DSS, SOC 2, ISO 27001) with evidence |

## Animation timing

| Element | Time to settle | Trick |
| --- | --- | --- |
| CountUp numbers | ~1.5 s | Capture at 1–2 s after load |
| Stage animations (`/scanner`, `/demo`) | ~2–3 s per step | Capture mid-step for "live" feel |
| Charts (Recharts) | ~0.5 s | No delay needed |
| Toasts | 4 s auto-dismiss | Capture within first 2 s, or re-trigger a scan |

## Zoom & crop

- Capture at 100% zoom for crisp text; resize to 2× if capturing at 150%.
- Crop top 20% nav bar away only if it looks plain; otherwise keep for context.
- Keep the left sidebar visible in dashboard shots — it shows the product is a platform.

## Pacing for the judge presentation

1. Screenshots 2, 7, 10 are the ones judges will see — capture them first.
2. Record a short demo video (Phase 14) at 60 fps, ~2 minutes, judge mode auto-run, with voice narration ON for audio.
3. GitHub social preview banner: 1280×640, dark background, tagline "Every prompt. Every model. Zero secrets leaking." + Executive Command Center screenshot.
