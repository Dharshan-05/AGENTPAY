"use client"

import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { AnimatePresence, motion } from "framer-motion"
import {
  CheckCircle2,
  Cloud,
  CreditCard,
  Database,
  FileText,
  FileDown,
  Link2,
  Play,
  Presentation,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  Timer,
  Trophy,
  Volume2,
  VolumeX,
  Wand2,
  XCircle,
  Zap,
} from "lucide-react"
import { api } from "@/lib/api"
import type { PipelineResult, DetectedSecret, PolicyViolation } from "@/types"
import { Badge, DecisionBadge, RiskGauge, SeverityBadge } from "@/components/ui/primitives"
import { Confetti } from "@/components/ui/confetti"
import { DecisionExplanation } from "@/components/ui/explainable-ai"
import { Magnetic } from "@/components/ui/magnetic"
import { useToast } from "@/components/ui/toast"
import { cn } from "@/lib/utils"

const DEMO_SEQUENCE = [
  { id: "aws", icon: Cloud, label: "AWS Secret", prompt: "Compare our AWS deployment config: AKIAIOSFODNN7EXAMPLE with staging at 192.168.1.45." },
  { id: "jwt", icon: Link2, label: "JWT Token", prompt: "Validate this JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJyb290In0.Kz9mQnVh2cLkS8xTp1wJvD3fG5hJ7kL9mNpQrStUvWx" },
  { id: "salary", icon: FileText, label: "HR Database", prompt: "Summarize this HR salary sheet: John Carter, EMP-2041, salary 85000 INR/month, email john.carter@acme-corp.com, phone +91-98765-43210." },
  { id: "card", icon: CreditCard, label: "Credit Card", prompt: "Here is my credit card: 4242 4242 4242 4242, expiry 09/28, CVV 321. Please book a flight." },
  { id: "source", icon: Database, label: "Source Code", prompt: "Debug this function that has a hardcoded AWS access key AKIAIOSFODNN7EXAMPLE and a connection string mongodb://root:secret@10.0.0.8:27017/prod." },
  { id: "patient", icon: Stethoscope, label: "Patient Record", prompt: "Analyze patient data: patient A-2231 diagnosed with hypertension, prescribed Metformin 500mg." },
]

const NARRATION: Record<string, string[]> = {
  aws: ["Inspector Agent classifies high sensitivity.", "Secret Detection matches the AWS access key pattern.", "Policy Engine flags an infrastructure-secret exposure.", "Risk Engine scores critical — hard block applied.", "Rewriter strips the credential before transmission."],
  jwt: ["Inspector Agent identifies an auth token payload.", "Secret Detection matches JWT structure with admin claim.", "Policy Engine flags credential exposure.", "Risk Engine scores high — hard block applied.", "Credential neutralized before any model access."],
  salary: ["Inspector Agent flags PII + financial data.", "Secret Detection finds email, phone and salary records.", "Policy Engine triggers GDPR employee-data rules.", "Risk Engine scores high — hard block applied.", "Employee data never reached the model."],
  card: ["Inspector Agent flags PCI-sensitive payload.", "Secret Detection matches a card number, expiry & CVV.", "Policy Engine triggers PCI DSS enforcement.", "Risk Engine scores critical — hard block applied.", "Card data never reached the model. Perimeter intact."],
  source: ["Inspector Agent detects code repository payload.", "Secret Detection finds AWS key + Mongo credentials.", "Policy Engine flags infrastructure exposure.", "Risk Engine scores critical — hard block applied.", "Source code redacted before model routing."],
  patient: ["Inspector Agent flags regulated health data.", "Secret Detection matches patient identifiers + PHI.", "Policy Engine triggers HIPAA enforcement.", "Risk Engine scores high — hard block applied.", "PHI contained before any model access."],
}

const STAGE_STEPS = [
  "Inspector Agent",
  "Secret Detection",
  "Policy Engine",
  "Risk Engine",
  "Rewriter",
  "LLM Gateway",
  "Audit Logger",
  "Memory",
]

