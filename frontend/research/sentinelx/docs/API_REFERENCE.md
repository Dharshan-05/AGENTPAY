# SentinelX — API Reference

Base URL: `http://localhost:3001`. All routes are prefixed with `/api`. Content-Type: `application/json`.

## Core

### `POST /api/scan`
Scan a prompt through the full pipeline.

```json
{ "prompt": "…", "provider": "openai", "userId": "optional" }
```

Returns `PipelineResult`:

```ts
{
  pipelineId, status, decision, riskScore, threatLevel,
  violations: PolicyViolation[], secrets: DetectedSecret[],
  originalPrompt, rewrittenPrompt | null,
  agentTrace: AgentTraceEntry[], auditLogId, provider, model, latencyMs
}
```

### `GET /api/health`
Service liveness: `{ status, service, version, timestamp }`.

## Audit & governance

| Route | Description |
|---|---|
| `GET /api/audit?page=&limit=&search=` | Paginated audit log |
| `GET /api/audit/:id` | Single audit record |
| `GET /api/policies` | Enabled policy packs |
| `GET /api/rules` | Detection rules |
| `GET /api/alerts` | Security alerts |
| `POST /api/alerts/:id/ack` | Acknowledge an alert |
| `GET /api/settings` | Gateway settings map |
| `GET /api/agents/health` | Per-agent health telemetry |
| `GET /api/dashboard` | Command-center KPIs: totals, blocked, violations 24h, sessions, recent 50, sparklines, region map |
| `GET /api/presence` | Live analyst presence (avatar/name/status/role/region) |
| `POST /api/policies/recommend` | AI-suggested policy packs for an industry |
| `GET /api/compliance/summary` | Compliance posture + AI-generated executive briefing text |

## Incident response

| Route | Description |
|---|---|
| `GET /api/incidents?severity=&status=` | Incident queue + open/critical/breached stats |
| `GET /api/incidents/:id` | Full incident: timeline, evidence, notes, related prompts |
| `POST /api/incidents/:id/notes` `{ body, author? }` | Add investigation note |
| `POST /api/incidents/:id/assign` `{ owner }` | Assign owner |
| `POST /api/incidents/:id/status` `{ status: TRIAGE\|INVESTIGATING\|CONTAINED\|RESOLVED }` | Advance resolution workflow |
| `POST /api/incidents/:id/evidence` `{ label, value, kind? }` | Attach evidence capture |
| `GET /api/incidents/:id/export` | Regulator-grade JSON report |

## Threat intelligence

| Route | Description |
|---|---|
| `GET /api/threat-intel` | Advisory feed: campaigns, CVE-linked IoCs, MITRE ATT&CK, sources, stats |
| `GET /api/threat-intel/:id` | Single advisory with response playbook |

## Copilot

| Route | Description |
|---|---|
| `GET /api/copilot/suggestions` | Suggested prompts (incl. executive) |
| `POST /api/copilot` `{ message }` | Rule-based telemetry answer with `data` |
| `POST /api/copilot/intent` `{ message }` | Intent classification + telemetry payload for quick actions |

Executive queries supported: why threats increased, department risk, GDPR violations, today vs yesterday, current posture, executive summary.

## Enterprise telemetry

| Route | Payload highlights |
|---|---|
| `GET /api/executive` | security score, maturity, compliance status, KPIs, department breakdown, alerts, recommendations |
| `GET /api/executive/insights` | AI-generated CISO briefing (trends, risks, wins) |
| `GET /api/executive/kpis` | Executive KPI series (revenue risk, uptime, compliance) |
| `GET /api/soc` | threat map, stream, agent activity, queues, investigations, **regions** (6-region feed with attack lifecycle), **counters**, **throughput** (24-pt series), **ticker** (recent events) |
| `GET /api/twin` | departments (Engineering, Finance, Human Resources, Sales, Legal, Operations) with risk index, violations, incidents, compliance, improvements, **policies** count |
| `GET /api/analytics` | monthly/weekly/hourly threats, dept + policy comparison, risk evolution, detection donut, agent latency, pipeline duration, compliance radar, **riskForecast** (14-pt), **incidentHeatmap** (7d×24h), **policyEffectiveness**, **detectionAccuracyTrend** (12 mo), **complianceScoreTrend** |
| `GET /api/explain` | **AI Explainability**: `decisions[]` (prompt, decision, riskScore, threatLevel, user, department, confidence, recommendation, `agentContributions[]`, `riskFactors[]`, `policyFactors[]`, `reasoningTimeline[]`) + `summary` (blocked/rewritten/flagged/allowed/avgRisk/topAgent) |
| `GET /api/explain/:id/ai-reasoning` | Per-decision AI reasoning narrative |
| `GET /api/explain/ai-notes` | AI explainability notes feed |
| `GET /api/system` | version, deployment, cluster, CPU/mem/latency/queue, infra status, pods/replicas/canary |
| `GET /api/llm/status` | Provider configuration + simulation mode |
| `GET /api/llm/usage` | Token + estimated-cost usage counters |

## Errors

- `400` — missing/invalid input (e.g. empty prompt).
- `404` — resource not found (e.g. audit id).
- `413` — prompt payload exceeds 50,000 characters.
- Non-2xx responses include an `error` field.
