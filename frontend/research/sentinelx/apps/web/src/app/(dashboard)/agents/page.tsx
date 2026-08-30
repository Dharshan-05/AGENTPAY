"use client"

import { useCallback, useEffect, useMemo, useState } from "react"
import { motion } from "framer-motion"
import { Activity, Bot, CheckCircle2, Clock, Cpu, HeartPulse, RefreshCw } from "lucide-react"
import { api } from "@/lib/api"
import type { AgentHealth } from "@/types"
import { Badge, PageHeader } from "@/components/ui/primitives"
import { CountUp } from "@/components/ui/motion"
import { cn } from "@/lib/utils"

const PIPELINE_ORDER = [
  "inspector-agent",
  "secret-detection-agent",
  "policy-engine",
  "risk-engine",
  "prompt-rewriter",
  "llm-adapter",
  "audit-logger",
  "memory-agent",
]

export default function AgentsPage() {
  const [agents, setAgents] = useState<AgentHealth[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<string | null>("risk-engine")
  const [beat, setBeat] = useState(0)

  const load = useCallback(async () => {
    try {
      const d = await api.agents()
      setAgents(d)
    } catch {
      setAgents([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
    const t = setInterval(load, 5000)
    return () => clearInterval(t)
  }, [load])

  useEffect(() => {
    const t = setInterval(() => setBeat((b) => b + 1), 2000)
    return () => clearInterval(t)
  }, [])

  const sorted = useMemo(
    () => [...agents].sort((a, b) => PIPELINE_ORDER.indexOf(a.id) - PIPELINE_ORDER.indexOf(b.id)),
    [agents],
  )
  const active = agents.find((a) => a.id === selected) ?? agents[0]
  const avgLatency = agents.length ? Math.round(agents.reduce((acc, a) => acc + a.responseTime, 0) / agents.length) : 0

  return (
    <div className="space-y-6">
      <PageHeader
        title="Agent Monitor"
        description="The eight agents that inspect every prompt — responsibilities, latency, throughput, and pipeline order."
        actions={
          <button onClick={load} className="tech-chip cursor-pointer hover:border-accent">
            <RefreshCw className="h-3 w-3" /> Refresh
          </button>
        }
      />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { label: "Agents online", value: agents.filter((a) => a.status === "HEALTHY").length, suffix: "", cls: "text-status-low", icon: HeartPulse },
          { label: "Avg latency", value: avgLatency, suffix: "ms", cls: "text-accent-light", icon: Clock },
          { label: "Prompts processed", value: agents.reduce((acc, a) => acc + (a.processed ?? 0), 0), suffix: "", cls: "text-text-primary", icon: Activity },
          { label: "Success rate", value: agents.length ? agents.reduce((acc, a) => acc + a.successRate, 0) / agents.length : 0, suffix: "%", decimals: 1, cls: "text-status-low", icon: CheckCircle2 },
        ].map((s) => (
          <div key={s.label} className="glass-card card-glow p-4">
            <div className="flex items-center gap-1.5 text-[11px] uppercase tracking-wider text-text-muted">
              <s.icon className="h-3 w-3" /> {s.label}
            </div>
            <p className={cn("mono mt-1.5 text-2xl font-semibold", s.cls)}>
              <CountUp value={s.value} decimals={s.decimals ?? 0} />{s.suffix}
            </p>
          </div>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        <div className="space-y-2 lg:col-span-2">
          {loading && <p className="py-10 text-center text-sm text-text-muted">Loading agents…</p>}
          {sorted.map((agent, i) => (
            <motion.button
              key={agent.id}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              onClick={() => setSelected(agent.id)}
              className={cn(
                "w-full rounded-xl border p-3.5 text-left transition-all",
                selected === agent.id
                  ? "border-accent/40 bg-accent/5 shadow-glow"
                  : "border-border-default bg-white/[0.02] hover:border-border-strong",
              )}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/15">
                    <Bot className="h-4 w-4 text-accent-light" />
                  </div>
                  <div>
                    <p className="text-xs font-medium text-text-primary">{agent.name}</p>
                    <p className="text-[10px] text-text-muted">#{i + 1} in pipeline</p>
                  </div>
                </div>
                <span className="flex items-center gap-1.5 text-[10px] text-status-low">
                  <span className="h-1.5 w-1.5 rounded-full bg-status-low heartbeat" />
                  {agent.status}
                </span>
              </div>
              <div className="mono mt-2 flex items-center gap-3 text-[10px] text-text-muted">
                <span>{agent.responseTime}ms</span>
                <span>·</span>
                <span>{agent.successRate}% success</span>
                <span>·</span>
                <span>{agent.memoryMb}MB</span>
              </div>
            </motion.button>
          ))}
        </div>

        <div className="glass-card p-6 lg:col-span-3">
          {active && (
            <>
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    <div className="relative flex h-12 w-12 items-center justify-center rounded-xl bg-accent/15">
                      <Cpu className="h-6 w-6 text-accent-light" />
                      <span className={cn("absolute -right-1 -top-1 flex h-3 w-3", beat % 2 === 0 && "animate-ping")}>
                        <span className="h-3 w-3 rounded-full bg-status-low" />
                      </span>
                    </div>
                    <div>
                      <h2 className="text-base font-semibold text-text-primary">{active.name}</h2>
                      <Badge variant="success">HEALTHY</Badge>
                    </div>
                  </div>
                  <p className="mt-4 max-w-md text-sm leading-relaxed text-text-secondary">{active.responsibility}</p>
                </div>
                <div className="text-right">
                  <p className="mono text-2xl font-semibold text-accent-light">{active.responseTime}ms</p>
                  <p className="text-[10px] uppercase tracking-wider text-text-muted">avg response</p>
                </div>
              </div>

              <div className="mt-6 grid grid-cols-3 gap-3">
                {[
                  { label: "Processed", value: active.processed?.toLocaleString() ?? "—", icon: Activity, cls: "text-text-primary" },
                  { label: "Success rate", value: `${active.successRate}%`, icon: CheckCircle2, cls: "text-status-low" },
                  { label: "Memory", value: `${active.memoryMb}MB`, icon: Cpu, cls: "text-accent-light" },
                ].map((m) => (
                  <div key={m.label} className="rounded-xl border border-border-subtle bg-white/[0.02] p-4">
                    <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-text-muted">
                      <m.icon className="h-3 w-3" /> {m.label}
                    </div>
                    <p className={cn("mono mt-1.5 text-lg font-semibold", m.cls)}>{m.value}</p>
                  </div>
                ))}
              </div>

              <div className="mt-4 rounded-lg border border-border-default bg-white/[0.02] px-4 py-2.5">
                <p className="text-[10px] uppercase tracking-wider text-text-muted">Current task</p>
                <p className="mt-1 flex items-center gap-2 text-xs text-text-secondary">
                  <span className="h-1.5 w-1.5 rounded-full bg-accent-light pulse-dot" />
                  {active.currentTask}
                </p>
              </div>

              <div className="mt-6">
                <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-text-muted">Pipeline position</p>
                <div className="flex flex-wrap items-center gap-1.5">
                  {sorted.map((a, i) => (
                    <div key={a.id} className="flex items-center gap-1.5">
                      <span
                        onClick={() => setSelected(a.id)}
                        className={cn(
                          "cursor-pointer rounded-lg border px-2.5 py-1.5 text-[10px] font-medium transition-colors",
                          a.id === active.id
                            ? "border-accent bg-accent/15 text-accent-light"
                            : "border-border-default text-text-muted hover:border-border-strong hover:text-text-secondary",
                        )}
                      >
                        {a.name.replace(/-/g, " ")}
                      </span>
                      {i < sorted.length - 1 && <span className="text-text-muted/40">→</span>}
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
