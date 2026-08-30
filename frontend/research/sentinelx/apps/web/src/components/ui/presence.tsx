"use client"

import { useCallback, useEffect, useState } from "react"
import { motion } from "framer-motion"
import { io } from "socket.io-client"
import { Radio, Users } from "lucide-react"
import { api } from "@/lib/api"
import type { AnalystPresence } from "@/types"
import { Badge } from "./primitives"
import { cn } from "@/lib/utils"

const STATUS_TONE: Record<string, string> = {
  ONLINE: "bg-status-low",
  AWAY: "bg-status-medium",
  OFFLINE: "bg-text-muted",
}

export function PresencePanel() {
  const [analysts, setAnalysts] = useState<AnalystPresence[]>([])
  const [connected, setConnected] = useState(false)

  const apply = useCallback((list: AnalystPresence[]) => {
    setAnalysts(list)
  }, [])

  useEffect(() => {
    api.presence().then(apply).catch(() => {})
    const t = setInterval(() => api.presence().then(apply).catch(() => {}), 20000)
    return () => clearInterval(t)
  }, [apply])

  useEffect(() => {
    const socket = io(process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3001")
    socket.on("connect", () => setConnected(true))
    socket.on("presence:update", apply)
    socket.on("disconnect", () => setConnected(false))
    return () => {
      socket.disconnect()
    }
  }, [apply])

  const online = analysts.filter((a) => a.status === "ONLINE").length

  return (
    <div className="glass-card card-glow p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="flex items-center gap-2 text-sm font-semibold">
          <Users className="h-4 w-4 text-accent-light" /> Active Analysts
        </h3>
        <div className="flex items-center gap-2">
          <span className={cn("flex items-center gap-1.5 text-[10px]", connected ? "text-status-low" : "text-text-muted")}>
            <Radio className={cn("h-3 w-3", connected && "pulse-dot")} />
            {connected ? "live presence" : "polling"}
          </span>
          <Badge variant="success">{online} online</Badge>
        </div>
      </div>
      <div className="space-y-2">
        {analysts.map((a, i) => (
          <motion.div
            key={a.id}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.04 }}
            className="flex items-center gap-3 rounded-lg border border-border-default bg-white/[0.02] p-2.5"
          >
            <span className="relative flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-white/[0.04] text-xs">
              {a.emoji ?? a.name.slice(0, 2).toUpperCase()}
              <span className={cn("absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full border-2 border-bg-primary", STATUS_TONE[a.status] ?? "bg-text-muted")} />
            </span>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <p className="truncate text-xs font-medium text-text-primary">{a.name}</p>
                {a.incident && (
                  <span className="mono rounded bg-status-critical/10 px-1.5 py-0.5 text-[8px] text-status-critical">{a.incident}</span>
                )}
              </div>
              <p className="text-[10px] text-text-muted">{a.role} · {a.location} · {a.team}</p>
            </div>
            <span className={cn("text-[9px] font-semibold uppercase tracking-wider", a.status === "ONLINE" ? "text-status-low" : a.status === "AWAY" ? "text-status-medium" : "text-text-muted")}>
              {a.status}
            </span>
          </motion.div>
        ))}
        {analysts.length === 0 && <p className="py-4 text-center text-xs text-text-muted">No analysts connected</p>}
      </div>
    </div>
  )
}
