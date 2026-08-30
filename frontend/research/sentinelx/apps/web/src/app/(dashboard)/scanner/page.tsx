"use client"

import { memo, useCallback, useEffect, useRef, useState } from "react"
import { AnimatePresence, motion } from "framer-motion"
import {
  ArrowDown,
  ArrowRight,
  Bot,
  CheckCircle2,
  Cloud,
  CreditCard,
  Database,
  FastForward,
  FileDown,
  FileText,
  KeyRound,
  Link2,
  MemoryStick,
  Pause,
  Play,
  Radar,
  RefreshCw,
  ScanSearch,
  Send,
  ShieldCheck,
  Sparkles,
  StepBack,
  StepForward,
  Stethoscope,
  Timer,
  Wand2,
  XCircle,
  Zap,
} from "lucide-react"
import { api, PROVIDERS } from "@/lib/api"
import { subscribeAgentUpdates } from "@/lib/live"
import type { AgentTraceEntry, PipelineResult, DetectedSecret, PolicyViolation } from "@/types"
import { Badge, DecisionBadge, PageHeader, RiskGauge, SeverityBadge } from "@/components/ui/primitives"
import { cn } from "@/lib/utils"

const AGENT_META: Record<string, { label: string; icon: typeof Bot; desc: string }> = {
  "inspector-agent": { label: "Inspector Agent", icon: ScanSearch, desc: "Classifies intent & data sensitivity" },
  "secret-detection-agent": { label: "Secret Detection", icon: KeyRound, desc: "30+ pattern rules scan" },
  "policy-engine": { label: "Policy Engine", icon: ShieldCheck, desc: "GDPR · HIPAA · PCI DSS · SOC 2 · ISO 27001" },
  "risk-engine": { label: "Risk Engine", icon: Zap, desc: "Live enterprise risk scoring" },
  "prompt-rewriter": { label: "Prompt Rewriter", icon: Wand2, desc: "Intent-preserving sanitisation" },
  "llm-adapter": { label: "LLM Adapter", icon: Bot, desc: "Multi-provider gateway routing" },
  "audit-logger": { label: "Audit Logger", icon: FileText, desc: "Tamper-evident audit record" },
  "memory-agent": { label: "Memory Agent", icon: MemoryStick, desc: "Session & behavioural context" },
}

const AGENTS = [
  "inspector-agent",
  "secret-detection-agent",
  "policy-engine",
  "risk-engine",
  "prompt-rewriter",
  "llm-adapter",
  "audit-logger",
  "memory-agent",
]

