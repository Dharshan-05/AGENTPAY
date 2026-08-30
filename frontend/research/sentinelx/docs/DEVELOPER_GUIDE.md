# SentinelX — Developer Guide

This guide covers the codebase layout, the live pipeline protocol, and the
frontend architecture. For the demo flow and quick start, see the root
[README](../README.md).

## Repository layout

```
apps/api                  Fastify 5 + TypeScript governance gateway
  prisma/schema.prisma    Data models (User, AuditLog, Policy, DetectionRule, Alert, ...)
  src/server.ts           Routes, socket.io bridge, copilot engine
  src/agents/             The 8 agents + pipeline orchestrator
  src/engines/            Detection rules (42), policy packs (7), risk scoring, rewriting
  src/lib/store.ts        Prisma facade with in-memory demo fallback
  src/lib/redis.ts        Cache helpers + demo auto-seeding
  src/seed/               Demo data generator
apps/web                  Next.js 16 + Tailwind v4 dashboard
  src/app/(dashboard)/    App shell + 10 pages
  src/components/         Layout shell + UI primitives
  src/lib/api.ts          Typed REST client + shared constants
  src/lib/live.ts         socket.io client (single shared instance)
  src/types/index.ts      Shared TypeScript types (mirror API payloads)
docs/                     Planning + architecture docs
```

## The agent pipeline

`SentinelPipeline.execute()` (apps/api/src/agents/pipeline.ts) runs the eight
agents sequentially. Each completed stage produces an `AgentTraceEntry`
(agent id, status, confidence, execution time). Two side channels are emitted
per stage:

| Channel | Payload | When |
| --- | --- | --- |
| `agent:update` (socket.io broadcast) | `AgentTraceEntry` | after each agent completes |
| `scan:complete` (socket.io broadcast) | `{ auditLogId, decision, riskScore }` | when the run finishes |
| REST `POST /api/scan` response | full `PipelineResult` | when the run finishes |

Pacing: each stage waits `PIPELINE_PACE_MS + random(0..PIPELINE_PACE_JITTER_MS)`
before its update is emitted, so the UI animation reads as a live execution.
Set both to `0` for fast programmatic use. Seeding always runs unpaced.

### Frontend playback (apps/web scanner)

The scanner subscribes to `agent:update` and applies entries as they arrive
(`applyTrace`), advancing a cursor through the stage list. When the REST
response resolves, any missing stages are replayed from `result.agentTrace`
at 220 ms intervals (`replayTrace`), guaranteeing a correct final state even
if the socket never connected. `scan:complete` is currently informational.

## Store facade rules (apps/api/src/lib/store.ts)

The API has zero hard dependencies:

- `store.auditLog.create(data)` — pass the data object directly; do **not**
  wrap it in `{ data }` (the facade unwraps `data.data ?? data` itself).
- `store.auditLog.count({ where })` — pass `{ where }`, not a bare query
  (facade reads `where?.where ?? where`).
- In-memory mode auto-detects when PostgreSQL is unreachable and persists
  nothing — records reset on server restart, then `seedDemoDataIfEmpty()`
  repopulates demo data on boot.

## Frontend conventions

- **Theme**: Tailwind v4 `@theme` tokens in `globals.css` (`bg-primary`,
  `accent`, `border-*`, `status-*`, `text-*`). Reusable classes: `glass-card`,
  `card-glow`, `tech-chip`, `mono`, `scanline`, `skeleton`, `heartbeat`,
  `pulse-dot`, `grid-bg`, `agent-node`.
- **Typography**: Inter (UI) + JetBrains Mono (`mono` class for numbers).
- **UI kit**: `components/ui/primitives.tsx` (Badge, SeverityBadge,
  DecisionBadge, RiskGauge, PageHeader, EmptyState, SectionTitle),
  `components/ui/stat-card.tsx`, `components/ui/motion.tsx` (CountUp,
  Skeleton, GlowCard, Switch).
- **Data layer**: always go through `src/lib/api.ts`; never call `fetch`
  directly. `lib/live.ts` exports the single socket.io instance — call
  `subscribeAgentUpdates(cb)` and unsubscribe on unmount.
- **Charts**: Recharts. Wrap chart components in `React.memo` and derive
  their data with `useMemo` to avoid re-renders on the 10 s polling cycle.
  Heavy renderers get a `Memo*` export name (e.g. `MemoThroughput`,
  `MemoIncidentHeatmap`, `MemoDecisionGraph`).
- **Copilot rich answers**: `POST /api/copilot` may return a `data` payload
  alongside text; the web copilot renders it with
  `components/ui/copilot-cards.tsx` (`CopilotDataCards`). Any new copilot
  branch can attach a `data` array (dept risk, policy triggers, detection
  categories, highest-risk prompts, rewrites, today/yesterday, KPI grids).
- **Explainability**: decision explainability beyond incident pages lives in
  `/explain` backed by `GET /api/explain`; keep the `ExplainDecision` /
  `ExplainStats` types in `src/types/index.ts` in sync with the API shape.
- **Client components only** in `(dashboard)`: pages fetch on the client and
  render loading skeletons; no server components fetch API data.
- **No em-dashes in TS source files** — the dev toolchain previously failed
  to parse UTF-8 em-dashes in string literals. Use ASCII `-` or `·` only.

## Running

```bash
# API
cd apps/api && npm install && npx tsx src/server.ts

# Web
cd apps/web && npm install && npm run dev
```

### Verification commands

```bash
cd apps/api
npx tsc --noEmit                    # typecheck
npx tsx smoke.ts                    # REST smoke test
npx tsx smoke-pipeline.ts           # pipeline smoke test
npx tsx src/seed/run.ts             # force re-seed (memory mode only)

cd apps/web
npm run build                       # production build + typecheck
```

## Adding a detection rule or policy pack

1. **Rule**: add to the rule list in `apps/api/src/engines/detectors.ts`
   (name, regex pattern, severity, category, confidence). Avoid em-dashes.
2. **Policy pack**: add a pack in `apps/api/src/engines/policies.ts` using
   `policyPack(...)` + `rule(id, desc, severity, triggersOn, recommendation,
   explain)`; rules reference detection categories.
3. Re-seed (`npx tsx src/seed/run.ts`) to see it in `/policies` and
   `/compliance`.
