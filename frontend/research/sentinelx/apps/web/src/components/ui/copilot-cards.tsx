"use client"

import { memo } from "react"
import { motion } from "framer-motion"
import {
  Activity,
  ArrowDown,
  ArrowUp,
  Building2,
  Gavel,
  Landmark,
  ShieldAlert,
  ShieldCheck,
  Tag,
  Wand2,
} from "lucide-react"
import { DecisionBadge } from "./primitives"
import { cn } from "@/lib/utils"

function isArray(v: unknown): v is unknown[] {
  return Array.isArray(v) && v.length > 0
}

function barsFor(rows: unknown[]): Array<{ label: string; value: number; suffix?: string }> {
  return rows.map((r) => {
    const o = r as Record<string, unknown>
    const label = String(o.dept ?? o.department ?? o.regulation ?? o.category ?? o.policyName ?? o.name ?? "item")
    const value = Number(o.risk ?? o.riskIndex ?? o.avg ?? o.count ?? o.idx ?? 0)
    return { label, value, suffix: o.riskIndex !== undefined ? "%" : o.avg !== undefined ? "" : o.count !== undefined ? "" : undefined }
  })
}

function BarList({ rows, color, suffix }: { rows: Array<{ label: string; value: number; suffix?: string }>; color: string; suffix?: string }) {
  const max = Math.max(...rows.map((r) => r.value), 1)
  return (
    <div className="space-y-2">
      {rows.map((r, i) => (
        <div key={r.label}>
          <div className="flex items-center justify-between text-[11px]">
            <span className="truncate text-text-secondary">{r.label}</span>
            <span className="mono text-text-muted">
              {r.value}{r.suffix ?? suffix ?? ""}
            </span>
          </div>
          <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${(r.value / max) * 100}%` }}
              transition={{ duration: 0.6, delay: i * 0.04 }}
              className={cn("h-full rounded-full", color)}
            />
          </div>
        </div>
      ))}
    </div>
  )
}

function KpiCard({ icon: Icon, label, value, tone }: { icon: typeof ShieldCheck; label: string; value: string; tone: string }) {
  return (
    <div className="rounded-lg border border-border-default bg-white/[0.02] p-3">
      <Icon className={cn("h-3.5 w-3.5", tone)} />
      <p className="mt-1.5 text-[9px] uppercase tracking-wider text-text-muted">{label}</p>
      <p className={cn("mono mt-0.5 text-lg font-semibold", tone)}>{value}</p>
    </div>
  )
}

export const CopilotDataCards = memo(function CopilotDataCards({ data }: { data: unknown }) {
  if (data == null) return null

  const obj = data as Record<string, unknown>

  // Department risk: [{dept, risk, avg}]
  if (isArray(data)) {
    const first = data[0] as Record<string, unknown>
    if (first.dept !== undefined || first.riskIndex !== undefined) {
      const rows = barsFor(data)
      return (
        <Card icon={Building2} title="Department risk exposure" tone="text-status-medium">
          <BarList rows={rows} color="bg-gradient-to-r from-accent-dark to-accent-light" />
        </Card>
      )
    }
    if (first.regulation !== undefined || (first.policyName !== undefined && first.count !== undefined)) {
      const rows = barsFor(data)
      return (
        <Card icon={Gavel} title="Policy trigger frequency" tone="text-status-high">
          <BarList rows={rows} color="bg-status-medium" />
        </Card>
      )
    }
    if (first.category !== undefined) {
      const rows = barsFor(data)
      return (
        <Card icon={Tag} title="Detection categories" tone="text-accent-light">
          <BarList rows={rows} color="bg-gradient-to-r from-status-info to-accent-light" />
        </Card>
      )
    }
    if (first.riskScore !== undefined) {
      return (
        <Card icon={ShieldAlert} title="Highest-risk prompts" tone="text-status-critical">
          <div className="space-y-1.5">
            {(data as unknown[]).slice(0, 5).map((r, i) => {
              const o = r as Record<string, unknown>
              return (
                <div key={i} className="flex items-center gap-2 rounded-lg bg-white/[0.02] px-2.5 py-2">
                  <span className={cn("mono text-[10px] font-semibold", Number(o.riskScore) >= 80 ? "text-status-critical" : "text-status-high")}>
                    {String(o.riskScore)}/100
                  </span>
                  <span className="min-w-0 flex-1 truncate text-[11px] text-text-secondary">{String(o.prompt ?? "").slice(0, 70)}</span>
                  <DecisionBadge decision={String(o.decision ?? "ALLOW")} />
                </div>
              )
            })}
          </div>
        </Card>
      )
    }
    if (first.before !== undefined) {
      return (
        <Card icon={Wand2} title="Rewritten before transmission" tone="text-status-high">
          <div className="space-y-2">
            {(data as unknown[]).map((r, i) => {
              const o = r as Record<string, unknown>
              return (
                <div key={i} className="rounded-lg border border-border-default bg-white/[0.02] p-2.5">
                  <p className="text-[10px] text-text-muted">Before</p>
                  <p className="mt-0.5 line-through decoration-status-critical/60 text-[10px] text-text-secondary">{String(o.before ?? "").slice(0, 80)}</p>
                  <p className="mt-1.5 text-[10px] text-text-muted">After</p>
                  <p className="mt-0.5 text-[10px] text-status-low">{String(o.after ?? "").slice(0, 80)}</p>
                </div>
              )
            })}
          </div>
        </Card>
      )
    }
    return (
      <Card icon={Activity} title="Analysis" tone="text-accent-light">
        <div className="flex flex-wrap gap-1.5">
          {(data as unknown[]).map((r, i) => {
            const o = r as Record<string, unknown>
            const label = String(o.regulation ?? o.category ?? o.dept ?? o.label ?? `item ${i + 1}`)
            const value = Number(o.count ?? o.risk ?? o.riskIndex ?? 0)
            return (
              <span key={i} className="flex items-center gap-1.5 rounded-lg border border-border-default bg-white/[0.02] px-2.5 py-1.5 text-[11px] text-text-secondary">
                {label}
                {value > 0 && <span className="mono text-[10px] text-accent-light">{value}</span>}
              </span>
            )
          })}
        </div>
      </Card>
    )
  }

  // Compare today vs yesterday
  if (obj.today !== undefined && obj.yesterday !== undefined) {
    const t = obj.today as Record<string, number>
    const y = obj.yesterday as Record<string, number>
    const rows: Array<{ label: string; today: number; yesterday: number }> = [
      { label: "Prompts", today: t.total ?? 0, yesterday: y.total ?? 0 },
      { label: "Blocked", today: t.blocked ?? 0, yesterday: y.blocked ?? 0 },
      { label: "Risky (≥35)", today: t.risky ?? 0, yesterday: y.risky ?? 0 },
      { label: "Avg risk", today: t.avg ?? 0, yesterday: y.avg ?? 0 },
    ]
    return (
      <Card icon={Activity} title="Today vs yesterday" tone="text-accent-light">
        <div className="grid grid-cols-2 gap-2">
          {rows.map((r) => {
            const delta = r.today - r.yesterday
            return (
              <div key={r.label} className="rounded-lg border border-border-default bg-white/[0.02] p-3">
                <p className="text-[9px] uppercase tracking-wider text-text-muted">{r.label}</p>
                <p className="mt-1 flex items-center gap-1.5">
                  <span className="mono text-lg font-semibold text-text-primary">{r.today}</span>
                  {delta !== 0 && (
                    <span className={cn("mono flex items-center gap-0.5 text-[10px]", delta > 0 ? "text-status-critical" : "text-status-low")}>
                      {delta > 0 ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
                      {Math.abs(delta)}
                    </span>
                  )}
                </p>
              </div>
            )
          })}
        </div>
      </Card>
    )
  }

  // Posture / executive summary
  if (obj.companyScore !== undefined) {
    const rows: Array<{ icon: typeof ShieldCheck; label: string; value: string; tone: string }> = [
      { icon: ShieldCheck, label: "Security score", value: `${obj.companyScore}/100`, tone: Number(obj.companyScore) >= 85 ? "text-status-low" : "text-status-medium" },
      { icon: ShieldAlert, label: "Blocked", value: String(obj.blocked ?? 0), tone: "text-status-critical" },
      { icon: Wand2, label: "Rewritten", value: String(obj.rewritten ?? 0), tone: "text-status-high" },
      { icon: Landmark, label: "Hotspot dept", value: String((obj.topDept as Record<string, unknown>)?.name ?? "n/a"), tone: "text-accent-light" },
    ]
    return (
      <Card icon={Landmark} title="Executive summary" tone="text-accent-light">
        <div className="grid grid-cols-2 gap-2">
          {rows.map((r) => (
            <KpiCard key={r.label} icon={r.icon} label={r.label} value={r.value} tone={r.tone} />
          ))}
        </div>
      </Card>
    )
  }

  // Why threats increased
  if (obj.riskyWeek !== undefined) {
    return (
      <Card icon={ShieldAlert} title="Threat drivers" tone="text-status-critical">
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
          <KpiCard icon={Activity} label="Risky prompts (7d)" value={String(obj.riskyWeek)} tone="text-status-critical" />
          <KpiCard icon={Tag} label="Top secret type" value={String(obj.topSecret ?? "n/a")} tone="text-status-high" />
          <KpiCard icon={Building2} label="Hotspot dept" value={String(obj.topDept ?? "n/a")} tone="text-status-medium" />
        </div>
      </Card>
    )
  }

  // Generic fallback: render as small JSON-ish chips
  const entries = Object.entries(obj).filter(([, v]) => typeof v === "number" || typeof v === "string")
  if (entries.length > 0) {
    return (
      <Card icon={Activity} title="Key metrics" tone="text-accent-light">
        <div className="flex flex-wrap gap-1.5">
          {entries.map(([k, v]) => (
            <span key={k} className="flex items-center gap-1.5 rounded-lg border border-border-default bg-white/[0.02] px-2.5 py-1.5 text-[11px] text-text-secondary">
              <span className="capitalize text-text-muted">{k.replace(/([A-Z])/g, " $1")}</span>
              <span className="mono text-[10px] text-accent-light">{String(v)}</span>
            </span>
          ))}
        </div>
      </Card>
    )
  }

  return null
})

function Card({ icon: Icon, title, tone, children }: { icon: typeof ShieldCheck; title: string; tone: string; children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-2 rounded-xl border border-border-default bg-bg-secondary/40 p-3.5"
    >
      <p className="mb-2.5 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider">
        <Icon className={cn("h-3 w-3", tone)} /> {title}
      </p>
      {children}
    </motion.div>
  )
}
