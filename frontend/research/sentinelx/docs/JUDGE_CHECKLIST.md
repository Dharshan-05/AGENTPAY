# SentinelX — Judge Checklist

> Run this before every presentation. Everything below must work before you walk into the room.

## Before the demo

| Item | Check |
| --- | --- |
| API running | `curl http://localhost:3001/api/health` → `"status":"ok"`, `"mode":"memory"` |
| Web running | `curl -o /dev/null -w "%{http_code}" http://localhost:3000/demo` → `200` |
| Terminal windows | Pre-opened on the API and web logs; both visible on a second screen or alt-tab reachable |
| No API keys needed | Confirm startup log shows the expected simulated-provider warning (this is normal) |
| Incident store | At least one open incident exists (`/incidents`) so the Incident Response Center shows data |

## Internet

- **Internet is optional** — SentinelX runs fully offline in demo mode. Verify once that nothing in the demo path (scan → demo → reports) attempts a network call.
- If you want live LLM responses, providers require keys — decide this before the event; the demo is designed to run without them.

## Audio & voice narration

| Item | Check |
| --- | --- |
| System volume | Up, external speaker tested |
| Browser audio permission | Open `/demo` → click **Voice narration** once → a line is spoken |
| Backup | Captions appear regardless of audio — the demo still tells the story silently |

## Animations & interactions

- Judge Mode auto-runs all 6 attacks with stage animation, threat-activity bars, and confetti.
- ⌘K command palette opens and `G` + key navigation works.
- Toasts appear on scans and incidents.
- All CountUp numbers animate (no static 0s — means API is not connected).

## Shortcuts to rehearse

| Keys | Action |
| --- | --- |
| ⌘K → `G D` | Dashboard |
| ⌘K → `G X` | Executive |
| ⌘K → `G O` | Mission Control (SOC) |
| ⌘K → `G P` | Demo |
| ⌘K → `G Q` | Explainability |
| ⌘K → `G C` | Copilot |
| ⌘K → `G W` | Twin |

## Browser

- Chrome, latest, fullscreen, 1920×1080 (or the event resolution — test at the actual event screen).
- Zoom 100%; text crisp. Disable extensions that inject into pages.
- Close all other tabs; disable system notifications during the talk.

## Theme & polish

- Dark theme confirmed (app default); no light-mode flash on load.
- Title tab shows SentinelX with the teal icon (icon.svg in the manifest).
- 404 page is branded — route to a random URL once as a sanity check.

## API & backup mode

| Failure | Primary recovery | Time |
| --- | --- | --- |
| API dies | `cd apps/api && npx tsx src/server.ts` | < 5 s |
| Web dies | `cd apps/web && npm run dev` | < 10 s |
| Both died | Restart script / pre-warmed tmux sessions (see `docs/BACKUP_PLAN.md`) | < 30 s |
| Scan errors | `/api/health` must be `ok`; restart API, refresh page | < 15 s |

## 5 minutes before you start

1. `curl /api/health` + `curl /demo` — both green.
2. Open `/demo` and warm the voice-narration click.
3. Reset any stray demo state: refresh the browser (in-memory state persists across refresh via the API, not the page).
4. Mute notifications, close tabs, stand next to the machine.
5. Breath. One click. Let SentinelX narrate.
