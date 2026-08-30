"use client"

import { motion } from "framer-motion"
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Fingerprint,
  GitBranch,
  Gavel,
  Shield,
  Sparkles,
  Wand2,
  Zap,
} from "lucide-react"
import type { AuditRecord, DetectedSecret, PolicyViolation, PipelineResult } from "@/types"
import { Badge, DecisionBadge, SeverityBadge } from "./primitives"
import { cn } from "@/lib/utils"

interface ExplainableData {
  prompt: string
  decision: string
  riskScore: number
  threatLevel: string
  secrets: DetectedSecret[]
  violations: PolicyViolation[]
  rewrittenPrompt: string | null
  rewritten: boolean
}

function toData(r: PipelineResult | AuditRecord): ExplainableData {
  const prompt = "originalPrompt" in r ? (r as PipelineResult).originalPrompt : (r as AuditRecord).prompt
  return {
    prompt,
    decision: r.decision,
    riskScore: r.riskScore,
    threatLevel: r.threatLevel,
    secrets: r.secrets ?? [],
    violations: r.violations ?? [],
    rewrittenPrompt: r.rewrittenPrompt ?? null,
    rewritten: !!r.rewrittenPrompt && r.rewrittenPrompt !== prompt,
  }
}

function contribution(secrets: DetectedSecret[], violations: PolicyViolation[], score: number): Array<{ label: string; weight: number; detail: string; tone: string }> {
  const out: Array<{ label: string; weight: number; detail: string; tone: string }> = []
  if (secrets.length > 0) {
    const worst = secrets.reduce((a, s) => Math.max(a, s.severity === "CRITICAL" ? 40 : s.severity === "HIGH" ? 25 : s.severity === "MEDIUM" ? 12 : 5), 0)
    out.push({
      label: "Sensitive data exposure",
      weight: Math.min(55, worst * (1 + Math.min(secrets.length - 1, 5) * 0.15)),
      detail: `${secrets.length} sensitive entit${secrets.length === 1 ? "y" : "ies"} matched detection patterns with ${Math.round((secrets.reduce((a, s) => a + s.confidence, 0) / secrets.length) * 100)}% average confidence.`,
      tone: "from-status-high to-status-critical",
    })
  }
  if (violations.length > 0) {
    const vScore = violations.reduce((a, v) => a + (v.severity === "CRITICAL" ? 40 : v.severity === "HIGH" ? 25 : v.severity === "MEDIUM" ? 12 : 5) * 1.2, 0)
    out.push({
      label: "Policy violations",
      weight: Math.min(60, vScore),
      detail: `${violations.length} policy pack${violations.length === 1 ? "" : "s"} triggered — ${[...new Set(violations.map((v) => v.regulation))].join(", ") || "corporate policy"}.`,
      tone: "from-status-critical to-status-high",
    })
  }
  if (score >= 35 && out.length === 0) {
    out.push({
      label: "Elevated composite risk",
      weight: Math.min(35, score * 0.4),
      detail: "Composite score crossed the medium threshold without a single dominant trigger.",
      tone: "from-status-medium to-status-high",
    })
  }
  if (out.length === 0) {
    out.push({ label: "Clean request", weight: 5, detail: "No sensitive entities or policy violations detected.", tone: "from-status-low to-status-low" })
  }
  return out.sort((a, b) => b.weight - a.weight)
}

function whyRewritten(d: ExplainableData): string {
  if (!d.rewritten) return ""
  const secretLabels = d.secrets.map((s) => s.label)
  const vioRegs = [...new Set(d.violations.map((v) => v.regulation))]
  if (secretLabels.length > 0 && vioRegs.length > 0) return `Detected ${secretLabels.slice(0, 3).join(", ")} which violates ${vioRegs.slice(0, 3).join(", ")}. Rewriting preserves intent while redacting sensitive entities before the model sees them.`
  if (secretLabels.length > 0) return `Sensitive entit${d.secrets.length === 1 ? "y" : "ies"} (${secretLabels.slice(0, 3).join(", ")}) required redaction. Intent-preserving sanitisation applied.`
  if (vioRegs.length > 0) return `${vioRegs.slice(0, 3).join(", ")} policy constraints required sanitisation of the request body.`
  return "Policy engine flagged the request for sanitisation before transmission."
}

function businessImpact(d: ExplainableData): string {
  if (d.riskScore >= 80) return "Critical regulatory exposure — potential reportable breach (GDPR Art. 33 / HIPAA notification) with fines up to €20M or 4% of global turnover."
  if (d.riskScore >= 60) return "High business impact — credential compromise could enable lateral movement and data exfiltration."
  if (d.riskScore >= 35) return "Moderate impact — potential privacy complaint, audit finding, or reputational damage."
  if (d.riskScore >= 15) return "Limited impact — low-sensitivity data with minor exposure."
  return "No measurable business impact — benign traffic."
}

