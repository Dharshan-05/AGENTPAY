"use client"

import { useEffect, useState } from "react"
import { Activity, Cpu, Globe, HardDrive, Radio, Server, Timer, Zap } from "lucide-react"
import { cn } from "@/lib/utils"
import { api } from "@/lib/api"
import type { SystemStats } from "@/types"

interface StatusItem {
  label: string
  value: string
  ok: boolean
}

export function StatusBar() {
  const [items, setItems] = useState<StatusItem[]>([
    { label: "gateway", value: "connected", ok: true },
    { label: "postgres", value: "standby", ok: true },
    { label: "redis", value: "standby", ok: true },
    { label: "ws-bridge", value: "connected", ok: true },
  ])
  const [sys, setSys] = useState<SystemStats | null>(null)

  useEffect(() => {
    let cancelled = false
    const check = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3001"}/api/health`,
          { cache: "no-store" },
        )
        const data = await res.json()
        if (!cancelled) {
          setItems(() => [
            { label: "gateway", value: data.status ?? "ok", ok: true },
            { label: "postgres", value: "standby", ok: true },
            { label: "redis", value: "standby", ok: true },
            { label: "ws-bridge", value: "connected", ok: true },
          ])
        }
      } catch {
        if (!cancelled) {
          setItems((prev) => prev.map((it) => ({ ...it, ok: false, value: "offline" })))
        }
      }
    }
    check()
    const t = setInterval(check, 15000)
    return () => {
      cancelled = true
      clearInterval(t)
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      try {
        const d = await api.system()
        if (!cancelled) setSys(d)
      } catch {
        // ignore — status bar stays static
      }
    }
    load()
    const t = setInterval(load, 8000)
    return () => {
      cancelled = true
      clearInterval(t)
    }
  }, [])

  return (
    <footer className="fixed bottom-0 left-0 right-0 z-30 flex h-9 items-center justify-between gap-4 border-t border-border-subtle bg-bg-primary/90 px-6 backdrop-blur-xl">
      <div className="flex min-w-0 items-center gap-3 lg:gap-4">
        {items.map((item) => (
          <div key={item.label} className="flex shrink-0 items-center gap-1.5">
            <span
              className={cn(
                "h-1.5 w-1.5 rounded-full",
                item.ok ? "bg-status-low" : "bg-status-critical",
                item.ok && "pulse-dot",
              )}
            />
            <span className="mono text-[10px] text-text-muted">{item.label}</span>
            <span className={cn("mono text-[10px]", item.ok ? "text-text-secondary" : "text-status-critical")}>
              {item.value}
            </span>
          </div>
        ))}
      </div>
      <div className="flex min-w-0 items-center gap-3 overflow-x-auto no-scrollbar lg:gap-4">
        {sys && (
          <>
            <div className="flex shrink-0 items-center gap-1.5">
              <Timer className="h-3 w-3 text-text-muted" />
              <span className="mono text-[10px] text-text-secondary">api {sys.apiLatency}ms</span>
            </div>
            <div className="hidden shrink-0 items-center gap-1.5 xl:flex">
              <Cpu className="h-3 w-3 text-text-muted" />
              <span className="mono text-[10px] text-text-secondary">cpu {sys.cpuPct}%</span>
            </div>
            <div className="hidden shrink-0 items-center gap-1.5 xl:flex">
              <HardDrive className="h-3 w-3 text-text-muted" />
              <span className="mono text-[10px] text-text-secondary">mem {Math.round((sys.memoryMb / sys.memoryTotalMb) * 100)}%</span>
            </div>
            <div className="hidden shrink-0 items-center gap-1.5 xl:flex">
              <Server className="h-3 w-3 text-text-muted" />
              <span className="mono text-[10px] text-text-secondary">{sys.cluster.nodes} nodes</span>
            </div>
            <div className="hidden shrink-0 items-center gap-1.5 xl:flex">
              <Radio className="h-3 w-3 text-text-muted" />
              <span className="mono text-[10px] text-text-secondary">feed {sys.threatFeed}</span>
            </div>
          </>
        )}
        <div className="flex shrink-0 items-center gap-1.5">
          <Activity className="h-3 w-3 text-text-muted" />
          <span className="mono text-[10px] text-text-secondary">8 agents · healthy</span>
        </div>
        <div className="flex shrink-0 items-center gap-1.5">
          <Globe className="h-3 w-3 text-text-muted" />
          <span className="mono text-[10px] text-text-secondary">SentinelX v1.0.0</span>
        </div>
        <div className="hidden shrink-0 items-center gap-1.5 lg:flex">
          <Zap className="h-3 w-3 text-text-muted" />
          <span className="mono text-[10px] text-text-secondary">{sys ? `deploy ${sys.deployment}` : "vCPU 2 · RAM 4GB"}</span>
        </div>
      </div>
    </footer>
  )
}
