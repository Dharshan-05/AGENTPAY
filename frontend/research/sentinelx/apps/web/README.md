# SentinelX Web Console

Next.js 16 application for the SentinelX AI Governance Firewall — the operator, analyst, CISO, and judge-facing console.

## Stack

- **Next.js 16** (App Router, React 19, server-side rendered with client islands)
- **Tailwind CSS v4** — custom design tokens in `src/lib/design-tokens.ts`
- **Framer Motion** — animated pipeline stages, gauges, and page transitions
- **Socket.io client** — live agent telemetry from the SentinelX API (`src/lib/live.ts`)

## Development

```bash
npm install
npm run dev        # http://localhost:3000
```

The web app expects the SentinelX API on `http://localhost:3001`
(override with `NEXT_PUBLIC_API_URL`). The API runs in in-memory demo
mode with zero configuration — see `../api/README`-equivalent
documentation in the root `README.md`.

## Quality gates

```bash
npm run typecheck  # tsc --noEmit --noUnusedLocals --noUnusedParameters
npm run build      # production build (all routes static except /incidents/[id])
```

## Structure

- `src/app/(dashboard)/` — the 17 console pages (executive, SOC, scanner, twin, copilot, …)
- `src/app/page.tsx` — public marketing landing page
- `src/components/layout/` — sidebar, header, status bar, command palette, notifications
- `src/components/ui/` — shared primitives, gauges, world map, simulator, briefing components
- `src/lib/` — API client (`api.ts`), socket client (`live.ts`), RBAC (`rbac.ts`)