const DEMO_SCENARIOS = [
  { icon: Cloud, label: "AWS Secret", prompt: "Compare our AWS deployment config: AKIAIOSFODNN7EXAMPLE with staging at 192.168.1.45." },
  { icon: Database, label: "Mongo URI", prompt: "Connect to mongodb+srv://admin:Str0ngP@ss!w0rd@cluster0.mongodb.net/prod?retryWrites=true" },
  { icon: Link2, label: "JWT Token", prompt: "Validate this JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJyb290In0.Kz9mQnVh2cLkS8xTp1wJvD3fG5hJ7kL9mNpQrStUvWx" },
  { icon: FileText, label: "Salary Sheet", prompt: "Summarize this HR salary sheet: John Carter, EMP-2041, salary 85000 INR/month, email john.carter@acme-corp.com, phone +91-98765-43210." },
  { icon: CreditCard, label: "Credit Card", prompt: "Here is my credit card: 4242 4242 4242 4242, expiry 09/28, CVV 321. Please book a flight." },
  { icon: KeyRound, label: "API Key", prompt: "Debug this code: const apiKey = \"AIzaSyD9cW8jP4fZ2vE3rT6yU1iL0kM7nB5qXvS8\";" },
  { icon: Stethoscope, label: "Patient Data", prompt: "Analyze patient data: patient A-2231 diagnosed with hypertension, prescribed Metformin 500mg." },
  { icon: Sparkles, label: "Clean Prompt", prompt: "Write a marketing email announcing our new product launch for Q3. Keep it professional." },
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
  
  const agentTrace: AgentTraceEntry[] = [
    { agent: "inspector-agent", status: "COMPLETED", confidence: 0.96, executionTimeMs: 12, startedAt: now },
    { agent: "secret-detection-agent", status: "COMPLETED", confidence: 0.94, executionTimeMs: 8, startedAt: now },
    { agent: "policy-engine", status: "COMPLETED", confidence: 0.98, executionTimeMs: 5, startedAt: now },
    { agent: "risk-engine", status: "COMPLETED", confidence: 0.92, executionTimeMs: 15, startedAt: now },
    { agent: "prompt-rewriter", status: rewrittenPrompt ? "COMPLETED" : "SKIPPED", confidence: 0.89, executionTimeMs: 18, startedAt: now },
    { agent: "llm-adapter", status: decision === "BLOCK" ? "SKIPPED" : "COMPLETED", confidence: 0.95, executionTimeMs: 3, startedAt: now },
    { agent: "audit-logger", status: "COMPLETED", confidence: 1.0, executionTimeMs: 2, startedAt: now },
    { agent: "memory-agent", status: "COMPLETED", confidence: 0.97, executionTimeMs: 4, startedAt: now },
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

// Mission Control Components
const ThreatRadar = memo(function ThreatRadar({ active, riskScore }: { active: boolean; riskScore: number }) {
  const color = riskScore >= 80 ? "#ef4444" : riskScore >= 60 ? "#f97316" : riskScore >= 35 ? "#eab308" : "#22c55e"
  return (
    <div className="relative w-48 h-48">
      <svg viewBox="0 0 192 192" className="w-full h-full">
        <defs>
          <radialGradient id="radarGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={color} stopOpacity={0.15} />
            <stop offset="50%" stopColor={color} stopOpacity={0.05} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </radialGradient>
        </defs>
        <circle cx="96" cy="96" r="90" fill="none" stroke="rgba(11,130,122,0.15)" strokeWidth="1" />
        <circle cx="96" cy="96" r="60" fill="none" stroke="rgba(11,130,122,0.15)" strokeWidth="1" />
        <circle cx="96" cy="96" r="30" fill="none" stroke="rgba(11,130,122,0.15)" strokeWidth="1" />
        <line x1="96" y1="6" x2="96" y2="186" stroke="rgba(11,130,122,0.1)" strokeWidth="1" />
        <line x1="6" y1="96" x2="186" y2="96" stroke="rgba(11,130,122,0.1)" strokeWidth="1" />
        <line x1="28" y1="28" x2="164" y2="164" stroke="rgba(11,130,122,0.1)" strokeWidth="1" />
        <line x1="164" y1="28" x2="28" y2="164" stroke="rgba(11,130,122,0.1)" strokeWidth="1" />
        {active && (
          <>
            <motion.path
              d="M96 6 A90 90 0 0 1 186 96"
              fill="none"
              stroke={color}
              strokeWidth="2"
              strokeOpacity={0.4}
              strokeLinecap="round"
              animate={{ pathLength: [0, 1] }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            />
            <motion.path
              d="M96 6 A90 90 0 0 1 186 96"
              fill="none"
              stroke={color}
              strokeWidth="1"
              strokeOpacity={0.2}
              strokeLinecap="round"
              animate={{ pathLength: [0.5, 0] }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear", delay: 1 }}
            />
          </>
        )}
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <motion.div
          className="w-16 h-16 rounded-full flex items-center justify-center"
          style={{ background: `radial-gradient(circle, ${color}20, ${color}00)` }}
          animate={{ scale: active ? [1, 1.1, 1] : 1 }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          <RiskGauge score={riskScore} size="sm" />
        </motion.div>
      </div>
      <div className="absolute bottom-2 left-1/2 -translate-x-1/2 text-center">
        <p className="text-[10px] font-medium uppercase tracking-wider text-text-muted">THREAT RADAR</p>
        <p className="text-[11px] mono font-bold" style={{ color }}>{riskScore}</p>
      </div>
    </div>
  )
})

const PipelineVisualization = memo(function PipelineVisualization({ 
  agentStates, 
  cursor, 
  running,
  elapsed 
}: { 
  agentStates: Record<string, AgentTraceEntry>
  cursor: number
  running: boolean
  elapsed: number
}) {
  const nodes = AGENTS.map((id, i) => {
    const meta = AGENT_META[id] ?? { label: id, icon: Bot, desc: "" }
    const state = agentStates[id]
    const isCurrent = i === cursor
    const isDone = (state?.status === "COMPLETED")
    const isSkipped = state?.status === "SKIPPED"
    return { id, meta, state, isCurrent, isDone, isSkipped, index: i }
  })

  return (
    <div className="relative">
      {/* Connection lines */}
      <svg className="absolute left-[32px] top-0 bottom-0 w-4 pointer-events-none" viewBox="0 0 16 400" preserveAspectRatio="none">
        <defs>
          <linearGradient id="flowGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#0b827a" stopOpacity={0.6} />
            <stop offset="50%" stopColor="#0b827a" stopOpacity={0.2} />
            <stop offset="100%" stopColor="#0b827a" stopOpacity={0} />
          </linearGradient>
        </defs>
        {nodes.slice(0, -1).map((_, i) => (
          <motion.line
            key={`conn-${i}`}
            x1="8" y1={i * 50 + 44}
            x2="8" y2={i * 50 + 94}
            stroke={nodes[i].isDone || nodes[i+1].isDone ? "url(#flowGrad)" : "rgba(11,130,122,0.15)"}
            strokeWidth={2}
            strokeDasharray={running && (nodes[i].isCurrent || nodes[i+1].isCurrent) ? "8 8" : "0"}
            strokeLinecap="round"
            animate={running && (nodes[i].isCurrent || nodes[i+1].isCurrent) ? { strokeDashoffset: [-16, 16] } : undefined}
            transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
          />
        ))}
        {running && cursor < AGENTS.length && (
          <motion.g
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{ y: cursor * 50 + 16 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          >
            <circle cx="8" cy="0" r="3.5" fill="#0ea79c" />
            <circle cx="8" cy="0" r="7" fill="#0ea79c" opacity="0.35">
              <animate attributeName="r" values="4;9;4" dur="1.1s" repeatCount="indefinite" />
              <animate attributeName="opacity" values="0.5;0.1;0.5" dur="1.1s" repeatCount="indefinite" />
            </circle>
          </motion.g>
        )}
      </svg>

      <div className="flex flex-col gap-0">
        {nodes.map((node, i) => (
          <motion.div
            key={node.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.06 }}
            className="relative flex items-center gap-4 pl-12"
          >
            {/* Node */}
            <motion.div
              className="relative flex-shrink-0 flex h-12 w-12 items-center justify-center rounded-xl"
              animate={{
                scale: node.isCurrent && running ? [1, 1.08, 1] : 1,
                boxShadow: node.isCurrent && running 
                  ? ["0 0 0 rgba(11,130,122,0)", "0 0 30px rgba(11,130,122,0.4)", "0 0 0 rgba(11,130,122,0)"] 
                  : undefined,
              }}
              transition={{
                duration: 1.2,
                repeat: node.isCurrent && running ? Infinity : 0,
              }}
              style={{
                background: node.isDone 
                  ? "linear-gradient(135deg, #22c55e, #16a34a)"
                  : node.isCurrent && running
                  ? "linear-gradient(135deg, #0b827a, #0ea79c)"
                  : node.isSkipped
                  ? "rgba(255,255,255,0.05)"
                  : "rgba(255,255,255,0.03)",
                border: node.isDone 
                  ? "1px solid rgba(34,197,94,0.4)"
                  : node.isCurrent && running
                  ? "1px solid rgba(11,130,122,0.6)"
                  : "1px solid rgba(255,255,255,0.08)",
              }}
            >
              <node.meta.icon 
                className={cn("h-5 w-5", node.isDone || (node.isCurrent && running) ? "text-white" : "text-text-muted")} 
              />
              <AnimatePresence mode="popLayout">
                {node.isDone ? (
                  <motion.span 
                    key="done" 
                    initial={{ scale: 0, rotate: -90 }} 
                    animate={{ scale: 1, rotate: 0 }} 
                    transition={{ type: "spring", stiffness: 500, damping: 25 }}
                    className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-status-low text-white text-[9px]"
                  >
                    ✓
                  </motion.span>
                ) : node.isCurrent && running ? (
                  <motion.span 
                    key="running" 
                    animate={{ rotate: 360 }} 
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-accent text-white text-[9px]"
                  >
                    ⟳
                  </motion.span>
                ) : node.isSkipped ? (
                  <motion.span 
                    key="skipped" 
                    initial={{ scale: 0 }} 
                    animate={{ scale: 1 }}
                    className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-text-muted text-white text-[9px]"
                  >
                    −
                  </motion.span>
                ) : null}
              </AnimatePresence>
            </motion.div>

            {/* Info panel */}
            <motion.div
              className="flex-1 min-w-0 p-3 rounded-xl transition-all"
              style={{
                background: node.isCurrent && running 
                  ? "rgba(11,130,122,0.08)"
                  : node.isDone
                  ? "rgba(34,197,94,0.05)"
                  : "rgba(255,255,255,0.02)",
                border: node.isCurrent && running 
                  ? "1px solid rgba(11,130,122,0.3)"
                  : node.isDone
                  ? "1px solid rgba(34,197,94,0.2)"
                  : "1px solid transparent",
              }}
              animate={{
                boxShadow: node.isCurrent && running 
                  ? "0 0 24px rgba(11,130,122,0.15)" 
                  : "none",
              }}
            >
              <div className="flex items-center justify-between gap-2">
                <p className="text-xs font-medium text-text-primary truncate">{node.meta.label}</p>
                <div className="flex items-center gap-1.5">
                  {node.isCurrent && running && (
                    <motion.span
                      animate={{ opacity: [0.4, 1, 0.4] }}
                      transition={{ duration: 1, repeat: Infinity }}
                      className="flex h-1.5 w-1.5 rounded-full bg-accent-light"
                    />
                  )}
                  {node.isDone && !node.isSkipped && (
                    <CheckCircle2 className="h-3.5 w-3.5 text-status-low" />
                  )}
                  {node.isSkipped && (
                    <XCircle className="h-3.5 w-3.5 text-text-muted" />
                  )}
                </div>
              </div>
              <p className="mt-0.5 line-clamp-1 text-[10px] text-text-muted">{node.meta.desc}</p>
              <div className="mt-1.5 flex items-center gap-3 text-[10px]">
                {node.state && node.isDone ? (
                  <>
                    <span className="mono text-accent-light">{node.state.executionTimeMs}ms</span>
                    <span className="mono text-text-muted">conf {(node.state.confidence * 100).toFixed(0)}%</span>
                  </>
                ) : node.isCurrent && running ? (
                  <span className="mono text-accent-light">running… {elapsed}ms</span>
                ) : (
                  <span className="mono text-text-muted/50">awaiting…</span>
                )}
              </div>
            </motion.div>
          </motion.div>
        ))}
      </div>
    </div>
  )
})

const LiveRiskMeter = memo(function LiveRiskMeter({ score, active, running }: { score: number; active: boolean; running: boolean }) {
  const color = score >= 80 ? "#ef4444" : score >= 60 ? "#f97316" : score >= 35 ? "#eab308" : "#22c55e"
  const label = score >= 80 ? "CRITICAL" : score >= 60 ? "HIGH" : score >= 35 ? "MEDIUM" : score >= 15 ? "LOW" : "SAFE"
  
  return (
    <div className="glass-card card-glow p-5">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Zap className="h-4 w-4" style={{ color }} />
          <span className="text-xs font-medium uppercase tracking-wider text-text-muted">LIVE RISK METER</span>
        </div>
        <Badge variant={score >= 60 ? "danger" : score >= 35 ? "warning" : "success"}>{label}</Badge>
      </div>
      <div className="relative h-32 flex items-center justify-center">
        <svg viewBox="0 0 200 200" className="w-full h-full -rotate-90">
          <circle cx="100" cy="100" r="85" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="12" />
          <motion.circle
            cx="100" cy="100" r="85"
            fill="none"
            stroke={color}
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={`${(score / 100) * 534} 534`}
            style={{ filter: active ? "drop-shadow(0 0 8px " + color + ")" : "none" }}
            animate={running && active ? { strokeDasharray: [`${(score / 100) * 534} 534`, `${Math.min((score + Math.random() * 5) / 100, 1) * 534} 534`] } : undefined}
            transition={{ duration: 0.5, repeat: Infinity, repeatType: "mirror", ease: "easeInOut" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className="mono font-bold text-4xl"
            style={{ color }}
            animate={{ scale: running && active ? [1, 1.03, 1] : 1 }}
            transition={{ duration: 0.8, repeat: Infinity }}
          >
            {score}
          </motion.span>
          <span className="text-[10px] uppercase tracking-widest text-text-muted">risk score</span>
        </div>
      </div>
      <div className="mt-4 flex items-center justify-between text-[11px] text-text-muted">
        <span>Threshold: 35 (Medium)</span>
        <span>Updated: {running ? "live" : "static"}</span>
      </div>
    </div>
  )
})

function stageFindings(result: PipelineResult, agent: string): string | null {
  if (agent === "secret-detection-agent") return result.secrets.length ? `${result.secrets.length} found` : "clean"
  if (agent === "policy-engine") return result.violations.length ? `${result.violations.length} violations` : "no match"
  if (agent === "risk-engine") return `score ${result.riskScore}`
  if (agent === "prompt-rewriter") return result.rewrittenPrompt ? "rewritten" : "unchanged"
  if (agent === "llm-adapter") return result.status === "BLOCKED" ? "blocked" : "routed"
  if (agent === "audit-logger") return result.auditLogId ? "committed" : "failed"
  if (agent === "memory-agent") return "context stored"
  return null
}

export default function ScannerPage() {
  const [prompt, setPrompt] = useState("")
  const [provider, setProvider] = useState<string>("openai")
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState<PipelineResult | null>(null)
  const [cursor, setCursor] = useState(0)
  const [agentStates, setAgentStates] = useState<Record<string, AgentTraceEntry>>({})
  const [error, setError] = useState<string | null>(null)
  const [elapsed, setElapsed] = useState(0)
  const [replaySpeed, setReplaySpeed] = useState(1)
  const [replaying, setReplaying] = useState(false)
  const [replayPaused, setReplayPaused] = useState(false)
  const [replayIdx, setReplayIdx] = useState(0)
  const [demoMode, setDemoMode] = useState(true)
  const resultRef = useRef<HTMLDivElement>(null)
  const appliedRef = useRef<Set<string>>(new Set())
  const runIdRef = useRef(0)
  const startRef = useRef(0)
  const unsubRef = useRef<(() => void) | null>(null)
  const replayTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const replayRunRef = useRef(0)

  useEffect(() => {
    return () => unsubRef.current?.()
  }, [])

  useEffect(() => {
    if (!running) return
    const t = setInterval(() => setElapsed(Math.round(performance.now() - startRef.current)), 100)
    return () => clearInterval(t)
  }, [running])

  const applyTrace = useCallback((entry: AgentTraceEntry) => {
    setAgentStates((prev) => ({ ...prev, [entry.agent]: entry }))
    const idx = AGENTS.indexOf(entry.agent)
    if (idx >= 0) {
      appliedRef.current.add(entry.agent)
      setCursor((c) => {
        let next = Math.max(c, idx + 1)
        while (next < AGENTS.length && appliedRef.current.has(AGENTS[next])) next++
        return next
      })
    }
  }, [])

  const replayTrace = useCallback((trace: AgentTraceEntry[]) => {
    let i = 0
    const timer = setInterval(() => {
      if (i >= trace.length) {
        clearInterval(timer)
        return
      }
      const entry = trace[i]
      if (appliedRef.current.has(entry.agent)) {
        i++
        return
      }
      applyTrace(entry)
      i++
    }, 220)
    return timer
  }, [applyTrace])

  const runScan = useCallback(async (text?: string) => {
    const value = (text ?? prompt).trim()
    if (!value) return
    const runId = ++runIdRef.current
    setRunning(true)
    setError(null)
    setResult(null)
    setAgentStates({})
    setCursor(0)
    appliedRef.current = new Set()
    startRef.current = performance.now()
    setElapsed(0)

    const unsubscribe = subscribeAgentUpdates((entry) => {
      if (runId === runIdRef.current && !appliedRef.current.has(entry.agent)) applyTrace(entry)
    })
    unsubRef.current?.()
    unsubRef.current = unsubscribe

    try {
      let res: PipelineResult
      if (demoMode) {
        res = mockScan(value, provider)
      } else {
        try {
          res = await api.scan(value, provider)
        } catch (apiError) {
          console.warn("API scan failed, using mock:", apiError)
          res = mockScan(value, provider)
        }
      }
      
      if (runId !== runIdRef.current) return
      const timer = replayTrace(res.agentTrace)
      setResult(res)
      setTimeout(() => {
        clearInterval(timer)
        if (runId === runIdRef.current) {
          setAgentStates((prev) => {
            const next = { ...prev }
            for (const t of res.agentTrace) next[t.agent] = t
            return next
          })
          setCursor(AGENTS.length)
        }
        unsubRef.current?.()
        unsubRef.current = null
        resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })
      }, 1900)
    } catch (e) {
      if (runId !== runIdRef.current) return
      setError(e instanceof Error ? e.message : "Scan failed")
    } finally {
      if (runId === runIdRef.current) {
        setTimeout(() => {
          if (runId === runIdRef.current) setRunning(false)
        }, 2200)
      }
    }
  }, [prompt, provider, applyTrace, replayTrace, demoMode])

  const completed = Object.values(agentStates).filter((s) => s.status === "COMPLETED").length
  const progress = Math.round((completed / AGENTS.length) * 100)

  const clearReplayTimer = () => {
    if (replayTimerRef.current) {
      clearTimeout(replayTimerRef.current)
      replayTimerRef.current = null
    }
  }

  const applyReplayFrame = useCallback((entry: AgentTraceEntry) => {
    setAgentStates((prev) => ({ ...prev, [entry.agent]: entry }))
    const idx = AGENTS.indexOf(entry.agent)
    setCursor((c) => Math.max(c, idx + 1))
  }, [])

  const stepReplay = useCallback(
    (trace: AgentTraceEntry[], startAt: number) => {
      clearReplayTimer()
      if (startAt >= trace.length) {
        setReplaying(false)
        setReplayPaused(false)
        return
      }
      const entry = trace[startAt]
      applyReplayFrame(entry)
      setReplayIdx(startAt + 1)
      replayTimerRef.current = setTimeout(
        () => stepReplay(trace, startAt + 1),
        Math.max(120, 280 / replaySpeed),
      )
    },
    [applyReplayFrame, replaySpeed],
  )

  const startReplay = useCallback(
    (fromIdx = 0) => {
      if (!result) return
      const runId = ++replayRunRef.current
      setReplaying(true)
      setReplayPaused(false)
      setAgentStates({})
      setCursor(0)
      setReplayIdx(fromIdx)
      const trace = result.agentTrace
      const applyFrom = (i: number) => {
        setAgentStates({})
        setCursor(0)
        for (let k = 0; k < i; k++) applyReplayFrame(trace[k])
        if (i < trace.length) {
          stepReplay(trace, i)
        } else {
          setReplaying(false)
          setReplayPaused(false)
        }
      }
      if (fromIdx > 0) {
        applyFrom(fromIdx)
      } else {
        stepReplay(trace, 0)
      }
      return () => {
        if (runId === replayRunRef.current) clearReplayTimer()
      }
    },
    [result, applyReplayFrame, stepReplay],
  )

  const toggleReplay = () => {
    if (!result) return
    if (replaying && !replayPaused) {
      setReplayPaused(true)
      clearReplayTimer()
    } else if (replaying && replayPaused) {
      setReplayPaused(false)
      stepReplay(result.agentTrace, replayIdx)
    } else {
      startReplay()
    }
  }

  const stepForward = () => {
    if (!result) return
    clearReplayTimer()
    const trace = result.agentTrace
    if (replayIdx < trace.length) {
      applyReplayFrame(trace[replayIdx])
      setReplayIdx(replayIdx + 1)
    }
  }

  const stepBackward = () => {
    if (!result) return
    clearReplayTimer()
    const trace = result.agentTrace
    if (replayIdx <= 0) return
    const newIdx = replayIdx - 1
    setAgentStates({})
    setCursor(0)
    for (let k = 0; k < newIdx; k++) applyReplayFrame(trace[k])
    setReplayIdx(newIdx)
  }

  const exportTrace = () => {
    if (!result) return
    const payload = {
      product: "SentinelX AI Governance Firewall",
      type: "Agent execution trace",
      pipelineId: result.pipelineId,
      decision: result.decision,
      riskScore: result.riskScore,
      threatLevel: result.threatLevel,
      latencyMs: result.latencyMs,
      provider: result.provider,
      model: result.model,
      exportedAt: new Date().toISOString(),
      agentTrace: result.agentTrace,
    }
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `sentinelx-trace-${result.pipelineId.slice(0, 8)}.json`
    a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }

  useEffect(() => {
    return () => {
      clearReplayTimer()
      replayRunRef.current++
    }
  }, [])

  return (
    <div className="space-y-6">
      <PageHeader
        title="Prompt Scanner"
        description="Submit a prompt and watch the full SentinelX agent pipeline inspect, detect, score, and sanitize it in real time — before it ever reaches an LLM."
      />

      <div className="glass-card p-6">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent-light opacity-60" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-accent-light" />
            </span>
            <span className="text-xs font-medium uppercase tracking-wider text-text-secondary">
              Inspection Console
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-text-muted">Route to</span>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              aria-label="Route to provider"
              className="rounded-lg border border-border-default bg-bg-tertiary px-3 py-1.5 text-xs text-text-primary outline-none transition-colors hover:border-border-strong focus:border-accent"
            >
              {PROVIDERS.map((p) => (
                <option key={p.id} value={p.id}>{p.label}</option>
              ))}
            </select>
            <button
              onClick={() => setDemoMode(!demoMode)}
              className={cn(
                "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-all",
                demoMode
                  ? "bg-accent/10 border-accent/40 text-accent-light hover:bg-accent/20"
                  : "bg-white/[0.03] border-border-default text-text-secondary hover:bg-white/[0.06] hover:border-border-strong"
              )}
              aria-pressed={demoMode}
              title={demoMode ? "Disable demo mode (use real API)" : "Enable demo mode (works offline)"}
            >
              <Zap className="h-3.5 w-3.5" />
              {demoMode ? "Demo Mode: ON" : "Demo Mode: OFF"}
            </button>
          </div>
        </div>

        <div className="relative">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            aria-label="Prompt to scan"
            placeholder="Paste or type a prompt here… e.g. “Summarize this HR salary sheet with employee emails and phone numbers”"
            rows={4}
            className="w-full resize-none rounded-xl border border-border-default bg-bg-secondary/60 p-4 pr-14 text-sm text-text-primary placeholder:text-text-muted outline-none transition-all focus:border-accent focus:shadow-glow"
          />
          {running && (
            <div className="pointer-events-none absolute inset-x-0 top-0 h-full overflow-hidden rounded-xl">
              <div className="scanline" />
            </div>
          )}
          <button
            onClick={() => runScan()}
            disabled={running || !prompt.trim()}
            className="absolute right-3 top-3 flex h-9 w-9 items-center justify-center rounded-lg bg-accent text-white shadow-glow transition-all hover:bg-accent-light disabled:cursor-not-allowed disabled:opacity-40"
            aria-label="Scan prompt"
          >
            {running ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </button>
        </div>

        <div className="mt-4">
          <div className="mb-2 flex items-center gap-2">
            <Sparkles className="h-3.5 w-3.5 text-accent-light" />
            <span className="text-[11px] font-medium uppercase tracking-wider text-text-muted">
              Demo scenarios
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            {DEMO_SCENARIOS.map((s) => (
              <button
                key={s.label}
                onClick={() => { setPrompt(s.prompt); runScan(s.prompt) }}
                disabled={running}
                className="group flex items-center gap-1.5 rounded-lg border border-border-default bg-white/[0.02] px-2.5 py-1.5 text-[11px] font-medium text-text-secondary transition-all hover:border-accent/50 hover:bg-accent/5 hover:text-text-primary hover:shadow-glow disabled:cursor-not-allowed disabled:opacity-40"
              >
                <s.icon className="h-3 w-3 text-text-muted transition-colors group-hover:text-accent-light" />
                {s.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {running && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          {/* Mission Control Header */}
          <div className="glass-card card-glow p-5">
            <div className="mb-5 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <Bot className="h-4 w-4 text-accent-light pulse-dot" />
                <h2 className="text-sm font-semibold">Mission Control · Agent Pipeline Executing</h2>
                <Badge variant="info">LIVE</Badge>
              </div>
              <span className="mono text-xs text-accent-light">
                stage {Math.min(completed + 1, AGENTS.length)}/8 · {elapsed}ms
              </span>
            </div>

            <div className="mb-6 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
              <motion.div
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.4 }}
                className="h-full rounded-full bg-gradient-to-r from-accent-dark via-accent to-accent-light shadow-glow"
              />
            </div>

            <div className="grid gap-4 lg:grid-cols-3">
              {/* Pipeline Visualization */}
              <div className="lg:col-span-2">
                <PipelineVisualization agentStates={agentStates} cursor={cursor} running={running} elapsed={elapsed} />
              </div>

              {/* Right column: Radar + Live Risk */}
              <div className="space-y-4">
                <div className="glass-card card-glow p-5 flex flex-col items-center">
                  <div className="flex items-center gap-2 self-start mb-3">
                    <Radar className="h-4 w-4 text-accent-light" />
                    <span className="text-xs font-medium uppercase tracking-wider text-text-muted">Threat Radar</span>
                  </div>
                  <ThreatRadar active={running} riskScore={result?.riskScore ?? Math.min(progress * 1.2, 80)} />
                </div>
                <LiveRiskMeter score={result?.riskScore ?? Math.min(progress * 1.3, 90)} active={running} running={running} />
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {error && (
        <div className="rounded-xl border border-status-critical/30 bg-critical p-4 text-sm text-status-critical">
          {error}
        </div>
      )}

      {result && !running && (
        <motion.div ref={resultRef} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="space-y-4 scroll-mt-20">
          <div className={cn("glass-card p-5", result.threatLevel === "CRITICAL" && "glass-card-accent border-status-critical/30")}>
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <RiskGauge score={result.riskScore} />
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-semibold">{result.decision}</h3>
                    <DecisionBadge decision={result.decision} />
                  </div>
                  <p className="mt-1 max-w-md text-xs leading-relaxed text-text-secondary">
                    {result.violations[0]?.reason ?? "No policy violations — prompt transmitted safely to the model."}
                  </p>
                  {result.violations[0] && (
                    <p className="mt-1 text-[11px] text-accent-light">Recommended: {result.violations[0].recommendation}</p>
                  )}
                </div>
              </div>
              <div className="space-y-1.5 text-right">
                <p className="mono text-[11px] text-text-muted">pipeline {result.pipelineId.slice(0, 8)}</p>
                <p className="mono text-[11px] text-text-muted">{result.provider} / {result.model}</p>
                <p className="mono text-[11px] text-text-muted">{result.latencyMs}ms total</p>
                <Badge variant={result.decision === "ALLOW" ? "success" : result.decision === "BLOCK" ? "danger" : "warning"}>
                  {result.status}
                </Badge>
              </div>
            </div>
          </div>

          {/* Threat Radar & Live Risk Meter - Prominent Analysis */}
          <div className="grid gap-4 lg:grid-cols-3">
            <div className="lg:col-span-1">
              <div className="glass-card card-glow p-5 flex flex-col items-center">
                <div className="flex items-center gap-2 self-start mb-3">
                  <Radar className="h-4 w-4 text-accent-light" />
                  <span className="text-xs font-medium uppercase tracking-wider text-text-muted">Threat Radar</span>
                </div>
                <ThreatRadar active={true} riskScore={result.riskScore} />
                <div className="mt-3 text-center">
                  <p className="text-[10px] uppercase tracking-wider text-text-muted">Threat Level</p>
                  <p className="text-lg font-bold mono" style={{ color: result.riskScore >= 80 ? "#ef4444" : result.riskScore >= 60 ? "#f97316" : result.riskScore >= 35 ? "#eab308" : "#22c55e" }}>
                    {result.threatLevel}
                  </p>
                </div>
              </div>
            </div>
            <div className="lg:col-span-2">
              <LiveRiskMeter score={result.riskScore} active={true} running={false} />
            </div>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <div className="glass-card p-5">
              <div className="mb-3 flex items-center justify-between">
                <h3 className="text-sm font-semibold">Original Prompt</h3>
                <Badge variant="outline">{result.secrets.length} sensitive entit{result.secrets.length === 1 ? "y" : "ies"}</Badge>
              </div>
              <HighlightedPrompt text={result.originalPrompt} secrets={result.secrets} />
              {result.secrets.length > 0 && (
                <div className="mt-4 space-y-2">
                  {result.secrets.map((s, i) => (
                    <div key={i} className="flex items-center justify-between gap-3 rounded-lg border border-border-default bg-white/[0.02] px-3 py-2">
                      <div className="flex items-center gap-2">
                        <SeverityBadge severity={s.severity} />
                        <span className="text-xs text-text-secondary">{s.label}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="mono max-w-[180px] truncate rounded bg-white/[0.04] px-2 py-0.5 text-[10px] text-status-critical">{s.match}</span>
                        <ArrowRight className="h-3 w-3 text-text-muted" />
                        <span className="mono max-w-[180px] truncate rounded bg-accent/10 px-2 py-0.5 text-[10px] text-accent-light">{s.redacted}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="glass-card p-5">
              <div className="mb-3 flex items-center justify-between">
                <h3 className="text-sm font-semibold">Sanitized Prompt</h3>
                {result.rewrittenPrompt ? <Badge variant="warning">Rewritten</Badge> : <Badge variant="success">Unchanged</Badge>}
              </div>
              {result.rewrittenPrompt ? (
                <div className="rounded-xl border border-accent/25 bg-accent/5 p-4 text-sm leading-relaxed text-text-primary">
                  {result.rewrittenPrompt}
                </div>
              ) : (
                <div className="rounded-xl border border-border-default bg-white/[0.02] p-4 text-sm leading-relaxed text-text-secondary">
                  {result.originalPrompt}
                </div>
              )}
              {result.rewrittenPrompt && (
                <p className="mt-3 flex items-center gap-1.5 text-[11px] text-accent-light">
                  <Wand2 className="h-3.5 w-3.5" />
                  Intent preserved · sensitive entities removed before reaching the model
                </p>
              )}
            </div>
          </div>

          {result.violations.length > 0 && (
            <div className="glass-card p-5">
              <div className="mb-3 flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-status-high" />
                <h3 className="text-sm font-semibold">Policy Violations</h3>
              </div>
              <div className="space-y-3">
                {result.violations.map((v, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.08 }}
                    className="rounded-lg border border-border-default bg-white/[0.02] p-4"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <SeverityBadge severity={v.severity} />
                        <span className="text-xs font-medium text-text-primary">{v.policyName}</span>
                      </div>
                      <span className="tech-chip">{v.regulation} · {v.category}</span>
                    </div>
                    <p className="mt-2 text-xs leading-relaxed text-text-secondary">{v.reason}</p>
                    <p className="mt-1.5 flex items-start gap-1.5 text-[11px] text-accent-light">
                      <Sparkles className="mt-0.5 h-3 w-3 flex-shrink-0" />
                      {v.recommendation}
                    </p>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          <div className="glass-card p-5">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-sm font-semibold">Agent Execution Trace</h3>
              <span className="text-[11px] text-text-muted">{result.agentTrace.length} stages</span>
            </div>
            <div className="space-y-1">
              {result.agentTrace.map((t, i) => {
                const meta = AGENT_META[t.agent] ?? { label: t.agent, icon: Bot, desc: "" }
                return (
                  <div key={i} className="flex items-center gap-3 rounded-lg px-2 py-1.5">
                    <span className="mono w-6 text-[10px] text-text-muted">{String(i + 1).padStart(2, "0")}</span>
                    <span className="w-4 text-center text-text-muted">
                      {i < result.agentTrace.length - 1 ? <ArrowDown className="h-3 w-3" /> : <CheckCircle2 className="h-3 w-3 text-status-low" />}
                    </span>
                    <span className="w-40 truncate text-xs text-text-secondary">{meta.label}</span>
                    <span className="hidden text-[10px] text-text-muted sm:block">{meta.desc}</span>
                    <div className="ml-auto flex items-center gap-3">
                      {stageFindings(result, t.agent) && <span className="hidden text-[10px] text-status-low md:block">✓ {stageFindings(result, t.agent)}</span>}
                      <span className="mono text-[10px] text-text-muted">{t.executionTimeMs}ms</span>
                      <span className="mono text-[10px] text-accent-light">{Math.round(t.confidence * 100)}%</span>
                      {t.status === "COMPLETED" && <CheckCircle2 className="h-3.5 w-3.5 text-status-low" />}
                      {t.status === "SKIPPED" && <span className="text-[10px] text-text-muted">skipped</span>}
                      {t.status === "FAILED" && <XCircle className="h-3.5 w-3.5 text-status-critical" />}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Replay controls */}
          <div className="glass-card card-glow p-5">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <h3 className="flex items-center gap-2 text-sm font-semibold">
                <Timer className="h-4 w-4 text-accent-light" /> Pipeline Replay
              </h3>
              <div className="flex items-center gap-2">
                <span className="mono text-[10px] text-text-muted">speed</span>
                <input
                  type="range"
                  min={0.5}
                  max={4}
                  step={0.5}
                  value={replaySpeed}
                  onChange={(e) => setReplaySpeed(Number(e.target.value))}
                  className="w-24 cursor-pointer accent-[#0b827a]"
                  aria-label="Replay speed"
                />
                <span className="mono w-8 text-[10px] text-accent-light">{replaySpeed}×</span>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={stepBackward}
                disabled={!result || replayIdx <= 0}
                className="flex h-9 w-9 items-center justify-center rounded-lg border border-border-default bg-white/[0.02] text-text-secondary transition-all hover:border-accent/50 hover:text-accent-light disabled:cursor-not-allowed disabled:opacity-30"
                aria-label="Step backward"
              >
                <StepBack className="h-4 w-4" />
              </button>
              <button
                onClick={toggleReplay}
                className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent text-white shadow-glow transition-all hover:bg-accent-light"
                aria-label={replaying && !replayPaused ? "Pause replay" : "Play replay"}
              >
                {replaying && !replayPaused ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
              </button>
              <button
                onClick={stepForward}
                disabled={!result || replayIdx >= result.agentTrace.length}
                className="flex h-9 w-9 items-center justify-center rounded-lg border border-border-default bg-white/[0.02] text-text-secondary transition-all hover:border-accent/50 hover:text-accent-light disabled:cursor-not-allowed disabled:opacity-30"
                aria-label="Step forward"
              >
                <StepForward className="h-4 w-4" />
              </button>
              <button
                onClick={() => startReplay()}
                className="flex h-9 items-center gap-1.5 rounded-lg border border-border-default bg-white/[0.02] px-3 text-[11px] font-medium text-text-secondary transition-all hover:border-accent/50 hover:text-accent-light"
              >
                <FastForward className="h-3.5 w-3.5" /> Replay all
              </button>
              <span className="mono ml-1 text-[10px] text-text-muted">
                frame {replayIdx}/{result.agentTrace.length}
                {replaying && !replayPaused && <span className="ml-2 text-status-low">● replaying</span>}
                {replaying && replayPaused && <span className="ml-2 text-status-medium">⏸ paused</span>}
              </span>
              <button
                onClick={exportTrace}
                className="ml-auto flex h-9 items-center gap-1.5 rounded-lg border border-accent/40 bg-accent/10 px-3 text-[11px] font-medium text-accent-light transition-all hover:bg-accent/20"
              >
                <FileDown className="h-3.5 w-3.5" /> Export trace
              </button>
            </div>
          </div>
        </motion.div>
      )}

      {!result && !running && !error && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card flex flex-col items-center justify-center gap-4 py-16 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-accent/30 bg-accent/10 shadow-glow">
            <Play className="h-6 w-6 text-accent-light" />
          </div>
          <div>
            <p className="text-sm font-medium text-text-primary">Ready for inspection</p>
            <p className="mt-1 max-w-md text-xs text-text-muted">
              The pipeline: Inspector → Secret Detection → Policy Engine → Risk Engine → Rewriter → LLM Gateway → Audit Logger → Memory
            </p>
          </div>
          <div className="mt-2 flex flex-wrap items-center justify-center gap-2 text-[10px] text-text-muted">
            {AGENTS.map((id, i) => (
              <span key={id} className="flex items-center gap-1.5">
                {i > 0 && <ArrowRight className="h-3 w-3 opacity-50" />}
                {AGENT_META[id]?.label.replace(/ Agent|Agent /g, "").replace(/ Engine/g, "")}
              </span>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  )
}

function HighlightedPrompt({ text, secrets }: { text: string; secrets: PipelineResult["secrets"] }) {
  if (secrets.length === 0) {
    return (
      <div className="rounded-xl border border-border-default bg-white/[0.02] p-4 text-sm leading-relaxed text-text-secondary">
        {text}
      </div>
    )
  }
  const parts: React.ReactNode[] = []
  let last = 0
  for (const s of secrets) {
    const start = s.position.start
    const end = s.position.end
    if (start > last) parts.push(<span key={`t-${last}`}>{text.slice(last, start)}</span>)
    parts.push(
      <mark key={`s-${start}`} className="rounded bg-status-critical/20 px-1 py-0.5 text-status-critical">
        {text.slice(start, end)}
      </mark>,
    )
    last = end
  }
  if (last < text.length) parts.push(<span key="tail">{text.slice(last)}</span>)
  return (
    <div className="rounded-xl border border-border-default bg-white/[0.02] p-4 text-sm leading-relaxed text-text-primary">
      {parts}
    </div>
  )
}
