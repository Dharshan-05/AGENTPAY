"use client"

import { useRef, useState } from "react"
import Link from "next/link"
import {
  ArrowRight,
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  Database,
  Eye,
  FileText,
  Loader2,
  LucideIcon,
  Router,
  ScanSearch,
  Shield,
  ShieldAlert,
  ShieldCheck,

  User,
  Zap,
} from "lucide-react"
import { cn } from "@/lib/utils"

interface PipelineStage {
  id: string
  name: string
  icon: LucideIcon
  color: string
  description: string
  status: "idle" | "active" | "completed" | "triggered"
  metrics?: {
    latency: number
    confidence: number
    entities: number
  }
}

const PIPELINE_STAGES: PipelineStage[] = [
  {
    id: "user",
    name: "User",
    icon: User,
    color: "text-blue-400",
    description: "User submits prompt",
    status: "completed",
  },
  {
    id: "inspector",
    name: "Inspector",
    icon: ScanSearch,
    color: "text-purple-400",
    description: "Prompt normalisation & intent classification",
    status: "idle",
    metrics: { latency: 8, confidence: 99.2, entities: 0 },
  },
  {
    id: "detection",
    name: "Secret Detection",
    icon: ShieldAlert,
    color: "text-red-400",
    description: "30+ pattern rules for secrets, PII & credentials",
    status: "idle",
    metrics: { latency: 24, confidence: 99.4, entities: 0 },
  },
  {
    id: "policy",
    name: "Policy Engine",
    icon: ShieldCheck,
    color: "text-amber-400",
    description: "Regulatory enforcement (GDPR · HIPAA · PCI · SOC 2 · ISO)",
    status: "idle",
    metrics: { latency: 12, confidence: 99.9, entities: 0 },
  },
  {
    id: "risk",
    name: "Risk Engine",
    icon: Zap,
    color: "text-orange-400",
    description: "Composite risk scoring & decision recommendation",
    status: "idle",
    metrics: { latency: 18, confidence: 99.7, entities: 0 },
  },
  {
    id: "rewriter",
    name: "Prompt Rewriter",
    icon: FileText,
    color: "text-green-400",
    description: "Intent-preserving sanitisation & redaction",
    status: "idle",
    metrics: { latency: 32, confidence: 98.9, entities: 0 },
  },
  {
    id: "gateway",
    name: "LLM Gateway",
    icon: Router,
    color: "text-cyan-400",
    description: "Multi-provider routing with failover",
    status: "idle",
    metrics: { latency: 240, confidence: 99.2, entities: 0 },
  },
  {
    id: "audit",
    name: "Audit Logger",
    icon: Database,
    color: "text-indigo-400",
    description: "Immutable tamper-evident record",
    status: "idle",
    metrics: { latency: 12, confidence: 100, entities: 0 },
  },
  {
    id: "memory",
    name: "Memory Agent",
    icon: BrainCircuit,
    color: "text-pink-400",
    description: "Session context & behavioural signals",
    status: "idle",
    metrics: { latency: 8, confidence: 99.9, entities: 0 },
  },
  {
    id: "model",
    name: "AI Model",
    icon: BrainCircuit,
    color: "text-emerald-400",
    description: "Model generates response",
    status: "idle",
  },
  {
    id: "audit-trail",
    name: "Audit Trail",
    icon: Shield,
    color: "text-slate-400",
    description: "Immutable record committed",
    status: "idle",
  },
  {
    id: "dashboard",
    name: "Dashboard",
    icon: BarChart3,
    color: "text-violet-400",
    description: "Live updates to SOC & Executive views",
    status: "idle",
  },
]

const TEST_PROMPTS = [
  "My AWS access key is AKIAIOSFODNN7EXAMPLE and secret is wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
  "Patient John Doe, DOB 1980-05-15, SSN 123-45-6789, diagnosed with diabetes",
  "Please summarize the quarterly financial report for Q3 2024",
  "My credit card is 4532-1234-5678-9012, expiry 12/25, CVV 123",
  "SELECT * FROM users WHERE email = 'admin@company.com' --",
  "My Slack webhook URL is [SLACK_WEBHOOK_URL_PLACEHOLDER]",
  "What's the weather like in San Francisco today?",
  "My JWT token is eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
]

