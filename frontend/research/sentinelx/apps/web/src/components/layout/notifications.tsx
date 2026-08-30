"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import { AnimatePresence, motion } from "framer-motion"
import { Bell, CheckCheck, ShieldAlert, Sparkles, XCircle, Zap } from "lucide-react"
import { api, timeAgo } from "@/lib/api"
import type { AuditRecord } from "@/types"
import { DecisionBadge } from "@/components/ui/primitives"
import { cn } from "@/lib/utils"

export function NotificationCenter() {
  const [open, setOpen] = useState(false)
  const [events, setEvents] = useState<AuditRecord[]>([])
  const [unread, setUnread] = useState(0)
  const [loading, setLoading] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const d = await api.audit({ limit: 8 })
      setEvents(d.records)
      setUnread(d.records.filter((r) => r.decision !== "ALLOW").length)
    } catch {
      setEvents([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (open) load()
  }, [open, load])

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener("mousedown", handler)
    return () => document.removeEventListener("mousedown", handler)
  }, [])

  const iconFor = (ev: AuditRecord) =>
    ev.decision === "BLOCK" ? (
      <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-critical"><XCircle className="h-3.5 w-3.5 text-status-critical" /></span>
    ) : ev.decision === "REWRITE" ? (
      <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-high"><Zap className="h-3.5 w-3.5 text-status-high" /></span>
    ) : ev.decision === "FLAG" ? (
      <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-medium"><ShieldAlert className="h-3.5 w-3.5 text-status-medium" /></span>
    ) : (
      <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-low"><Sparkles className="h-3.5 w-3.5 text-status-low" /></span>
    )

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="relative flex h-9 w-9 items-center justify-center rounded-lg border border-border-default text-text-muted transition-colors hover:border-border-strong hover:text-text-primary"
        aria-label={unread > 0 ? `Notifications (${unread} unread)` : "Notifications"}
        aria-expanded={open}
      >
        <Bell className="h-4 w-4" />
        {unread > 0 && (
          <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-status-critical px-1 text-[9px] font-bold text-white">
            {unread}
          </span>
        )}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.98 }}
            transition={{ type: "spring", stiffness: 400, damping: 30 }}
            className="absolute right-0 top-12 z-50 w-80 overflow-hidden rounded-2xl border border-border-default bg-bg-secondary shadow-modal"
          >
            <div className="flex items-center justify-between border-b border-border-subtle px-4 py-3">
              <p className="text-xs font-semibold text-text-primary">Notifications</p>
              <button
                onClick={() => setUnread(0)}
                className="flex items-center gap-1 text-[10px] text-text-muted transition-colors hover:text-accent-light"
              >
                <CheckCheck className="h-3 w-3" /> Mark all read
              </button>
            </div>

            <div className="max-h-96 overflow-y-auto" role="log" aria-live="polite">
              {loading && <p className="px-4 py-6 text-center text-xs text-text-muted">Loading…</p>}
              {!loading && events.length === 0 && (
                <p className="px-4 py-8 text-center text-xs text-text-muted">No activity yet</p>
              )}
              {events.map((ev) => (
                <div key={ev.id} className={cn("flex items-start gap-3 border-b border-border-subtle/50 px-4 py-3 last:border-0", ev.decision !== "ALLOW" && "bg-white/[0.01]")}>
                  {iconFor(ev)}
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-xs text-text-primary">{ev.prompt.slice(0, 60)}…</p>
                    <p className="mt-0.5 text-[10px] text-text-muted">
                      {ev.user?.name ?? "Gateway"} · {timeAgo(ev.timestamp)} · risk {ev.riskScore}
                    </p>
                  </div>
                  <DecisionBadge decision={ev.decision} />
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}