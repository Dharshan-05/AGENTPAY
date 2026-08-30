# SentinelX — Backup Demo Plan

> SentinelX is built to never need internet, keys, or a database. But laptops fail. Here is how to recover any failure in under 30 seconds.

## Golden rule

**The demo state lives in the API process, not the browser.** Keep the API process alive and you can survive any browser or page failure. Keep two terminals pre-opened at all times:

```
Terminal 1 (API):  cd apps/api        → npx tsx src/server.ts
Terminal 2 (Web):  cd apps/web        → npm run dev
```

## Failure matrix

| Failure | Symptom | Recovery (under 30 s) |
| --- | --- | --- |
| Internet dies | Page loads (all local) — nothing breaks. Judge Mode keeps running | No action. Demo is 100% local |
| LLM fails / keys invalid | Startup shows simulated-provider warning; scans still return results | No action. Simulated fallback is the designed demo path |
| API crashes | Every page shows toasts with errors; numbers stop | `Cmd+C` in Terminal 1 → `npx tsx src/server.ts` → wait for "listening" → refresh |
| Browser crashes | Tab gone; API still running | Reopen http://localhost:3000 → incidents, audits, and stats return (they live in the API) |
| Web dev server crashes | Page fails to load | `Cmd+C` in Terminal 2 → `npm run dev` → wait for "Ready" → open localhost:3000 |
| Laptop freezes | Everything dead | Hard reboot → reopen both terminals (commands are in this file) → both servers up in < 60 s |
| Scan endpoint broken | `/scanner` errors | `curl /api/health`; if `ok` refresh the page; if not, restart API |
| Judge Mode freezes mid-run | Stage stops advancing | Click **Stop demo** → **Run full demo**. Timer/state reset is full |
| Voice narration silent | No audio | Click **Voice narration** toggle (browser gesture rule). Captions still narrate visually |
| Confetti / report missing at end | Banner absent | The report button appears in the success banner; click **Run again** for a fresh pass |

## Recovery scripts (recommended)

Create `start-demo.sh` in the repo root (not committed with credentials, just convenience):

```bash
#!/usr/bin/env bash
set -e
echo "Starting SentinelX API on :3001 ..."
(cd apps/api && nohup npx tsx src/server.ts > /tmp/sentinelx-api.log 2>&1 &)
sleep 2
echo "Starting SentinelX web on :3000 ..."
(cd apps/web && nohup npm run dev > /tmp/sentinelx-web.log 2>&1 &)
sleep 5
curl -sf http://localhost:3001/api/health && echo "API OK"
curl -sf -o /dev/null http://localhost:3000/demo && echo "WEB OK"
```

> Paste this into a terminal to bring the whole product back after any crash. `docs/JUDGE_CHECKLIST.md` has the pre-talk verification pass.

## State you lose

- Refresh loses nothing visible (data is served from the API in-memory store).
- Restarting the API resets incidents/audits created during the session back to the seeded baseline — that's acceptable; the seeded data is already demo-rich.

## 60-second full restore (worst case: dead laptop)

1. Power on → open terminal.
2. `cd "Shadow AI Leak Detector" && bash start-demo.sh`
3. Open http://localhost:3000 → `/demo` → **Judge Mode**.
4. Total elapsed: under 60 seconds, zero configuration, zero keys.
