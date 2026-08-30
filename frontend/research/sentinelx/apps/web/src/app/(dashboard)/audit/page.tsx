"use client"

import { useCallback, useEffect, useState } from "react"
import { motion } from "framer-motion"
import { ChevronLeft, ChevronRight, ClipboardCheck, Download, ExternalLink, FileSearch, X } from "lucide-react"
import { api, formatDate, timeAgo, THREAT_COLORS } from "@/lib/api"
import type { AuditRecord, DetectedSecret } from "@/types"
import { Badge, DecisionBadge, PageHeader, RiskGauge, SeverityBadge } from "@/components/ui/primitives"
import { cn } from "@/lib/utils"
import Link from "next/link"

export default function AuditPage() {
  const [records, setRecords] = useState<AuditRecord[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState("")
  const [selected, setSelected] = useState<AuditRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const pageSize = 20

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const d = await api.audit({ page, limit: pageSize, search: search || undefined })
      setRecords(d.records)
      setTotal(d.total)
    } catch {
      setRecords([])
    } finally {
      setLoading(false)
    }
  }, [page, search])

  useEffect(() => {
    const t = setTimeout(load, search ? 350 : 0)
    return () => clearTimeout(t)
  }, [load, search])

  const exportJson = () => {
    const blob = new Blob([JSON.stringify(records, null, 2)], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `sentinelx-audit-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }

  const pages = Math.max(1, Math.ceil(total / pageSize))

  return (
    <div className="space-y-6">
      <PageHeader
        title="Audit Logs"
        description="Tamper-evident record of every prompt, detection, policy decision, and model interaction — SHA-256 hashed and immutable."
        actions={
          <button onClick={exportJson} className="tech-chip cursor-pointer hover:border-accent">
            <Download className="h-3 w-3" /> Export JSON
          </button>
        }
      />

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="relative">
          <FileSearch className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-text-muted" />
          <input
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            aria-label="Search prompts"
            placeholder="Search prompts…"
            className="w-72 rounded-lg border border-border-default bg-bg-tertiary py-2 pl-9 pr-3 text-xs text-text-primary outline-none transition-colors placeholder:text-text-muted focus:border-accent"
          />
        </div>
        <div className="flex items-center gap-2 text-[11px] text-text-muted">
          <span className="mono">{total} records</span>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="flex h-7 w-7 items-center justify-center rounded-lg border border-border-default transition-colors hover:border-border-strong disabled:opacity-30"
            >
              <ChevronLeft className="h-3.5 w-3.5" />
            </button>
            <span className="mono px-2">{page} / {pages}</span>
            <button
              onClick={() => setPage((p) => Math.min(pages, p + 1))}
              disabled={page >= pages}
              className="flex h-7 w-7 items-center justify-center rounded-lg border border-border-default transition-colors hover:border-border-strong disabled:opacity-30"
            >
              <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>

      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-border-subtle bg-white/[0.02] text-[10px] uppercase tracking-wider text-text-muted">
                <th className="px-4 py-3 font-medium">Timestamp</th>
                <th className="px-4 py-3 font-medium">User</th>
                <th className="px-4 py-3 font-medium">Prompt Hash</th>
                <th className="px-4 py-3 font-medium">Prompt</th>
                <th className="px-4 py-3 font-medium">Risk</th>
                <th className="px-4 py-3 font-medium">Policies</th>
                <th className="px-4 py-3 font-medium">Model</th>
                <th className="px-4 py-3 font-medium">Decision</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td colSpan={8} className="py-10 text-center text-xs text-text-muted">Loading audit records…</td>
                </tr>
              )}
              {!loading && records.length === 0 && (
                <tr>
                  <td colSpan={8} className="py-10 text-center text-xs text-text-muted">No audit records found.</td>
                </tr>
              )}
              {records.map((r, i) => (
                <motion.tr
                  key={r.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: Math.min(i * 0.02, 0.4) }}
                  onClick={() => setSelected(r)}
                  className="cursor-pointer border-b border-border-subtle/50 transition-colors last:border-0 hover:bg-white/[0.02]"
                >
                  <td className="mono whitespace-nowrap px-4 py-3 text-[11px] text-text-muted">{timeAgo(r.timestamp)}</td>
                  <td className="px-4 py-3">
                    <span className="flex items-center gap-2 text-xs text-text-secondary">
                      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-accent/15 text-[9px] font-semibold text-accent-light">
                        {(r.user?.name ?? "S").slice(0, 2).toUpperCase()}
                      </span>
                      {r.user?.name ?? "Unknown"}
                    </span>
                  </td>
                  <td className="mono px-4 py-3 text-[10px] text-text-muted">{r.promptHash}</td>
                  <td className="max-w-[220px] truncate px-4 py-3 text-xs text-text-secondary">{r.prompt}</td>
                  <td className={cn("mono px-4 py-3 text-xs font-semibold", THREAT_COLORS[r.threatLevel])}>{r.riskScore}</td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {(r.policiesTriggered as string[])?.slice(0, 2).map((p, j) => (
                        <span key={j} className="tech-chip !px-1.5 !py-0 !text-[9px]">{p}</span>
                      ))}
                    </div>
                  </td>
                  <td className="mono px-4 py-3 text-[10px] text-text-muted">{r.llmProvider}</td>
                  <td className="px-4 py-3"><DecisionBadge decision={r.decision} /></td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selected && <AuditDetail record={selected} onClose={() => setSelected(null)} />}
    </div>
  )
}

function AuditDetail({ record, onClose }: { record: AuditRecord; onClose: () => void }) {
  const secrets = (record.secrets ?? []) as DetectedSecret[]
  const violations = (record.violations ?? []) as Array<{ policyName: string; regulation: string; severity: string; reason: string; recommendation: string }>

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed inset-0 z-50 flex items-start justify-end bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <motion.div
        initial={{ x: 60, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        className="h-full w-full max-w-xl overflow-y-auto border-l border-border-default bg-bg-primary p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-6 flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/15">
              <ClipboardCheck className="h-5 w-5 text-accent-light" />
            </div>
            <div>
              <h2 className="text-sm font-semibold">Audit Record</h2>
              <p className="mono text-[10px] text-text-muted">{record.id}</p>
            </div>
          </div>
          <button onClick={onClose} className="flex h-8 w-8 items-center justify-center rounded-lg text-text-muted hover:bg-white/[0.04] hover:text-text-primary">
            <X className="h-4 w-4" />
          </button>
        </div>

        <Link
          href={`/incidents/${record.id}`}
          className="mb-6 flex items-center gap-2 rounded-xl border border-accent/30 bg-accent/10 px-4 py-3 text-xs font-medium text-accent-light transition-all hover:bg-accent/15 hover:shadow-glow"
        >
          <ExternalLink className="h-3.5 w-3.5" />
          Open full incident investigation
        </Link>

        <div className="mb-6 flex items-center gap-6 rounded-xl border border-border-default bg-white/[0.02] p-4">
          <RiskGauge score={record.riskScore} />
          <div className="space-y-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className="text-text-muted">Decision</span>
              <DecisionBadge decision={record.decision} />
            </div>
            <p className="text-text-muted">Recorded <span className="text-text-primary">{formatDate(record.timestamp)}</span> · {timeAgo(record.timestamp)}</p>
            <p className="text-text-muted">Gateway <span className="mono text-text-primary">{record.llmProvider} / {record.llmModel}</span></p>
            <p className="text-text-muted">Prompt hash <span className="mono text-accent-light">{record.promptHash}</span></p>
          </div>
        </div>

        <div className="mb-5">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-text-muted">Original Prompt</h3>
          <div className="rounded-xl border border-border-default bg-white/[0.02] p-4 text-xs leading-relaxed text-text-secondary">
            {record.prompt}
          </div>
        </div>

        {record.rewrittenPrompt && (
          <div className="mb-5">
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-text-muted">Rewritten Prompt</h3>
            <div className="rounded-xl border border-accent/25 bg-accent/5 p-4 text-xs leading-relaxed text-text-primary">
              {record.rewrittenPrompt}
            </div>
          </div>
        )}

        {secrets.length > 0 && (
          <div className="mb-5">
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-text-muted">Detected Secrets ({secrets.length})</h3>
            <div className="space-y-2">
              {secrets.map((s, i) => (
                <div key={i} className="flex items-center justify-between gap-3 rounded-lg border border-border-subtle bg-white/[0.02] px-3 py-2">
                  <div className="flex items-center gap-2">
                    <SeverityBadge severity={s.severity} />
                    <span className="text-xs text-text-secondary">{s.label}</span>
                  </div>
                  <span className="mono max-w-[200px] truncate text-[10px] text-status-critical">{s.match}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {violations.length > 0 && (
          <div className="mb-5">
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-text-muted">Policy Violations ({violations.length})</h3>
            <div className="space-y-2">
              {violations.map((v, i) => (
                <div key={i} className="rounded-lg border border-border-subtle bg-white/[0.02] p-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-text-primary">{v.policyName}</span>
                    <Badge variant="outline">{v.regulation}</Badge>
                  </div>
                  <p className="mt-1.5 text-[11px] leading-relaxed text-text-secondary">{v.reason}</p>
                  <p className="mt-1 text-[11px] text-accent-light">→ {v.recommendation}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        <div>
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-text-muted">Agent Trace</h3>
          <div className="space-y-1">
            {(record as unknown as { agentTrace?: Array<{ agent: string; status: string; executionTimeMs: number }> }).agentTrace?.map((t, i) => (
              <div key={i} className="flex items-center justify-between rounded px-2 py-1 text-[11px]">
                <span className="text-text-secondary">{t.agent}</span>
                <span className="flex items-center gap-2">
                  <span className="mono text-text-muted">{t.executionTimeMs}ms</span>
                  <Badge variant={t.status === "COMPLETED" ? "success" : "outline"}>{t.status}</Badge>
                </span>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