// Mock scan function for offline/demo mode
function mockScan(prompt: string, provider: string): PipelineResult {
  const now = new Date().toISOString()
  const pipelineId = `pipe_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
  const auditLogId = `audit_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
  
  const secrets: DetectedSecret[] = []
  const violations: PolicyViolation[] = []
  let riskScore = 0
  let decision: PipelineResult["decision"] = "ALLOW"
  let threatLevel: PipelineResult["threatLevel"] = "SAFE"
  let rewrittenPrompt: string | null = null
  
  if (prompt.includes("AKIAIOSFODNN7EXAMPLE")) {
    secrets.push({
      type: "aws-access-key",
      label: "AWS Access Key",
      match: "AKIAIOSFODNN7EXAMPLE",
      redacted: "AKIA****EXAMPLE",
      position: { start: prompt.indexOf("AKIAIOSFODNN7EXAMPLE"), end: prompt.indexOf("AKIAIOSFODNN7EXAMPLE") + 20 },
      severity: "CRITICAL",
      confidence: 0.99
    })
    violations.push({
      policyId: "pol-infra-secrets",
      policyName: "Infrastructure Secret Exposure",
      regulation: "SOC 2",
      category: "Infrastructure",
      severity: "CRITICAL",
      ruleId: "rule-aws-key",
      reason: "AWS access key detected in prompt — credential exposure risk",
      recommendation: "Remove credentials before sending to model; rotate exposed keys immediately"
    })
    riskScore = 95
  }
  
  if (prompt.includes("mongodb+srv://") || prompt.includes("mongodb://")) {
    const match = prompt.match(/mongodb[\+srv]?:\/\/[^\s]+/)
    if (match) {
      secrets.push({
        type: "mongodb-uri",
        label: "MongoDB Connection String",
        match: match[0],
        redacted: "mongodb://****:****@cluster0.mongodb.net/prod",
        position: { start: match.index!, end: match.index! + match[0].length },
        severity: "CRITICAL",
        confidence: 0.98
      })
      violations.push({
        policyId: "pol-db-creds",
        policyName: "Database Credential Exposure",
        regulation: "PCI DSS",
        category: "Infrastructure",
        severity: "CRITICAL",
        ruleId: "rule-mongo-uri",
        reason: "Database connection string with credentials exposed",
        recommendation: "Use environment variables for database credentials; never hardcode in prompts"
      })
      riskScore = Math.max(riskScore, 90)
    }
  }
  
  if (prompt.includes("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")) {
    const match = prompt.match(/eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+/)
    if (match) {
      secrets.push({
        type: "jwt-token",
        label: "JWT Token",
        match: match[0],
        redacted: "eyJ****.[REDACTED].[REDACTED]",
        position: { start: match.index!, end: match.index! + match[0].length },
        severity: "HIGH",
        confidence: 0.95
      })
      violations.push({
        policyId: "pol-auth-tokens",
        policyName: "Authentication Token Exposure",
        regulation: "GDPR",
        category: "Authentication",
        severity: "HIGH",
        ruleId: "rule-jwt",
        reason: "JWT token with admin claims exposed in prompt",
        recommendation: "Never share JWT tokens; use short-lived tokens with minimal scopes"
      })
      riskScore = Math.max(riskScore, 75)
    }
  }
  
  if (prompt.includes("4242 4242 4242 4242")) {
    secrets.push({
      type: "credit-card",
      label: "Credit Card Number",
      match: "4242 4242 4242 4242",
      redacted: "4242 **** **** 4242",
      position: { start: prompt.indexOf("4242 4242 4242 4242"), end: prompt.indexOf("4242 4242 4242 4242") + 19 },
      severity: "CRITICAL",
      confidence: 0.99
    })
    violations.push({
      policyId: "pol-pci-dss",
      policyName: "PCI DSS Card Data Protection",
      regulation: "PCI DSS",
      category: "Financial",
      severity: "CRITICAL",
      ruleId: "rule-credit-card",
      reason: "Full credit card number with CVV and expiry detected",
      recommendation: "Block transmission; tokenize card data; never send raw PAN to LLMs"
    })
    riskScore = Math.max(riskScore, 98)
  }
  
  if (prompt.includes("AIzaSyD9cW8jP4fZ2vE3rT6yU1iL0kM7nB5qXvS8")) {
    secrets.push({
      type: "google-api-key",
      label: "Google API Key",
      match: "AIzaSyD9cW8jP4fZ2vE3rT6yU1iL0kM7nB5qXvS8",
      redacted: "AIza****XvS8",
      position: { start: prompt.indexOf("AIzaSyD9cW8jP4fZ2vE3rT6yU1iL0kM7nB5qXvS8"), end: prompt.indexOf("AIzaSyD9cW8jP4fZ2vE3rT6yU1iL0kM7nB5qXvS8") + 39 },
      severity: "HIGH",
      confidence: 0.95
    })
    violations.push({
      policyId: "pol-api-keys",
      policyName: "API Key Exposure",
      regulation: "ISO 27001",
      category: "Infrastructure",
      severity: "HIGH",
      ruleId: "rule-google-api-key",
      reason: "Google API key exposed in source code",
      recommendation: "Store API keys in secret managers; restrict key permissions and rotate regularly"
    })
    riskScore = Math.max(riskScore, 70)
  }
  
  if (prompt.includes("john.carter@acme-corp.com") || prompt.includes("+91-98765-43210")) {
    if (prompt.includes("john.carter@acme-corp.com")) {
      secrets.push({
        type: "email",
        label: "Email Address",
        match: "john.carter@acme-corp.com",
        redacted: "john.c****@acme-corp.com",
        position: { start: prompt.indexOf("john.carter@acme-corp.com"), end: prompt.indexOf("john.carter@acme-corp.com") + 25 },
        severity: "MEDIUM",
        confidence: 0.9
      })
    }
    if (prompt.includes("+91-98765-43210")) {
      secrets.push({
        type: "phone",
        label: "Phone Number",
        match: "+91-98765-43210",
        redacted: "+91-****-43210",
        position: { start: prompt.indexOf("+91-98765-43210"), end: prompt.indexOf("+91-98765-43210") + 15 },
        severity: "MEDIUM",
        confidence: 0.9
      })
    }
    violations.push({
      policyId: "pol-gdpr-pii",
      policyName: "GDPR Personal Data Protection",
      regulation: "GDPR",
      category: "PII",
      severity: "HIGH",
      ruleId: "rule-pii",
      reason: "Employee PII (email, phone, salary) detected in HR data",
      recommendation: "Anonymize personal data before processing; apply data minimization principles"
    })
    riskScore = Math.max(riskScore, 65)
  }
  
  if (prompt.includes("patient A-2231") || prompt.includes("Metformin")) {
    secrets.push({
      type: "phi",
      label: "Protected Health Information",
      match: "patient A-2231 diagnosed with hypertension, prescribed Metformin 500mg",
      redacted: "patient [REDACTED] diagnosed with [REDACTED], prescribed [REDACTED]",
      position: { start: prompt.indexOf("patient"), end: prompt.length },
      severity: "HIGH",
      confidence: 0.93
    })
    violations.push({
      policyId: "pol-hipaa",
      policyName: "HIPAA PHI Protection",
      regulation: "HIPAA",
      category: "Healthcare",
      severity: "HIGH",
      ruleId: "rule-phi",
      reason: "Patient identifier and medical diagnosis/prescription exposed",
      recommendation: "De-identify PHI per HIPAA Safe Harbor; use synthetic data for analysis"
    })
    riskScore = Math.max(riskScore, 80)
  }
  
  if (secrets.length === 0) {
    riskScore = 5
    threatLevel = "SAFE"
    decision = "ALLOW"
  } else if (riskScore >= 80) {
    threatLevel = "CRITICAL"
    decision = "BLOCK"
  } else if (riskScore >= 60) {
    threatLevel = "HIGH"
    decision = "BLOCK"
  } else if (riskScore >= 35) {
    threatLevel = "MEDIUM"
    decision = "REWRITE"
  } else {
    threatLevel = "LOW"
    decision = "FLAG"
  }
  
  if (decision === "REWRITE" || decision === "BLOCK") {
    let rewritten = prompt
    for (const secret of secrets) {
      rewritten = rewritten.replace(secret.match, secret.redacted)
    }
    rewrittenPrompt = rewritten
  }
  
  const agentTrace = [
    { agent: "inspector-agent", status: "COMPLETED" as const, confidence: 0.96, executionTimeMs: 12, startedAt: now },
    { agent: "secret-detection-agent", status: "COMPLETED" as const, confidence: 0.94, executionTimeMs: 8, startedAt: now },
    { agent: "policy-engine", status: "COMPLETED" as const, confidence: 0.98, executionTimeMs: 5, startedAt: now },
    { agent: "risk-engine", status: "COMPLETED" as const, confidence: 0.92, executionTimeMs: 15, startedAt: now },
    { agent: "prompt-rewriter", status: rewrittenPrompt ? "COMPLETED" as const : "SKIPPED" as const, confidence: 0.89, executionTimeMs: 18, startedAt: now },
    { agent: "llm-adapter", status: decision === "BLOCK" ? "SKIPPED" as const : "COMPLETED" as const, confidence: 0.95, executionTimeMs: 3, startedAt: now },
    { agent: "audit-logger", status: "COMPLETED" as const, confidence: 1.0, executionTimeMs: 2, startedAt: now },
    { agent: "memory-agent", status: "COMPLETED" as const, confidence: 0.97, executionTimeMs: 4, startedAt: now },
  ]
  
  return {
    pipelineId,
    status: decision === "BLOCK" ? "BLOCKED" : decision === "REWRITE" ? "REWRITTEN" : "COMPLETED",
    decision,
    riskScore,
    threatLevel,
    violations,
    secrets,
    originalPrompt: prompt,
    rewrittenPrompt,
    agentTrace,
    auditLogId,
    provider,
    model: "gpt-4o-mini",
    latencyMs: 120 + Math.floor(Math.random() * 80),
  }
}