function decisionTree(d: ExplainableData): Array<{ label: string; state: "pass" | "trigger" | "decision"; detail: string }> {
  const tree: Array<{ label: string; state: "pass" | "trigger" | "decision"; detail: string }> = []
  tree.push({ label: "Inspector Agent", state: d.secrets.length || d.violations.length ? "trigger" : "pass", detail: "Prompt normalised & intent classified" })
  tree.push({ label: "Secret Detection", state: d.secrets.length ? "trigger" : "pass", detail: `${d.secrets.length} entit${d.secrets.length === 1 ? "y" : "ies"} matched` })
  tree.push({ label: "Policy Engine", state: d.violations.length ? "trigger" : "pass", detail: `${d.violations.length} pack${d.violations.length === 1 ? "" : "s"} triggered` })
  tree.push({ label: "Risk Engine", state: d.riskScore >= 35 ? "trigger" : "pass", detail: `Composite score ${d.riskScore}/100` })
  tree.push({ label: d.rewritten ? "Rewriter" : "LLM Gateway", state: "decision", detail: d.decision })
  return tree
}

export function DecisionExplanation({ result }: { result: PipelineResult | AuditRecord }) {
  const d = toData(result)
  const contributions = contribution(d.secrets, d.violations, d.riskScore)
  const maxWeight = Math.max(...contributions.map((c) => c.weight), 1)
  const tree = decisionTree(d)
  const rewriterReason = whyRewritten(d)

  return (
    <div className="space-y-5">
      {/* Why decision */}
      <div className="rounded-xl border border-border-default bg-white/[0.02] p-4">
        <div className="mb-3 flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-accent-light" />
          <h4 className="text-sm font-semibold">Why this decision</h4>
        </div>
        <div className="flex items-center gap-2 text-xs text-text-secondary">
          <span>The request was <DecisionBadge decision={d.decision} /></span>
          <ArrowRight className="h-3 w-3 text-text-muted" />
          <span className="mono text-status-medium">{d.riskScore}/100</span>
          <span className={cn("mono", d.threatLevel === "CRITICAL" ? "text-status-critical" : d.threatLevel === "HIGH" ? "text-status-high" : d.threatLevel === "MEDIUM" ? "text-status-medium" : "text-status-low")}>
            {d.threatLevel}
          </span>
        </div>
      </div>

      {/* Risk contribution */}
      <div className="rounded-xl border border-border-default bg-white/[0.02] p-4">
        <div className="mb-3 flex items-center gap-2">
          <Activity className="h-4 w-4 text-status-high" />
          <h4 className="text-sm font-semibold">Risk contribution</h4>
        </div>
        <div className="space-y-2.5">
          {contributions.map((c, i) => (
            <div key={c.label}>
              <div className="flex items-center justify-between text-xs">
                <span className="font-medium text-text-primary">{c.label}</span>
                <span className="mono text-text-secondary">+{Math.round(c.weight)}</span>
              </div>
              <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(c.weight / maxWeight) * 100}%` }}
                  transition={{ duration: 0.7, delay: 0.1 + i * 0.06 }}
                  className={cn("h-full rounded-full bg-gradient-to-r", c.tone)}
                />
              </div>
              <p className="mt-1 text-[11px] leading-relaxed text-text-muted">{c.detail}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Decision tree */}
      <div className="rounded-xl border border-border-default bg-white/[0.02] p-4">
        <div className="mb-3 flex items-center gap-2">
          <GitBranch className="h-4 w-4 text-accent-light" />
          <h4 className="text-sm font-semibold">Decision tree</h4>
        </div>
        <div className="space-y-0">
          {tree.map((node, i) => (
            <div key={node.label}>
              <div className="flex items-center gap-2.5">
                <span
                  className={cn(
                    "flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full border text-[10px]",
                    node.state === "trigger"
                      ? "border-status-high/40 bg-high text-status-high"
                      : node.state === "decision"
                        ? "border-accent/40 bg-accent/10 text-accent-light"
                        : "border-status-low/30 bg-low text-status-low",
                  )}
                >
                  {node.state === "trigger" ? <AlertTriangle className="h-3 w-3" /> : node.state === "decision" ? <CheckCircle2 className="h-3 w-3" /> : <CheckCircle2 className="h-3 w-3" />}
                </span>
                <div className="flex min-w-0 flex-1 items-center justify-between gap-2">
                  <div>
                    <p className="text-xs font-medium text-text-primary">{node.label}</p>
                    <p className="text-[10px] text-text-muted">{node.detail}</p>
                  </div>
                  <Badge variant={node.state === "trigger" ? "warning" : node.state === "decision" ? "info" : "success"}>
                    {node.state === "trigger" ? "triggered" : node.state === "decision" ? d.decision : "passed"}
                  </Badge>
                </div>
              </div>
              {i < tree.length - 1 && (
                <div className="ml-3 h-4 w-px bg-border-strong" aria-hidden />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Why rewritten */}
      {d.rewritten && rewriterReason && (
        <div className="rounded-xl border border-accent/25 bg-accent/[0.04] p-4">
          <div className="mb-2 flex items-center gap-2">
            <Wand2 className="h-4 w-4 text-accent-light" />
            <h4 className="text-sm font-semibold">Why it was rewritten</h4>
          </div>
          <p className="text-xs leading-relaxed text-text-secondary">{rewriterReason}</p>
          {d.rewrittenPrompt && (
            <div className="mt-3 rounded-lg border border-accent/20 bg-white/[0.02] p-3">
              <p className="mb-1 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-accent-light">
                <Wand2 className="h-3 w-3" /> Sanitized output
              </p>
              <p className="text-xs leading-relaxed text-text-primary">{d.rewrittenPrompt}</p>
            </div>
          )}
        </div>
      )}

      {/* Policy impact */}
      {d.violations.length > 0 && (
        <div className="rounded-xl border border-border-default bg-white/[0.02] p-4">
          <div className="mb-3 flex items-center gap-2">
            <Gavel className="h-4 w-4 text-status-high" />
            <h4 className="text-sm font-semibold">Policy impact</h4>
          </div>
          <div className="space-y-2">
            {d.violations.map((v, i) => (
              <div key={i} className="flex items-start gap-2.5 rounded-lg bg-white/[0.02] p-2.5">
                <SeverityBadge severity={v.severity} />
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium text-text-primary">{v.policyName}</p>
                  <p className="text-[10px] text-text-muted">{v.regulation} · rule {v.ruleId}</p>
                  <p className="mt-1 text-[11px] leading-relaxed text-text-secondary">{v.reason}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Matched rules & confidence */}
      {d.secrets.length > 0 && (
        <div className="rounded-xl border border-border-default bg-white/[0.02] p-4">
          <div className="mb-3 flex items-center gap-2">
            <Fingerprint className="h-4 w-4 text-status-critical" />
            <h4 className="text-sm font-semibold">Matched rule & pattern confidence</h4>
          </div>
          <div className="space-y-2.5">
            {d.secrets.map((s, i) => (
              <div key={i} className="flex items-center gap-3 rounded-lg bg-white/[0.02] p-2.5">
                <SeverityBadge severity={s.severity} />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between">
                    <span className="truncate text-xs font-medium text-text-primary">{s.label}</span>
                    <span className="mono text-[10px] text-text-muted">{(s.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div className="mt-1 h-1 overflow-hidden rounded-full bg-white/[0.05]">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${s.confidence * 100}%` }}
                      transition={{ duration: 0.6, delay: 0.1 + i * 0.05 }}
                      className="h-full rounded-full bg-gradient-to-r from-status-medium to-status-critical"
                    />
                  </div>
                  <p className="mono mt-1 truncate text-[10px] text-status-critical">{s.match}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Business impact */}
      <div className="rounded-xl border border-border-default bg-white/[0.02] p-4">
        <div className="mb-2 flex items-center gap-2">
          <Shield className="h-4 w-4 text-accent-light" />
          <h4 className="text-sm font-semibold">Business impact</h4>
        </div>
        <p className="text-xs leading-relaxed text-text-secondary">{businessImpact(d)}</p>
      </div>

      {/* Confidence visualization */}
      <div className="rounded-xl border border-border-default bg-white/[0.02] p-4">
        <div className="mb-3 flex items-center gap-2">
          <Zap className="h-4 w-4 text-accent-light" />
          <h4 className="text-sm font-semibold">Decision confidence</h4>
        </div>
        <div className="flex items-center gap-4">
          <div className="relative h-20 w-20">
            <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
              <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
              <motion.circle
                cx="50"
                cy="50"
                r="42"
                fill="none"
                stroke="#0ea79c"
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={`${Math.round(d.riskScore >= 15 ? Math.min(0.99, 0.75 + d.secrets.length * 0.04 + d.violations.length * 0.02) * 264 : 0.4 * 264)} 264`}
                initial={{ strokeDasharray: "0 264" }}
                animate={{ strokeDasharray: `${Math.round(d.riskScore >= 15 ? Math.min(0.99, 0.75 + d.secrets.length * 0.04 + d.violations.length * 0.02) * 264 : 0.4 * 264)} 264` }}
                transition={{ duration: 1, ease: "easeOut" }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="mono text-lg font-bold text-text-primary">
                {Math.round((d.riskScore >= 15 ? Math.min(0.99, 0.75 + d.secrets.length * 0.04 + d.violations.length * 0.02) : 0.4) * 100)}%
              </span>
              <span className="text-[8px] uppercase tracking-widest text-text-muted">conf</span>
            </div>
          </div>
          <div className="flex-1 space-y-1.5">
            {[
              { label: "Pattern confidence", v: d.secrets.length ? Math.round((d.secrets.reduce((a, s) => a + s.confidence, 0) / d.secrets.length) * 100) : 0 },
              { label: "Policy certainty", v: d.violations.length ? 97 : 82 },
              { label: "Composite score", v: d.riskScore },
            ].map((row) => (
              <div key={row.label} className="flex items-center gap-2">
                <span className="w-28 text-[10px] text-text-muted">{row.label}</span>
                <div className="h-1 flex-1 overflow-hidden rounded-full bg-white/[0.05]">
                  <motion.div initial={{ width: 0 }} animate={{ width: `${row.v}%` }} transition={{ duration: 0.7 }} className="h-full rounded-full bg-accent" />
                </div>
                <span className="mono w-8 text-right text-[10px] text-text-secondary">{row.v}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
