<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# Quality gates (must pass before finishing any change)

```bash
cd apps/web && npm run typecheck && npm run build
cd apps/api && npm run typecheck
```

- Both `typecheck` scripts run `tsc --noEmit --noUnusedLocals --noUnusedParameters` (strict — no dead imports/vars).
- Smoke: API `http://localhost:3001/api/health`, web `http://localhost:3000/dashboard`.
- Never commit; never remove functionality; demo runs in-memory (no provider keys needed).