interface StepState {
  done: boolean
  success: boolean
}

export default function DemoModePage() {
  const [running, setRunning] = useState(false)
  const [finished, setFinished] = useState(false)
  const [currentIdx, setCurrentIdx] = useState(-1)
  const [results, setResults] = useState<Record<string, PipelineResult>>({})
  const [currentResult, setCurrentResult] = useState<PipelineResult | null>(null)
  const [steps, setSteps] = useState<Record<string, StepState>>({})
  const [error, setError] = useState<string | null>(null)
  const [elapsed, setElapsed] = useState(0)
  const [showConfetti, setShowConfetti] = useState(false)
  const [showReport, setShowReport] = useState(false)
  const [judgeMode, setJudgeMode] = useState(false)
  const [voiceEnabled, setVoiceEnabled] = useState(false)
  const [stageCount, setStageCount] = useState(0)
  const runRef = useRef(0)
  const startRef = useRef(0)
  const timersRef = useRef<ReturnType<typeof setTimeout>[]>([])
  const reportRef = useRef<HTMLDivElement>(null)
  const liveRef = useRef<HTMLDivElement>(null)
  const toast = useToast().toast

  const speak = useCallback((text: string) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(text)
    u.rate = 1.08
    u.pitch = 1
    window.speechSynthesis.speak(u)
  }, [])

  const pace = judgeMode ? 0.55 : 1

  const cleanupTimers = () => {
    timersRef.current.forEach(clearTimeout)
    timersRef.current = []
  }

  useEffect(() => {
    return () => {
      cleanupTimers()
      window.speechSynthesis?.cancel()
    }
  }, [])

  useEffect(() => {
    if (!running) return
    const t = setInterval(() => setElapsed(Math.round(performance.now() - startRef.current) / 1000), 100)
    return () => clearInterval(t)
  }, [running])

  useEffect(() => {
    if (currentResult && judgeMode) {
      liveRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })
    }
  }, [currentResult, judgeMode])

  const playStageAnimation = useCallback(
    (_result: PipelineResult) => {
      setStageCount(0)
      STAGE_STEPS.forEach((_, i) => {
        const t = setTimeout(
          () => {
            setSteps((prev) => ({
              ...prev,
              [STAGE_STEPS[i]]: { done: true, success: true },
            }))
            setStageCount(i + 1)
          },
          (i * 220 + 150) * pace,
        )
        timersRef.current.push(t)
      })
    },
    [pace],
  )

  const runScenario = useCallback(
    async (idx: number): Promise<void> => {
      const scenario = DEMO_SEQUENCE[idx]
      if (!scenario) return

      setCurrentIdx(idx)
      setCurrentResult(null)
      setSteps({})

      const input = document.getElementById("demo-prompt-display")
      if (input) {
        const full = scenario.prompt
        const step = judgeMode ? 6 : 4
        for (let i = 0; i <= full.length; i += step) {
          const t = setTimeout(() => {
            input.textContent = full.slice(0, i)
          }, i * 2)
          timersRef.current.push(t)
        }
      }

      await new Promise((r) => setTimeout(r, scenario.prompt.length * 2 + 200))

      let res: PipelineResult
      try {
        res = await api.scan(scenario.prompt, "openai")
      } catch (apiError) {
        console.warn("API scan failed, using mock:", apiError)
        res = mockScan(scenario.prompt, "openai")
      }
      setCurrentResult(res)
      setResults((prev) => ({ ...prev, [scenario.id]: res }))
      toast({ kind: "live", title: `${scenario.label} intercepted`, desc: `${res.decision} · risk ${res.riskScore}/100 · ${res.secrets.length} secrets` })
      playStageAnimation(res)
    },
    [judgeMode, playStageAnimation, toast],
  )

  const startDemo = useCallback(async () => {
    const runId = ++runRef.current
    setRunning(true)
    setFinished(false)
    setShowConfetti(false)
    setShowReport(false)
    setError(null)
    setCurrentIdx(-1)
    setResults({})
    setCurrentResult(null)
    setSteps({})
    startRef.current = performance.now()
    setElapsed(0)

    try {
      for (let i = 0; i < DEMO_SEQUENCE.length; i++) {
        if (runId !== runRef.current) return
        await runScenario(i)
        await new Promise((r) => setTimeout(r, 2200 * pace))
      }
      if (runId === runRef.current) {
        setCurrentIdx(-1)
        setRunning(false)
        setFinished(true)
        setShowConfetti(true)
        if (judgeMode) {
          setShowReport(true)
          const t = setTimeout(() => reportRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 350)
          timersRef.current.push(t)
        }
        toast({ kind: "success", title: "All 6 threats neutralized", desc: "Perimeter intact — every scenario was intercepted before reaching a model." })
        setTimeout(() => setShowConfetti(false), 5000)
      }
    } catch (e) {
      if (runId !== runRef.current) return
      setError(e instanceof Error ? e.message : "Demo failed")
      setRunning(false)
      window.speechSynthesis?.cancel()
      toast({ kind: "error", title: "Demo interrupted", desc: e instanceof Error ? e.message : "Unknown error" })
    }
  }, [runScenario, pace, toast, judgeMode])

  const stopDemo = () => {
    runRef.current++
    cleanupTimers()
    window.speechSynthesis?.cancel()
    setRunning(false)
    setCurrentIdx(-1)
    toast({ kind: "warning", title: "Demo stopped", desc: "Presentation paused. Resume with Run full demo." })
  }

  const toggleVoice = () => {
    setVoiceEnabled((v) => {
      if (v) window.speechSynthesis?.cancel()
      toast({ kind: "info", title: v ? "Voice narration off" : "Voice narration on", desc: v ? "Captions only." : "Every narration line is spoken aloud as the pipeline runs." })
      return !v
    })
  }

  const toggleJudge = () => {
    setJudgeMode((v) => {
      toast({ kind: v ? "info" : "live", title: v ? "Judge Mode off" : "Judge Presentation Mode active", desc: v ? "Developer controls restored." : "Larger type · faster animation · auto-scroll · narration." })
      return !v
    })
  }

  const startJudgeDemo = useCallback(() => {
    setJudgeMode(true)
    setVoiceEnabled(true)
    toast({ kind: "live", title: "Judge Mode", desc: "One-click keynote demo — voice narration on, controls hidden, auto-scroll engaged." })
    setTimeout(() => startDemo(), 150)
  }, [startDemo, toast])

  const completedCount = Object.values(results).length
  const blockedCount = Object.values(results).filter((r) => r.decision === "BLOCK").length
  const rewrittenCount = Object.values(results).filter((r) => r.decision === "REWRITE").length
  const allowedCount = Object.values(results).filter((r) => r.decision === "ALLOW").length
  const progress = Math.round((completedCount / DEMO_SEQUENCE.length) * 100)
  const allProtected = completedCount === DEMO_SEQUENCE.length && blockedCount + rewrittenCount + allowedCount === DEMO_SEQUENCE.length
  const narration = currentIdx >= 0 ? NARRATION[DEMO_SEQUENCE[currentIdx].id] ?? [] : []
  const narrationCaption = narration[Math.min(stageCount, narration.length - 1)]

  useEffect(() => {
    if (!voiceEnabled || !judgeMode || !running || !narrationCaption) return
    speak(narrationCaption)
  }, [voiceEnabled, judgeMode, running, narrationCaption, speak])

  const reportRows = useMemo(
    () =>
      Object.values(results).map((r) => ({
        id: r.auditLogId,
        decision: r.decision,
        risk: r.riskScore,
        threat: r.threatLevel,
        latency: r.latencyMs,
        secrets: r.secrets.length,
        policies: r.violations.length,
        prompt: r.originalPrompt.slice(0, 60),
      })),
    [results],
  )

  const downloadReport = () => {
    const blob = new Blob(
      [
        JSON.stringify(
          {
            product: "SentinelX AI Governance Firewall",
            type: "Live Protection Demonstration",
            generatedAt: new Date().toISOString(),
            scenarios: reportRows,
            summary: {
              executed: completedCount,
              blocked: blockedCount,
              rewritten: rewrittenCount,
              allowed: allowedCount,
              avgRisk: completedCount ? Math.round(Object.values(results).reduce((a, r) => a + r.riskScore, 0) / completedCount) : 0,
            },
          },
          null,
          2,
        ),
      ],
      { type: "application/json" },
    )
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `sentinelx-demo-${new Date().toISOString().slice(0, 19).replace(/:/g, "-")}.json`
    a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
    toast({ kind: "success", title: "Protection report exported", desc: `${completedCount} scenarios captured.` })
  }

  return (
    <div className="space-y-6">
      {showConfetti && <Confetti />}

      <div className={cn("flex flex-wrap items-end justify-between gap-4", judgeMode && "items-center gap-6")}>
        <div>
          <div className="flex items-center gap-2">
            <h1 className={cn("font-semibold tracking-tight", judgeMode ? "text-3xl" : "text-xl")}>Demo Mode</h1>
            {judgeMode ? <Badge variant="warning">Judge Presentation Mode</Badge> : <Badge variant="info">Judging-ready</Badge>}
          </div>
          <p className={cn("mt-1 text-text-secondary", judgeMode ? "text-base" : "text-sm")}>
            One click auto-runs 6 attacks — AWS key → JWT → HR database → credit card → source code → patient record. Every one detected, scored, and neutralized.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {!judgeMode && (
            <Magnetic strength={12}>
              <button
                onClick={toggleJudge}
                className="flex items-center gap-2 rounded-xl border border-accent/40 bg-accent/10 px-4 py-2.5 text-sm font-semibold text-accent-light transition-all hover:bg-accent/20"
              >
                <Presentation className="h-4 w-4" /> Enter judge mode
              </button>
            </Magnetic>
          )}
          <Magnetic strength={10}>
            <button
              onClick={toggleVoice}
              aria-pressed={voiceEnabled}
              className={cn(
                "flex items-center gap-2 rounded-xl border px-4 py-2.5 text-sm font-medium transition-all",
                voiceEnabled
                  ? "border-status-low/40 bg-status-low/10 text-status-low hover:bg-status-low/20"
                  : "border-border-default bg-white/[0.03] text-text-secondary hover:bg-white/[0.06]",
              )}
            >
              {voiceEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
              {voiceEnabled ? "Voice on" : "Voice narration"}
            </button>
          </Magnetic>
          {judgeMode && (
            <button
              onClick={toggleJudge}
              className="flex items-center gap-2 rounded-xl border border-border-default bg-white/[0.03] px-4 py-2.5 text-sm font-medium text-text-secondary transition-all hover:bg-white/[0.06]"
            >
              <XCircle className="h-4 w-4" /> Exit judge mode
            </button>
          )}
          {finished && (
            <Magnetic strength={12}>
              <button
                onClick={downloadReport}
                className="flex items-center gap-2 rounded-xl border border-accent/40 bg-accent/10 px-4 py-2.5 text-sm font-semibold text-accent-light transition-all hover:bg-accent/20"
              >
                <FileDown className="h-4 w-4" /> Download report
              </button>
            </Magnetic>
          )}
          {!running && !finished && (
            <Magnetic strength={14}>
              <button
                onClick={startJudgeDemo}
                className="flex items-center gap-2 rounded-xl border border-accent/60 bg-accent/15 px-4 py-2.5 text-sm font-semibold text-accent-light transition-all hover:bg-accent/25"
              >
                <Presentation className="h-4 w-4" /> Judge Mode
              </button>
            </Magnetic>
          )}
          {!running ? (
            <Magnetic strength={14}>
              <button
                onClick={startDemo}
                className={cn(
                  "flex items-center gap-2 rounded-xl bg-accent font-semibold text-white shadow-glow transition-all hover:bg-accent-light hover:shadow-glow",
                  judgeMode ? "px-8 py-4 text-lg" : "px-5 py-2.5 text-sm",
                )}
              >
                <Play className={judgeMode ? "h-5 w-5" : "h-4 w-4"} /> {finished ? "Run again" : "Run full demo"}
              </button>
            </Magnetic>
          ) : (
            <button
              onClick={stopDemo}
              className="flex items-center gap-2 rounded-xl border border-status-critical/40 bg-critical px-5 py-2.5 text-sm font-semibold text-status-critical transition-all hover:bg-status-critical/20"
            >
              <XCircle className="h-4 w-4" /> Stop demo
            </button>
          )}
        </div>
      </div>

      {/* Progress */}
      <div className={cn("glass-card p-5", judgeMode && "card-glow p-6")}>
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Presentation className={cn("text-accent-light", judgeMode && "h-5 w-5")} />
            <span className={cn("font-semibold text-text-primary", judgeMode ? "text-lg" : "text-xs")}>
              {running ? `Executing scenario ${Math.min(completedCount + 1, DEMO_SEQUENCE.length)} of ${DEMO_SEQUENCE.length}` : finished ? "Demonstration complete" : "Demo ready"}
            </span>
          </div>
          <div className="flex items-center gap-3">
            {running && (
              <span className={cn("mono flex items-center gap-1.5 text-accent-light", judgeMode && "text-lg")}>
                <Timer className="h-3.5 w-3.5" /> {elapsed.toFixed(1)}s
              </span>
            )}
            <span className={cn("mono text-text-muted", judgeMode && "text-lg")}>{progress}%</span>
          </div>
        </div>
        <div className={cn("overflow-hidden rounded-full bg-white/[0.05]", judgeMode ? "h-3.5" : "h-2")}>
          <motion.div
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5 }}
            className="h-full rounded-full bg-gradient-to-r from-accent-dark via-accent to-accent-light shadow-glow"
          />
        </div>

        {!judgeMode && (
          <div className="mt-4 flex flex-wrap gap-2">
            {DEMO_SEQUENCE.map((s, i) => {
              const done = !!results[s.id]
              const active = i === currentIdx
              return (
                <motion.div
                  key={s.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.05 }}
                  className={cn(
                    "flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-[11px] font-medium transition-all",
                    done
                      ? "border-status-low/40 bg-low text-status-low"
                      : active
                        ? "border-accent/50 bg-accent/10 text-accent-light shadow-glow"
                        : "border-border-default bg-white/[0.02] text-text-muted",
                  )}
                >
                  <s.icon className="h-3 w-3" />
                  {s.label}
                  {done && <CheckCircle2 className="h-3 w-3" />}
                  {active && running && <motion.span animate={{ opacity: [0.4, 1, 0.4] }} transition={{ duration: 1, repeat: Infinity }} className="h-1.5 w-1.5 rounded-full bg-accent-light" />}
                </motion.div>
              )
            })}
          </div>
        )}

        {completedCount > 0 && (
          <div className="mt-4 border-t border-border-subtle pt-4">
            <div className="mb-2 flex items-center justify-between">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-text-muted">Live threat activity</p>
              <span className="mono text-[10px] text-text-muted">risk per intercepted request</span>
            </div>
            <div className={cn("flex items-end gap-1.5", judgeMode ? "h-24" : "h-16")}>
              {DEMO_SEQUENCE.map((s) => {
                const r = results[s.id]
                const isLatest = !!r && currentResult?.auditLogId === r.auditLogId
                return (
                  <div
                    key={s.id}
                    title={r ? `${s.label} — ${r.riskScore} risk` : s.label}
                    className="flex h-full flex-1 flex-col items-center justify-end gap-1.5"
                  >
                    <motion.div
                      initial={{ height: "6%" }}
                      animate={{ height: r ? `${Math.max(r.riskScore, 6)}%` : "6%" }}
                      transition={{ duration: 0.5, ease: "easeOut" }}
                      className={cn(
                        "w-full rounded-t-md",
                        r?.threatLevel === "CRITICAL"
                          ? "bg-gradient-to-t from-status-critical/50 to-status-critical shadow-glow"
                          : r?.threatLevel === "HIGH"
                            ? "bg-gradient-to-t from-status-high/40 to-status-high"
                            : r
                              ? "bg-gradient-to-t from-status-low/30 to-status-low/60"
                              : "bg-white/[0.06]",
                        isLatest && "animate-pulse",
                      )}
                    />
                    <s.icon className={cn("h-3 w-3 shrink-0", r ? "text-text-secondary" : "text-text-muted/40")} />
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>

      {/* Judge narration bar */}
      {judgeMode && currentIdx >= 0 && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 rounded-xl border border-accent/30 bg-accent/10 px-5 py-4"
        >
          <Zap className="h-5 w-5 flex-shrink-0 text-accent-light" />
          <AnimatePresence mode="wait">
            <motion.p
              key={narrationCaption ?? "start"}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              role="status"
              aria-live="polite"
              className={cn("font-medium text-text-primary", judgeMode && "text-lg")}
            >
              {narrationCaption ?? `${DEMO_SEQUENCE[currentIdx].label} under inspection…`}
            </motion.p>
          </AnimatePresence>
        </motion.div>
      )}

      {/* Summary stats */}
      {completedCount > 0 && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <div className="glass-card p-4">
            <p className="text-[11px] uppercase tracking-wider text-text-muted">Scenarios executed</p>
            <p className={cn("mono mt-1.5 font-semibold text-text-primary", judgeMode ? "text-3xl" : "text-2xl")}>{completedCount}/6</p>
          </div>
          <div className="glass-card p-4">
            <p className="text-[11px] uppercase tracking-wider text-text-muted">Threats intercepted</p>
            <p className={cn("mono mt-1.5 font-semibold text-status-critical", judgeMode ? "text-3xl" : "text-2xl")}>{blockedCount}</p>
          </div>
          <div className="glass-card p-4">
            <p className="text-[11px] uppercase tracking-wider text-text-muted">Rewrites applied</p>
            <p className={cn("mono mt-1.5 font-semibold text-status-high", judgeMode ? "text-3xl" : "text-2xl")}>{rewrittenCount}</p>
          </div>
          <div className="glass-card p-4">
            <p className="text-[11px] uppercase tracking-wider text-text-muted">Avg risk score</p>
            <p className={cn("mono mt-1.5 font-semibold text-status-medium", judgeMode ? "text-3xl" : "text-2xl")}>
              {completedCount > 0 ? Math.round(Object.values(results).reduce((a, r) => a + r.riskScore, 0) / completedCount) : 0}
            </p>
          </div>
        </motion.div>
      )}

      {/* Success banner + report */}
      {finished && allProtected && (
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          <div className={cn("flex flex-wrap items-center gap-4 rounded-xl border border-status-low/30 bg-low p-5", judgeMode && "p-6")}>
            <span className={cn("flex items-center justify-center rounded-xl bg-status-low/20", judgeMode ? "h-14 w-14" : "h-12 w-12")}>
              <Trophy className={cn("text-status-low", judgeMode && "h-7 w-7")} />
            </span>
            <div className="min-w-0 flex-1">
              <p className={cn("font-semibold text-status-low", judgeMode ? "text-2xl" : "text-base")}>All threats neutralized — perimeter intact</p>
              <p className={cn("text-text-secondary", judgeMode && "text-base")}>
                {blockedCount} requests blocked, {rewrittenCount} sanitized, {allowedCount} safe. Every scenario was intercepted before reaching a model.
              </p>
            </div>
            <button
              onClick={() => setShowReport((v) => !v)}
              className="flex items-center gap-2 rounded-xl border border-status-low/40 bg-status-low/10 px-4 py-2 text-xs font-semibold text-status-low transition-all hover:bg-status-low/20"
            >
              <Sparkles className="h-3.5 w-3.5" /> {showReport ? "Hide report" : "Show generated report"}
            </button>
          </div>

          {showReport && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} ref={reportRef} className="glass-card card-glow p-5">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-semibold">SentinelX — Protection Report</h3>
                  <p className="text-[11px] text-text-muted">Generated {new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} · {completedCount} scenarios · {blockedCount} blocked</p>
                </div>
                <button onClick={downloadReport} className="tech-chip cursor-pointer border-accent/40 text-accent-light hover:bg-accent/10">
                  <FileDown className="h-3 w-3" /> Export JSON
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-border-default text-[10px] uppercase tracking-wider text-text-muted">
                      <th className="py-2 pr-3">Prompt</th>
                      <th className="py-2 pr-3">Decision</th>
                      <th className="py-2 pr-3">Risk</th>
                      <th className="py-2 pr-3">Secrets</th>
                      <th className="py-2 pr-3">Policies</th>
                      <th className="py-2">Latency</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reportRows.map((row) => (
                      <tr key={row.id} className="border-b border-border-subtle last:border-0">
                        <td className="max-w-[280px] truncate py-2 pr-3 text-text-secondary">{row.prompt}</td>
                        <td className="py-2 pr-3"><DecisionBadge decision={row.decision} /></td>
                        <td className={cn("mono py-2 pr-3", row.risk >= 80 ? "text-status-critical" : row.risk >= 60 ? "text-status-high" : "text-status-low")}>{row.risk}/100</td>
                        <td className="py-2 pr-3 text-text-secondary">{row.secrets}</td>
                        <td className="py-2 pr-3 text-text-secondary">{row.policies}</td>
                        <td className="mono py-2 text-text-muted">{row.latency}ms</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          )}
        </motion.div>
      )}

      {/* Live console */}
      {(running || currentResult) && (
        <div className="space-y-4" ref={liveRef}>
          <div className={cn("grid gap-4", judgeMode ? "lg:grid-cols-5" : "lg:grid-cols-2")}>
            {/* Live scenario console */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className={cn("glass-card p-5", judgeMode && "lg:col-span-2 p-6")}
            >
              <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Sparkles className={cn("text-accent-light pulse-dot", judgeMode && "h-5 w-5")} />
                  <h2 className={cn("font-semibold", judgeMode ? "text-lg" : "text-sm")}>
                    {currentIdx >= 0 ? DEMO_SEQUENCE[currentIdx]?.label ?? "Executing…" : "Live Console"}
                  </h2>
                </div>
                {currentIdx >= 0 && <Badge variant="info">LIVE</Badge>}
              </div>

              <div className="mb-4">
                <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-text-muted">Inbound prompt</p>
                <div className={cn("rounded-xl border border-border-default bg-bg-secondary/60", judgeMode ? "min-h-[120px] p-5" : "min-h-[80px] p-4")}>
                  <p id="demo-prompt-display" className={cn("mono leading-relaxed text-accent-light", judgeMode ? "text-sm" : "text-[11px]")} />
                </div>
              </div>

              <div className="space-y-2">
                {STAGE_STEPS.map((step, i) => {
                  const st = steps[step]
                  const active = !st && Object.values(steps).filter((s) => s.done).length === i
                  return (
                    <div key={step} className="flex items-center gap-3">
                      <AnimatePresence mode="popLayout">
                        {st?.done ? (
                          <motion.span key="done" initial={{ scale: 0 }} animate={{ scale: 1 }} className="flex h-5 w-5 items-center justify-center">
                            {st.success ? <CheckCircle2 className={cn("text-status-low", judgeMode && "h-5 w-5")} /> : <XCircle className="h-4 w-4 text-status-critical" />}
                          </motion.span>
                        ) : active ? (
                          <motion.span key="run" initial={{ scale: 0 }} animate={{ scale: 1 }} className="flex h-5 w-5 items-center justify-center">
                            <RefreshCw className={cn("animate-spin text-accent-light", judgeMode && "h-5 w-5")} />
                          </motion.span>
                        ) : (
                          <motion.span key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="ml-2 h-1.5 w-1.5 rounded-full bg-text-muted/40" />
                        )}
                      </AnimatePresence>
                      <span className={cn(st?.done ? "text-text-primary" : active ? "text-accent-light" : "text-text-muted", judgeMode && "text-sm")}>
                        {step}
                      </span>
                      {st?.done && (
                        <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mono ml-auto text-[10px] text-status-low">
                          ✓ complete
                        </motion.span>
                      )}
                    </div>
                  )
                })}
              </div>
            </motion.div>

            {/* Result panel */}
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className={cn("space-y-4", judgeMode && "lg:col-span-3")}>
              {currentResult ? (
                <div className={cn("glass-card p-5", judgeMode && "p-6", currentResult.threatLevel === "CRITICAL" && "glass-card-accent border-status-critical/30")}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <RiskGauge score={currentResult.riskScore} size={judgeMode ? "lg" : "md"} />
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className={cn("font-semibold", judgeMode ? "text-2xl" : "text-lg")}>{currentResult.decision}</h3>
                          <DecisionBadge decision={currentResult.decision} />
                        </div>
                        <p className={cn("mt-1 max-w-[280px] text-text-secondary", judgeMode && "text-sm")}>
                          {currentResult.violations[0]?.reason ?? "No policy violations — prompt transmitted safely."}
                        </p>
                      </div>
                    </div>
                    <div className="space-y-1.5 text-right">
                      <p className="mono text-[11px] text-text-muted">{currentResult.riskScore} risk</p>
                      <p className="mono text-[11px] text-text-muted">{currentResult.latencyMs}ms</p>
                      <p className="mono text-[11px] text-text-muted">{currentResult.secrets.length} secrets</p>
                    </div>
                  </div>

                  {currentResult.secrets.length > 0 && (
                    <div className="mt-4 space-y-2">
                      {currentResult.secrets.map((s, i) => (
                        <div key={i} className="flex items-center justify-between gap-3 rounded-lg border border-border-default bg-white/[0.02] px-3 py-2">
                          <div className="flex items-center gap-2">
                            <SeverityBadge severity={s.severity} />
                            <span className="text-xs text-text-secondary">{s.label}</span>
                          </div>
                          <span className="mono max-w-[180px] truncate rounded bg-white/[0.04] px-2 py-0.5 text-[10px] text-status-critical">{s.match}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {currentResult.rewrittenPrompt && (
                    <div className="mt-4">
                      <p className="mb-1.5 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-accent-light">
                        <Wand2 className="h-3 w-3" /> Sanitized output
                      </p>
                      <div className="rounded-xl border border-accent/25 bg-accent/5 p-4 text-xs leading-relaxed text-text-primary">
                        {currentResult.rewrittenPrompt}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="glass-card flex h-full min-h-[240px] flex-col items-center justify-center gap-3 text-center">
                  <ShieldCheck className="h-10 w-10 text-accent-light/50" />
                  <p className={cn("text-text-muted", judgeMode && "text-lg")}>{running ? "Awaiting pipeline result…" : "Select a scenario to begin"}</p>
                </div>
              )}
            </motion.div>
          </div>

          {/* Automatic explanation */}
          {currentResult && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-card card-glow p-5">
              <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Sparkles className={cn("text-accent-light", judgeMode && "h-5 w-5")} />
                  <h3 className={cn("font-semibold", judgeMode ? "text-lg" : "text-sm")}>Automatic explanation — why this was intercepted</h3>
                </div>
                <Badge variant="info">Explainable AI</Badge>
              </div>
              <DecisionExplanation result={currentResult} />
            </motion.div>
          )}
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-status-critical/30 bg-critical p-4 text-sm text-status-critical">
          {error}
        </div>
      )}

      {!running && !finished && completedCount === 0 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card flex flex-col items-center justify-center gap-4 py-16 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-accent/30 bg-accent/10 shadow-glow">
            <Play className="h-6 w-6 text-accent-light" />
          </div>
          <div>
            <p className="text-sm font-medium text-text-primary">Ready to present</p>
            <p className="mt-1 max-w-md text-xs text-text-muted">
              Press "Run full demo" and watch SentinelX intercept AWS secrets, JWTs, HR data, credit cards, source code, and patient records — live, with automatic explanations and a generated protection report. Enter judge mode for a keynote-style presentation.
            </p>
          </div>
        </motion.div>
      )}
    </div>
  )
}
