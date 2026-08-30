"use client"

import { useEffect, useMemo, useState } from "react"
import { motion } from "framer-motion"
import { CheckCircle2, FileText, Scale } from "lucide-react"
import { api, timeAgo } from "@/lib/api"
import type { AuditRecord, Policy, PolicyViolation, DetectionRule } from "@/types"
import { Badge, PageHeader, SectionTitle, SeverityBadge } from "@/components/ui/primitives"
import { Switch } from "@/components/ui/motion"
import { cn } from "@/lib/utils"

const PROTECTED_FIELDS: Record<string, string[]> = {
  "GDPR": ["Names & emails", "Phone numbers", "Location data", "Device identifiers"],
  "HIPAA": ["Patient identifiers", "Diagnoses", "Prescriptions", "Insurance data"],
  "PCI DSS": ["Card numbers (PAN)", "CVV", "Expiry dates", "Cardholder name"],
  "SOC 2": ["Credentials", "Customer data", "Access tokens", "Config secrets"],
  "ISO 27001": ["API keys", "Private keys", "Passwords", "Connection strings"],
  "ACME-INTERNAL": ["Salary data", "Attorney-client info", "National IDs", "Board materials"],
}

const WEIGHT_LABEL: Record<string, string> = {
  CRITICAL: "Critical",
  HIGH: "High",
  MEDIUM: "Medium",
  LOW: "Low",
  INFO: "Info",
}

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<Policy[]>([])
  const [rules, setRules] = useState<DetectionRule[]>([])
  const [records, setRecords] = useState<AuditRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState<string | null>(null)
  const [toggles, setToggles] = useState<Record<string, boolean>>({})

  useEffect(() => {
    Promise.all([api.policies(), api.rules(), api.audit({ limit: 100 })])
      .then(([p, r, a]) => {
        setPolicies(p)
        setRules(r)
        setRecords(a.records)
        const init: Record<string, boolean> = {}
        for (const pol of p) init[pol.id] = pol.enabled
        setToggles(init)
      })
      .catch(() => undefined)
      .finally(() => setLoading(false))
  }, [])

  const violationsByPolicy = useMemo(() => {
    const map = new Map<string, { count: number; last: string | null }>()
    for (const rec of records) {
      for (const v of (rec.violations ?? []) as PolicyViolation[]) {
        const reg = v.regulation
        const entry = map.get(reg) ?? { count: 0, last: null }
        entry.count++
        if (!entry.last || rec.timestamp > entry.last) entry.last = rec.timestamp
        map.set(reg, entry)
      }
    }
    return map
  }, [records])

  const toggle = (id: string) => {
    setToggles((t) => ({ ...t, [id]: !t[id] }))
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Policy Center"
        description="Regulatory and corporate policy packs enforced on every prompt before it reaches an LLM."
      />

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="glass-card p-5 lg:col-span-2">
          <SectionTitle title="Policy Packs" sub="enforced in order of severity · toggles apply in the live demo" />
          {loading && <p className="py-8 text-center text-sm text-text-muted">Loading policies…</p>}
          <div className="space-y-3">
            {policies.map((p) => {
              const stat = violationsByPolicy.get(p.regulation) ?? { count: 0, last: null }
              return (
                <motion.div
                  key={p.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={cn(
                    "overflow-hidden rounded-xl border bg-white/[0.02] transition-colors",
                    toggles[p.id] === false ? "border-border-subtle opacity-70" : "border-border-default",
                  )}
                >
                  <div className="flex w-full items-center gap-4 px-4 py-3.5">
                    <button onClick={() => setOpen(open === p.id ? null : p.id)} className="flex min-w-0 flex-1 items-center gap-4 text-left hover:bg-white/[0.02]">
                      <div className={cn("flex h-10 w-10 items-center justify-center rounded-lg", p.severity === "CRITICAL" ? "bg-critical" : p.severity === "HIGH" ? "bg-high" : "bg-medium")}>
                        <Scale className={cn("h-4.5 w-4.5", p.severity === "CRITICAL" ? "text-status-critical" : p.severity === "HIGH" ? "text-status-high" : "text-status-medium")} />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-sm font-medium text-text-primary">{p.name}</span>
                          <Badge variant="outline">{p.regulation}</Badge>
                          <Badge variant="outline">{p.category}</Badge>
                        </div>
                        <p className="mt-0.5 line-clamp-1 text-xs text-text-muted">{p.description}</p>
                      </div>
                    </button>
                    <div className="flex items-center gap-3">
                      <div className="hidden text-right sm:block">
                        <p className="text-[10px] text-text-muted">
                          {stat.count > 0 ? `${stat.count} violation${stat.count === 1 ? "" : "s"}` : "no triggers"}
                        </p>
                        <p className="text-[10px] text-text-muted">{stat.last ? `last ${timeAgo(stat.last)}` : `weight ${WEIGHT_LABEL[p.severity]}`}</p>
                      </div>
                      <SeverityBadge severity={p.severity} />
                      <Switch checked={toggles[p.id] !== false} onCheckedChange={() => toggle(p.id)} label={`${p.name} enabled`} />
                    </div>
                  </div>
                  {open === p.id && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      className="overflow-hidden"
                    >
                      <div className="border-t border-border-subtle bg-bg-secondary/50 px-4 py-4">
                        <p className="mb-3 text-xs leading-relaxed text-text-secondary">{p.description}</p>
                        <div className="mb-3 grid gap-4 sm:grid-cols-2">
                          <div>
                            <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-text-muted">Protected fields</p>
                            <div className="flex flex-wrap gap-1.5">
                              {(PROTECTED_FIELDS[p.regulation] ?? []).map((f) => (
                                <span key={f} className="tech-chip !py-1 text-[10px] text-accent-light">{f}</span>
                              ))}
                            </div>
                          </div>
                          <div>
                            <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-text-muted">Enforcement stats</p>
                            <div className="space-y-1 text-[11px] text-text-secondary">
                              <p>Risk weight: <span className="mono text-text-primary">{WEIGHT_LABEL[p.severity]}</span></p>
                              <p>Violations: <span className="mono text-status-critical">{stat.count}</span></p>
                              <p>Last triggered: <span className="mono text-text-primary">{stat.last ? timeAgo(stat.last) : "never"}</span></p>
                              <p>Status: <span className="mono text-status-low">{toggles[p.id] !== false ? "enforced" : "bypassed"}</span></p>
                            </div>
                          </div>
                        </div>
                        <div className="space-y-2">
                          {(p.rules as Array<{ id: string; description: string; severity: string }> | undefined)?.map((r) => (
                            <div key={r.id} className="flex items-start gap-3 rounded-lg border border-border-subtle bg-white/[0.02] px-3 py-2">
                              <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 text-accent-light" />
                              <div className="flex-1">
                                <p className="text-xs text-text-secondary">{r.description}</p>
                                <p className="mono mt-0.5 text-[10px] text-text-muted">{r.id}</p>
                              </div>
                              <SeverityBadge severity={r.severity} />
                            </div>
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  )}
                </motion.div>
              )
            })}
          </div>
        </div>

        <div className="space-y-4">
          <div className="glass-card card-glow p-5">
            <SectionTitle title="Detection Rules" sub={`${rules.length} rules in the signature library`} />
            <div className="max-h-[520px] space-y-1.5 overflow-y-auto pr-1">
              {rules.map((r) => (
                <div key={r.id} className="flex items-center justify-between gap-2 rounded-lg px-2 py-1.5 hover:bg-white/[0.02]">
                  <div className="min-w-0">
                    <p className="truncate text-xs text-text-secondary">{r.name}</p>
                    <p className="mono truncate text-[9px] text-text-muted">{r.category}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="mono text-[9px] text-text-muted">{r.truePositiveCount + r.falsePositiveCount} hits</span>
                    <SeverityBadge severity={r.severity} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-card card-glow p-5">
            <SectionTitle title="Enforcement Flow" />
            <div className="space-y-2 text-xs text-text-secondary">
              {["Prompt received by gateway", "Secret detection (30+ patterns)", "Policy pack evaluation", "Risk scoring", "Decision: allow / rewrite / block", "Audit record committed"].map((s, i) => (
                <div key={i} className="flex items-center gap-2.5">
                  <span className="mono flex h-5 w-5 items-center justify-center rounded-full bg-accent/15 text-[9px] text-accent-light">{i + 1}</span>
                  {s}
                </div>
              ))}
            </div>
            <div className="mt-4 rounded-lg border border-accent/25 bg-accent/5 px-3 py-2.5 text-[11px] leading-relaxed text-text-muted">
              <FileText className="mb-1 h-3.5 w-3.5 text-accent-light" />
              Toggle a pack to simulate bypassing a regulation — policy engine enforcement changes in real time.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
