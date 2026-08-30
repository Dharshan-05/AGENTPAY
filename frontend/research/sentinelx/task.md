# Railway Fix Task List

- [/] Fix `apps/api/railway.toml` — remove `PORT = "3001"`, fix healthcheckTimeout
- [ ] Fix root `railway.toml` — increase healthcheckTimeout, remove HOST override
- [ ] Fix `server.ts` — PORT fallback to 8080, fix CORS allowlist
- [ ] Update `apps/web/.env.local` — point NEXT_PUBLIC_API_URL to Railway
- [ ] Run typecheck
- [ ] Run build
- [ ] Verify dist/server.js PORT binding
- [ ] git diff + commit
- [ ] git push origin main
- [ ] Smoke test production /api/health