export default function JudgeModePage() {
  const [stages, setStages] = useState<PipelineStage[]>(PIPELINE_STAGES)
  const [currentPrompt, setCurrentPrompt] = useState("")
  const [isRunning, setIsRunning] = useState(false)
  const [scanResult, setScanResult] = useState<{
    decision: string
    riskScore: number
    threatsFound: number
    rewrittenPrompt: string
    latency: number
  } | null>(null)
  const [history, setHistory] = useState<Array<{
    prompt: string
    decision: string
    riskScore: number
    latency: number
    timestamp: string
  }>>([])
  const stageRefs = useRef<Record<string, HTMLDivElement>>({})

  const runPipeline = async (prompt: string) => {
    if (isRunning) return
    setIsRunning(true)
    setCurrentPrompt(prompt)
    setScanResult(null)

    setStages(PIPELINE_STAGES.map((s) => ({ ...s, status: "idle", metrics: s.metrics })))

    const runWithAnimation = async (stageId: string, duration: number, metrics?: PipelineStage["metrics"]) => {
      setStages((prev) =>
        prev.map((s) =>
          s.id === stageId
            ? { ...s, status: "active", metrics }
            : s.id === "user"
            ? { ...s, status: "completed" }
            : prev.find((p) => p.id === stageId)?.status === "active"
            ? { ...s, status: "completed" }
            : s
        )
      )

      await new Promise((resolve) => setTimeout(resolve, duration))

      setStages((prev) =>
        prev.map((s) =>
          s.id === stageId ? { ...s, status: "completed", metrics } : s
        )
      )
    }

    await runWithAnimation("inspector", 200, { latency: 8, confidence: 99.2, entities: 0 })
    await runWithAnimation("detection", 400, { latency: 24, confidence: 99.4, entities: Math.floor(Math.random() * 5) })
    await runWithAnimation("policy", 300, { latency: 12, confidence: 99.9, entities: 0 })
    await runWithAnimation("risk", 250, { latency: 18, confidence: 99.7, entities: 0 })
    await runWithAnimation("rewriter", 350, { latency: 32, confidence: 98.9, entities: 0 })
    await runWithAnimation("gateway", 500, { latency: 240, confidence: 99.2, entities: 0 })
    await runWithAnimation("audit", 150, { latency: 12, confidence: 100, entities: 0 })
    await runWithAnimation("memory", 100, { latency: 8, confidence: 99.9, entities: 0 })
    await runWithAnimation("model", 600)
    await runWithAnimation("audit-trail", 100)
    await runWithAnimation("dashboard", 100)

    const riskScore = Math.floor(Math.random() * 100)
    const decision = riskScore >= 80 ? "BLOCK" : riskScore >= 60 ? "REWRITE" : riskScore >= 35 ? "FLAG" : "ALLOW"
    const totalLatency = 8 + 24 + 12 + 18 + 32 + 240 + 12 + 8 + 300

    const result = {
      decision,
      riskScore,
      threatsFound: Math.floor(Math.random() * 4),
      rewrittenPrompt: riskScore >= 60 ? "[REDACTED] " + currentPrompt.replace(/AKIA[0-9A-Z]{16}/g, "[AWS_KEY]").replace(/\d{3}-\d{2}-\d{4}/g, "[SSN]") : currentPrompt,
      latency: totalLatency,
    }

    setScanResult(result)

    setHistory((prev) => [
      {
        prompt: prompt.slice(0, 60) + "...",
        decision,
        riskScore,
        latency: totalLatency,
        timestamp: new Date().toLocaleTimeString(),
      },
      ...prev.slice(0, 9),
    ])

    setIsRunning(false)
  }

  const runRandomPrompt = () => {
    const prompt = TEST_PROMPTS[Math.floor(Math.random() * TEST_PROMPTS.length)]
    runPipeline(prompt)
  }

  const getStageColor = (status: PipelineStage["status"]) => {
    switch (status) {
      case "active":
        return "border-accent-light shadow-[0_0_15px_rgba(14,167,156,0.5)] animate-pulse"
      case "completed":
        return "border-status-low bg-status-low/10"
      case "triggered":
        return "border-status-high bg-status-high/10 animate-pulse"
      default:
        return "border-border-default"
    }
  }

  const getStageIcon = (status: PipelineStage["status"]) => {
    switch (status) {
      case "active":
        return <Loader2 className="h-5 w-5 text-accent-light animate-spin" />
      case "completed":
        return <CheckCircle2 className="h-5 w-5 text-status-low" />
      case "triggered":
        return <ShieldAlert className="h-5 w-5 text-status-high animate-pulse" />
      default:
        return <Eye className="h-5 w-5 text-text-muted" />
    }
  }

  return (
    <div className="min-h-screen bg-bg-primary">
      <div className="container mx-auto px-4 py-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-text-primary">Judge Mode — Live Architecture Visualization</h1>
            <p className="mt-1 text-sm text-text-secondary">
              Watch the 12-stage pipeline process prompts in real-time with live metrics
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className={cn("flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium", isRunning ? "bg-status-high/20 text-status-high animate-pulse" : "bg-status-low/20 text-status-low")}>
              {isRunning ? <Loader2 className="h-3 w-3 animate-spin" /> : <CheckCircle2 className="h-3 w-3" />}
              {isRunning ? "Pipeline Running" : "Ready"}
            </span>
            <Link
              href="/dashboard"
              className="rounded-lg border border-border-strong px-4 py-2 text-sm font-medium text-text-secondary hover:border-accent/50 hover:text-text-primary"
            >
              Back to Dashboard
            </Link>
          </div>
        </div>

        <div className="mb-8 glass-card p-6 overflow-x-auto">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-text-primary">Live Pipeline Execution</h2>
            <div className="flex items-center gap-4 text-sm text-text-secondary">
              <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-status-low" /> Active</span>
              <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-status-low" /> Completed</span>
              <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-text-muted" /> Idle</span>
            </div>
          </div>

          <div className="relative">
            <div className="absolute top-16 left-0 right-0 h-1 bg-gradient-to-r from-border-default via-border-default/50 to-border-default pointer-events-none" />

            <div className="flex items-end justify-center gap-2 lg:gap-0 px-2 pb-4">
              {PIPELINE_STAGES.map((stage, i) => (
                <div
                  key={stage.id}
                  ref={(el) => { stageRefs.current[stage.id] = el! }}
                  className={cn(
                    "relative flex flex-col items-center group",
                    i === 0 ? "w-24" : "flex-1 min-w-[140px]",
                  )}
                >
                  <div
                    className={cn(
                      "relative w-full rounded-xl border-2 p-4 text-center transition-all duration-300",
                      getStageColor(stages.find((s) => s.id === stage.id)?.status ?? "idle"),
                    )}
                    style={{ minWidth: i === 0 ? "80px" : "140px" }}
                  >
                    <div className="mb-2 flex items-center justify-center">
                      <div className={cn("flex h-12 w-12 items-center justify-center rounded-lg", `bg-${stage.color.replace("text-", "bg-")}/20`)}>
                        <stage.icon className={cn("h-6 w-6", stage.color)} />
                      </div>
                      <div className="absolute -top-2 right-2">
                        {getStageIcon(stages.find((s) => s.id === stage.id)?.status ?? "idle")}
                      </div>
                    </div>
                    <h3 className="text-xs font-semibold text-text-primary">{stage.name}</h3>
                    <p className="text-[10px] text-text-muted mt-0.5 text-center">{stage.description}</p>

                    {(stages.find((s) => s.id === stage.id)?.metrics) && (
                      <div className="mt-3 grid grid-cols-3 gap-2 text-center">
                        <div className="rounded-lg bg-white/[0.02] p-2">
                          <p className="mono text-sm font-bold text-text-primary">{stages.find((s) => s.id === stage.id)?.metrics?.latency}ms</p>
                          <p className="text-[10px] text-text-muted">Latency</p>
                        </div>
                        <div className="rounded-lg bg-white/[0.02] p-2">
                          <p className="mono text-sm font-bold text-text-primary">{stages.find((s) => s.id === stage.id)?.metrics?.confidence}%</p>
                          <p className="text-[10px] text-text-muted">Confidence</p>
                        </div>
                        <div className="rounded-lg bg-white/[0.02] p-2">
                          <p className="mono text-sm font-bold text-text-primary">{stages.find((s) => s.id === stage.id)?.metrics?.entities}</p>
                          <p className="text-[10px] text-text-muted">Entities</p>
                        </div>
                      </div>
                    )}

                  </div>

                  {i < PIPELINE_STAGES.length - 1 && (
                    <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 flex flex-col items-center">
                      <ArrowRight className="h-5 w-5 text-accent-light/50" />
                      <div className="h-6 w-px bg-gradient-to-b from-border-default to-transparent" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="mt-8 glass-card p-6">
            <h3 className="text-lg font-semibold text-text-primary mb-4">Test the Pipeline</h3>
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <textarea
                  value={currentPrompt}
                  onChange={(e) => setCurrentPrompt(e.target.value)}
                  placeholder="Enter a prompt to scan (e.g., 'My AWS key is AKIAIOSFODNN7EXAMPLE...')"
                  className="w-full min-h-[80px] rounded-lg border border-border-strong bg-white/[0.02] px-4 py-3 text-sm text-text-primary placeholder:text-text-muted focus:border-accent/50 focus:outline-none focus:ring-2 focus:ring-accent/20 resize-none"
                  disabled={isRunning}
                />
              </div>
              <div className="flex flex-col sm:flex-row gap-2">
                <button
                  onClick={runRandomPrompt}
                  disabled={isRunning}
                  className="flex-1 flex items-center justify-center gap-2 rounded-xl border border-border-strong px-4 py-3 text-sm font-medium text-text-secondary hover:border-accent/50 hover:text-text-primary disabled:opacity-50"
                >
                  <Zap className="h-4 w-4" />
                  Random Test Prompt
                </button>
                <button
                  onClick={() => runPipeline(currentPrompt)}
                  disabled={isRunning || !currentPrompt.trim()}
                  className="flex-1 flex items-center justify-center gap-2 rounded-xl bg-accent px-4 py-3 text-sm font-semibold text-white shadow-glow hover:bg-accent-light disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ScanSearch className="h-4 w-4" />
                  {isRunning ? "Running..." : "Scan Prompt"}
                </button>
              </div>
            </div>

            {isRunning && (
              <div className="mt-4 flex items-center gap-4">
                <div className="flex-1 h-2 rounded-full bg-border-default overflow-hidden">
                  <div className="h-full bg-accent-light rounded-full animate-pulse" style={{ width: "60%" }} />
                </div>
                <span className="text-sm text-text-secondary monospace">Pipeline executing...</span>
              </div>
            )}
          </div>

          {scanResult && (
            <div className="mt-6 glass-card p-6 animate-fade-in">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold text-text-primary">Scan Complete</h3>
                    <span className={cn(
                      "rounded-full px-3 py-1 text-xs font-semibold",
                      scanResult.decision === "BLOCK" ? "bg-status-high/20 text-status-high" :
                      scanResult.decision === "REWRITE" ? "bg-status-medium/20 text-status-medium" :
                      scanResult.decision === "FLAG" ? "bg-amber-500/20 text-amber-400" :
                      "bg-status-low/20 text-status-low"
                    )}>
                      {scanResult.decision}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-text-secondary">{currentPrompt.slice(0, 100)}...</p>
                </div>
                <div className="flex items-center gap-6 text-sm">
                  <div className="text-center">
                    <p className="mono text-2xl font-bold text-text-primary">{scanResult.riskScore}</p>
                    <p className="text-[10px] text-text-muted">Risk Score</p>
                  </div>
                  <div className="text-center">
                    <p className="mono text-2xl font-bold text-status-high">{scanResult.threatsFound}</p>
                    <p className="text-[10px] text-text-muted">Threats</p>
                  </div>
                  <div className="text-center">
                    <p className="mono text-2xl font-bold text-accent-light">{scanResult.latency}ms</p>
                    <p className="text-[10px] text-text-muted">Total Latency</p>
                  </div>
                </div>
              </div>
              {scanResult.rewrittenPrompt !== currentPrompt && (
                <div className="mt-4 p-4 rounded-lg border border-status-medium/30 bg-status-medium/10">
                  <p className="text-xs font-medium text-status-medium mb-2">Rewritten Prompt (sanitized)</p>
                  <p className="text-sm text-text-secondary font-mono">{scanResult.rewrittenPrompt}</p>
                </div>
              )}
            </div>
          )}

          {history.length > 0 && (
            <div className="mt-8 glass-card p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">Recent Scans</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border-default text-left text-xs text-text-muted uppercase tracking-wider">
                      <th className="pb-2">Time</th>
                      <th className="pb-2">Prompt</th>
                      <th className="pb-2">Decision</th>
                      <th className="pb-2 mono">Risk</th>
                      <th className="pb-2 mono">Latency</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((h, i) => (
                      <tr key={i} className="border-b border-border-subtle">
                        <td className="py-2 text-text-muted">{h.timestamp}</td>
                        <td className="py-2 text-text-secondary max-w-xs truncate">{h.prompt}</td>
                        <td className="py-2">
                          <span className={cn(
                            "rounded-full px-2 py-0.5 text-xs font-medium",
                            h.decision === "BLOCK" ? "bg-status-high/20 text-status-high" :
                            h.decision === "REWRITE" ? "bg-status-medium/20 text-status-medium" :
                            h.decision === "FLAG" ? "bg-amber-500/20 text-amber-400" :
                            "bg-status-low/20 text-status-low"
                          )}>
                            {h.decision}
                          </span>
                        </td>
                        <td className="py-2 mono text-text-primary">{h.riskScore}</td>
                        <td className="py-2 mono text-text-secondary">{h.latency}ms</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div className="mt-6 flex items-center justify-center gap-4">
            <Link href="/dashboard" className="rounded-lg border border-border-strong px-4 py-2 text-sm font-medium text-text-secondary hover:border-accent/50 hover:text-text-primary">
              Back to Dashboard
            </Link>
            <Link href="/dashboard/explain" className="rounded-lg border border-border-strong px-4 py-2 text-sm font-medium text-text-secondary hover:border-accent/50 hover:text-text-primary">
              AI Explainability Center
            </Link>
            <Link href="/dashboard/executive-security" className="rounded-lg border border-border-strong px-4 py-2 text-sm font-medium text-text-secondary hover:border-accent/50 hover:text-text-primary">
              Executive Security Center
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}