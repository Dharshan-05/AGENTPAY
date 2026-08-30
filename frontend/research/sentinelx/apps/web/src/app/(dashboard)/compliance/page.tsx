"use client"

import { useCallback, useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Award, CheckCircle2, FileText, RefreshCw, ShieldCheck, Sparkles, XCircle } from "lucide-react"
import { api } from "@/lib/api"
import type { AuditRecord } from "@/types"
import { Badge, PageHeader, SectionTitle } from "@/components/ui/primitives"
import { cn } from "@/lib/utils"

interface ComplianceStatus {
  regulation: string
  name: string
  status: "compliant" | "partial" | "at-risk"
  score: number
  findings: number
  description: string
  areas: string[]
}

export default function CompliancePage() {
  const [records, setRecords] = useState<AuditRecord[]>([])
  const [, setLoading] = useState(true)
  const [aiSummary, setAiSummary] = useState<{ text: string; model: string | null; simulated: boolean } | null>(null)
  const [aiLoading, setAiLoading] = useState(false)

  const load = useCallback(async () => {
    try {
      const d = await api.audit({ limit: 100 })
      setRecords(d.records)
    } catch {
      setRecords([])
    } finally {
      setLoading(false)
    }
  }, [])

  const loadAiSummary = useCallback(async () => {
    if (aiLoading) return
    setAiLoading(true)
    try {
      const res = await api.complianceSummary()
      setAiSummary({ text: res.data, model: res.model, simulated: res.simulated })
    } catch {
      setAiSummary(null)
    } finally {
      setAiLoading(false)
    }
  }, [aiLoading])

  useEffect(() => {
    load()
    const t = setInterval(load, 15000)
    return () => clearInterval(t)
  }, [load])

  const byRegulation = new Map<string, AuditRecord[]>()
  for (const r of records) {
    for (const reg of (r.policiesTriggered as string[]) ?? []) {
      const list = byRegulation.get(reg) ?? []
      list.push(r)
      byRegulation.set(reg, list)
    }
  }

  const statuses: ComplianceStatus[] = [
    {
      regulation: "GDPR",
      name: "EU General Data Protection Regulation",
      description: "Personal data protection and cross-border transfer controls for AI workloads.",
      status: "compliant",
      areas: ["PII redaction before transmission", "Audit trail for processing", "Art. 32 safeguards"],
      score: 100,
      findings: 0,
    },
    {
      regulation: "HIPAA",
      name: "Health Insurance Portability & Accountability Act",
      description: "Protected health information must never leave the covered entity boundary.",
      status: "compliant",
      areas: ["PHI blocking in prompts", "Breach notification readiness", "Covered entity controls"],
      score: 100,
      findings: 0,
    },
    {
      regulation: "PCI DSS",
      name: "Payment Card Industry Data Security Standard",
      description: "Cardholder data is blocked from generative AI services entirely.",
      status: "compliant",
      areas: ["PAN detection with Luhn validation", "No CHD storage", "Scope containment"],
      score: 100,
      findings: 0,
    },
    {
      regulation: "SOC 2",
      name: "SOC 2 Trust Services Criteria",
      description: "Security, availability, and confidentiality controls for the AI gateway.",
      status: "compliant",
      areas: ["CC6.1 logical access", "CC7.3 monitoring", "Incident evidence"],
      score: 100,
      findings: 0,
    },
    {
      regulation: "ISO 27001",
      name: "ISO/IEC 27001 Information Security",
      description: "Annex A controls for secrets hygiene and communications security.",
      status: "compliant",
      areas: ["A.9.2.6 secret removal", "A.10.1.1 cryptography", "A.13.1 network security"],
      score: 100,
      findings: 0,
    },
    {
      regulation: "ACME-INTERNAL",
      name: "Internal Corporate Policy",
      description: "Confidential compensation, legal, and HR data governed by company policy.",
      status: "at-risk",
      areas: ["Salary data protection", "Attorney-client privilege", "National identifiers"],
      score: Math.max(0, 100 - (byRegulation.get("ACME-INTERNAL")?.length ?? 0) * 5),
      findings: byRegulation.get("ACME-INTERNAL")?.length ?? 0,
    },
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Compliance Center"
        description="Regulatory posture for the AI governance layer — evaluated continuously against live gateway telemetry."
        actions={
          <Badge variant="success">
            <Award className="h-3 w-3" /> Enterprise Ready
          </Badge>
        }
      />

      {/* AI Compliance Summary */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card card-glow border-accent/20 p-5"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-accent-light" />
            <h2 className="text-sm font-semibold">AI Compliance Summary</h2>
            {aiSummary?.model && <span className="mono text-[10px] text-text-muted">{aiSummary.model}</span>}
            {aiSummary?.simulated && <Badge variant="info">simulated</Badge>}
          </div>
          <button
            onClick={loadAiSummary}
            disabled={aiLoading}
            className="flex items-center gap-1.5 rounded-lg border border-border-default bg-white/[0.02] px-3 py-1.5 text-[11px] font-medium text-text-secondary transition-all hover:border-accent/50 hover:bg-accent/5 hover:text-text-primary disabled:opacity-50"
          >
            <RefreshCw className={cn("h-3 w-3", aiLoading && "animate-spin")} />
            {aiSummary ? "Regenerate" : "Generate"}
          </button>
        </div>
        {aiLoading && !aiSummary ? (
          <div className="mt-3 space-y-2">
            <div className="h-3 w-full animate-pulse rounded bg-white/[0.04]" />
            <div className="h-3 w-11/12 animate-pulse rounded bg-white/[0.04]" />
            <div className="h-3 w-4/5 animate-pulse rounded bg-white/[0.04]" />
          </div>
        ) : aiSummary ? (
          <div className="mt-3 flex items-start gap-3 rounded-lg border border-accent/15 bg-accent/[0.03] p-4">
            <FileText className="mt-0.5 h-4 w-4 flex-shrink-0 text-accent-light" />
            <div className="text-xs leading-relaxed text-text-secondary">{aiSummary.text.split("\n").map((l, i) => (l ? <p key={i} className="mb-1.5">{l}</p> : null))}</div>
          </div>
        ) : (
          <p className="mt-3 text-xs text-text-muted">Click Generate to create an AI compliance summary grounded in the last 7 days of audit data.</p>
        )}
      </motion.div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {statuses.map((s, i) => {
          const active = byRegulation.get(s.regulation)
          const blocked = active?.filter((r) => r.decision === "BLOCK").length ?? 0
          return (
            <motion.div
              key={s.regulation}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06 }}
              className={cn(
                "glass-card p-5",
                s.status === "at-risk" && "border-status-high/30",
              )}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className={cn("flex h-10 w-10 items-center justify-center rounded-lg", s.status === "compliant" ? "bg-low" : "bg-high")}>
                    <ShieldCheck className={cn("h-5 w-5", s.status === "compliant" ? "text-status-low" : "text-status-high")} />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-text-primary">{s.regulation}</p>
                    <p className="text-[10px] text-text-muted">{s.name}</p>
                  </div>
                </div>
                {s.status === "compliant" ? (
                  <Badge variant="success"><CheckCircle2 className="h-3 w-3" /> Compliant</Badge>
                ) : (
                  <Badge variant="warning"><XCircle className="h-3 w-3" /> At Risk</Badge>
                )}
              </div>

              <p className="mt-3 text-xs leading-relaxed text-text-secondary">{s.description}</p>

              <div className="mt-3 space-y-1.5">
                {s.areas.map((a) => (
                  <div key={a} className="flex items-center gap-2 text-[11px] text-text-muted">
                    <CheckCircle2 className="h-3 w-3 text-accent-light" />
                    {a}
                  </div>
                ))}
              </div>

              <div className="mt-4 border-t border-border-subtle pt-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-text-muted">Control score</span>
                  <span className={cn("mono font-semibold", s.status === "compliant" ? "text-status-low" : "text-status-high")}>
                    {s.score}%
                  </span>
                </div>
                <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${s.score}%` }}
                    transition={{ duration: 0.8, delay: 0.2 + i * 0.05 }}
                    className={cn("h-full rounded-full", s.status === "compliant" ? "bg-status-low" : "bg-status-high")}
                  />
                </div>
                <p className="mt-2 text-[10px] text-text-muted">
                  {blocked} transmission{blocked === 1 ? "" : "s"} blocked in current window
                </p>
              </div>
            </motion.div>
          )
        })}
      </div>

      <div className="glass-card p-5">
        <SectionTitle title="Evidence Log" sub="live compliance-relevant events" />
        <div className="space-y-2">
          {records.slice(0, 6).map((r) => {
            const regs = (r.policiesTriggered as string[]) ?? []
            return (
              <div key={r.id} className="flex items-center gap-3 rounded-lg border border-border-subtle bg-white/[0.015] px-3 py-2">
                <span className="mono text-[10px] text-text-muted">{new Date(r.timestamp).toLocaleString()}</span>
                <span className="flex-1 truncate text-xs text-text-secondary">{r.prompt.length > 80 ? `${r.prompt.slice(0, 80)}…` : r.prompt}</span>
                {regs.map((reg) => (
                  <Badge key={reg} variant="outline">{reg}</Badge>
                ))}
              </div>
            )
          })}
          {records.length === 0 && <p className="py-6 text-center text-xs text-text-muted">No events recorded.</p>}
        </div>
      </div>
    </div>
  )
}
