"use client"

import { useCallback, useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Activity, ExternalLink, Filter } from "lucide-react"
import { api, timeAgo, DECISION_COLORS } from "@/lib/api"
import type { AuditRecord } from "@/types"
import { Badge, DecisionBadge, PageHeader } from "@/components/ui/primitives"
import { cn } from "@/lib/utils"
import Link from "next/link"

export default function ActivityPage() {
  const [events, setEvents] = useState<AuditRecord[]>([])
  const [filter, setFilter] = useState<string>("ALL")
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    try {
      const d = await api.audit({ limit: 30 })
      setEvents(d.records)
    } catch {
      setEvents([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
    const t = setInterval(load, 6000)
    return () => clearInterval(t)
  }, [load])

  const filtered = filter === "ALL" ? events : events.filter((e) => e.decision === filter)

  return (
    <div className="space-y-6">
      <PageHeader
        title="Live Activity"
        description="Every gateway event as it happens — prompt submissions, detections, decisions, and model routing."
        actions={
          <div className="flex items-center gap-1.5">
            <Filter className="h-3.5 w-3.5 text-text-muted" />
            {["ALL", "ALLOW", "BLOCK", "REWRITE", "FLAG"].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={cn(
                  "rounded-full border px-3 py-1 text-[10px] font-medium uppercase tracking-wider transition-colors",
                  filter === f
                    ? "border-accent bg-accent/15 text-accent-light"
                    : "border-border-default text-text-muted hover:text-text-secondary",
                )}
              >
                {f}
              </button>
            ))}
          </div>
        }
      />

      <div className="space-y-2">
        {loading && <p className="py-12 text-center text-sm text-text-muted">Streaming events…</p>}
        {!loading && filtered.length === 0 && (
          <p className="py-12 text-center text-sm text-text-muted">No events match this filter.</p>
        )}
        {filtered.map((ev, i) => (
          <motion.div
            key={ev.id}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: Math.min(i * 0.03, 0.5) }}
            className="flex items-start gap-4 rounded-xl border border-border-subtle bg-white/[0.015] px-4 py-3"
          >
            <span className={cn("mt-1 h-2 w-2 flex-shrink-0 rounded-full", DECISION_COLORS[ev.decision], i < 4 && "pulse-dot")} />
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <p className="text-xs font-medium text-text-primary">{ev.prompt.length > 120 ? `${ev.prompt.slice(0, 120)}…` : ev.prompt}</p>
              </div>
              <div className="mt-1 flex flex-wrap items-center gap-2 text-[11px] text-text-muted">
                <span className="flex items-center gap-1">
                  <Activity className="h-3 w-3" />
                  {ev.user?.name ?? "Gateway"}
                </span>
                <span>·</span>
                <span>{timeAgo(ev.timestamp)}</span>
                <span>·</span>
                <span className="mono">{ev.llmProvider} / {ev.llmModel}</span>
                <span>·</span>
                <span className="mono">risk {ev.riskScore}</span>
                {ev.rewrittenPrompt && (
                  <Badge variant="warning" className="ml-1">sanitized</Badge>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <DecisionBadge decision={ev.decision} />
              <Link
                href={`/incidents/${ev.id}`}
                className="flex items-center gap-1 rounded-md border border-border-default px-2 py-1 text-[10px] font-medium text-accent-light transition-all hover:border-accent/50 hover:bg-accent/10"
              >
                Investigate <ExternalLink className="h-2.5 w-2.5" />
              </Link>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
