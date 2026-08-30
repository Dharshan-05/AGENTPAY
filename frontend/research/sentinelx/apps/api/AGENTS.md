# SentinelX API — agent rules

## Quality gates (must pass before finishing any change)

```bash
cd apps/api && npm run typecheck
```

- `typecheck` runs `tsc --noEmit --noUnusedLocals --noUnusedParameters` (strict — no dead imports/vars).
- Smoke: `curl http://localhost:3001/api/health`.
- Server runs in-memory demo mode (`mode: "memory"`) — Prisma is the optional real-DB path, never required.
- Never commit; never remove functionality.
