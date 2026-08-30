"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import { motion } from "framer-motion"
import {
  ArrowRight,
  Bot,
  Brain,
  Lightbulb,
  MemoryStick,
  RefreshCw,
  Send,
  Shield,
  Sparkles,
} from "lucide-react"
import { api } from "@/lib/api"
import type { CopilotSuggestion, LLMStatus } from "@/types"
import { Badge, PageHeader } from "@/components/ui/primitives"
import { CopilotDataCards } from "@/components/ui/copilot-cards"
import { cn } from "@/lib/utils"

interface Message {
  role: "user" | "assistant"
  content: string
  data?: unknown
  model?: string
  tokensUsed?: number
  simulated?: boolean
  memory?: { count: number; recalled: string | null }
}

const DEFAULT_SUGGESTIONS = [
  "Why was the last prompt blocked?",
  "Show today's highest-risk prompts",
  "Which policy triggered most violations this week?",
  "Recommend improvements for our security posture",
]

function renderAnswer(text: string): React.ReactNode {
  const lines = text.split("\n")
  const blocks: React.ReactNode[] = []
  let list: string[] = []
  let inList = false
  let tableRows: string[] = []
  let inTable = false

  const flushList = (key: number) => {
    if (inList) {
      blocks.push(
        <ul key={`list-${key}`} className="my-2 space-y-1.5">
          {list.map((item, i) => {
            const cleaned = item.replace(/^\s*[-*]\s+/, "").replace(/^\d+\.\s+/, "")
            return (
              <li key={i} className="flex items-start gap-2 text-xs leading-relaxed text-text-secondary">
                <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-accent-light" />
                {cleaned}
              </li>
            )
          })}
        </ul>,
      )
      list = []
      inList = false
    }
  }

  const flushTable = (key: number) => {
    if (inTable) {
      const rows = tableRows.filter((r) => !/^[\s|:-]+$/.test(r) && r.trim() !== "")
      const parsed = rows.map((r) => r.split("|").slice(1, -1).map((c) => c.trim()))
      if (parsed.length > 0) {
        const [header, ...body] = parsed
        blocks.push(
          <div key={`table-${key}`} className="my-2 overflow-x-auto rounded-lg border border-border-default">
            <table className="w-full text-left text-[11px]">
              <thead>
                <tr className="border-b border-border-default bg-white/[0.03]">
                  {header.map((h, i) => (
                    <th key={i} className="px-3 py-2 font-semibold text-text-primary">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {body.map((row, i) => (
                  <tr key={i} className="border-b border-border-subtle last:border-0">
                    {row.map((c, j) => (
                      <td key={j} className="px-3 py-1.5 text-text-secondary">{c}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>,
        )
      }
      tableRows = []
      inTable = false
    }
  }

  let idx = 0
  for (const rawLine of lines) {
    const line = rawLine.trim()
    if (!line) continue

    if (line.startsWith("|")) {
      if (!inTable) {
        flushList(idx++)
        flushTable(idx++)
        inTable = true
      }
      tableRows.push(line)
      continue
    }

    // Bold segments: **text**
    const rich = line.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
      part.startsWith("**") && part.endsWith("**") ? (
        <strong key={i} className="font-semibold text-text-primary">{part.slice(2, -2)}</strong>
      ) : (
        <span key={i}>{part}</span>
      ),
    )

    if (/^\s*[-*]\s+/.test(line) || /^\d+\.\s+/.test(line)) {
      if (!inList) {
        flushList(idx++)
        flushTable(idx++)
        inList = true
      }
      list.push(line)
    } else {
      flushList(idx++)
      flushTable(idx++)
      blocks.push(
        <p key={`p-${idx}`} className="my-1.5 text-xs leading-relaxed text-text-secondary">
          {rich}
        </p>,
      )
    }
  }
  flushList(idx++)
  flushTable(idx++)

  return <div>{blocks}</div>
}

export default function CopilotPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [thinking, setThinking] = useState(false)
  const [suggestions, setSuggestions] = useState<CopilotSuggestion[]>([])
  const [typedText, setTypedText] = useState("")
  const [llmStatus, setLlmStatus] = useState<LLMStatus | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const loadSuggestions = useCallback(async () => {
    try {
      const s = await api.copilotSuggestions()
      setSuggestions(s.slice(0, 5))
    } catch {
      setSuggestions(DEFAULT_SUGGESTIONS.map((t, i) => ({ id: `d${i}`, text: t })))
    }
  }, [])

  useEffect(() => {
    loadSuggestions()
    api.llmStatus().then(setLlmStatus).catch(() => setLlmStatus(null))
  }, [loadSuggestions])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, typedText, thinking])

  useEffect(() => () => {
    if (timerRef.current) clearTimeout(timerRef.current)
  }, [])

  const typeOut = useCallback((full: string, done: () => void) => {
    let i = 0
    const step = () => {
      i += 2
      setTypedText(full.slice(0, i))
      if (i < full.length) {
        timerRef.current = setTimeout(step, 16)
      } else {
        done()
      }
    }
    step()
  }, [])

  const send = useCallback(async (text?: string) => {
    const value = (text ?? input).trim()
    if (!value || thinking) return
    setInput("")
    const history = messages.slice(-10).map((m) => ({ role: m.role, content: m.content }))
    setMessages((prev) => [...prev, { role: "user", content: value }])
    setThinking(true)
    setTypedText("")
    try {
      const res = await api.copilot(value, history)
      const answer = res.answer ?? "No answer generated."
      setMessages((prev) => [...prev, { role: "assistant", content: "", data: res.data, model: res.model, tokensUsed: res.tokensUsed, simulated: res.simulated, memory: res.memory }])
      typeOut(answer, () => {
        setMessages((prev) => {
          const next = [...prev]
          const last = next[next.length - 1]
          if (last?.role === "assistant" && last.content === "") {
            next[next.length - 1] = { role: "assistant", content: answer, data: res.data, model: res.model, tokensUsed: res.tokensUsed, simulated: res.simulated, memory: res.memory }
          }
          return next
        })
        setTypedText("")
        setThinking(false)
      })
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", content: "I couldn't reach the SentinelX copilot engine. Please try again." }])
      setThinking(false)
    }
  }, [input, thinking, typeOut, messages])

  const displayedMessages = messages.map((m, i) => {
    if (i === messages.length - 1 && m.role === "assistant" && m.content === "") {
      return { ...m, content: typedText }
    }
    return m
  })

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Security Copilot"
        description="Ask questions about your security posture. SentinelX analyses the live audit chain to explain decisions, surface risks, and recommend actions."
        actions={
          <Badge variant="info">
            {llmStatus?.defaultProvider ? "AI-powered" : "Rule-based"} · audit driven
          </Badge>
        }
      />

      <div className="grid gap-4 lg:grid-cols-3">
        {/* Chat Panel */}
        <div className="glass-card flex flex-col overflow-hidden lg:col-span-2" style={{ height: "calc(100vh - 280px)", minHeight: 480 }}>
          {/* Header */}
          <div className="flex items-center justify-between border-b border-border-subtle px-5 py-3">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent shadow-glow">
                <Bot className="h-4 w-4 text-white" />
              </div>
              <div>
                <p className="text-xs font-semibold text-text-primary">SentinelX Copilot</p>
                <p className="text-[10px] text-text-muted">Analysing {messages.length === 0 ? "live audit data" : `${messages.length} messages`}</p>
              </div>
            </div>
            <Badge variant="success">Online</Badge>
          </div>

          {/* Messages */}
          <div className="flex-1 space-y-4 overflow-y-auto p-5" role="log" aria-live="polite">
            {messages.length === 0 && (
              <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
                <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="flex h-16 w-16 items-center justify-center rounded-2xl border border-accent/30 bg-accent/10 shadow-glow">
                  <Brain className="h-8 w-8 text-accent-light" />
                </motion.div>
                <div>
                  <p className="text-sm font-medium text-text-primary">How can I help secure your AI?</p>
                  <p className="mt-1 max-w-sm text-xs text-text-muted">
                    Ask about blocked prompts, high-risk activity, policy triggers, department risk, or security recommendations.
                  </p>
                </div>
                <div className="mt-2 flex flex-wrap items-center justify-center gap-2">
                  {suggestions.map((s) => (
                    <button
                      key={s.id}
                      onClick={() => send(s.text)}
                      className="group flex items-center gap-1.5 rounded-lg border border-border-default bg-white/[0.02] px-3 py-1.5 text-[11px] font-medium text-text-secondary transition-all hover:border-accent/50 hover:bg-accent/5 hover:text-text-primary hover:shadow-glow"
                    >
                      <Lightbulb className="h-3 w-3 text-accent-light" />
                      {s.text}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {displayedMessages.map((m, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className={cn("flex", m.role === "user" ? "justify-end" : "justify-start")}
              >
                {m.role === "assistant" && (
                  <div className="mr-2 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg bg-accent/15">
                    <Bot className="h-3.5 w-3.5 text-accent-light" />
                  </div>
                )}
                <div
                  className={cn(
                    "max-w-[85%] rounded-2xl px-4 py-3",
                    m.role === "user"
                      ? "rounded-br-sm border border-accent/30 bg-accent/10 text-xs text-text-primary"
                      : "rounded-bl-sm border border-border-default bg-white/[0.02]",
                  )}
                >
                  {m.role === "assistant" ? (
                    <>
                      {renderAnswer(m.content)}
                      {m.data != null && <CopilotDataCards data={m.data} />}
                      {(m.model || m.tokensUsed != null) && (
                        <div className="mt-2 flex flex-wrap items-center gap-2 border-t border-border-subtle pt-2">
                          {m.model && (
                            <span className="flex items-center gap-1 rounded-md bg-accent/10 px-1.5 py-0.5 text-[9px] font-medium text-accent-light">
                              <Sparkles className="h-2.5 w-2.5" />
                              {m.model}
                            </span>
                          )}
                          {m.simulated != null && (
                            <span className="rounded-md bg-white/[0.04] px-1.5 py-0.5 text-[9px] text-text-muted">
                              {m.simulated ? "simulated" : "live"}
                            </span>
                          )}
                          {m.tokensUsed != null && (
                            <span className="mono rounded-md bg-white/[0.04] px-1.5 py-0.5 text-[9px] text-text-muted">
                              {m.tokensUsed} tokens
                            </span>
                          )}
                          {m.memory && m.memory.recalled && (
                            <span className="flex items-center gap-1 rounded-md bg-status-info/10 px-1.5 py-0.5 text-[9px] text-status-info">
                              <MemoryStick className="h-2.5 w-2.5" />
                              recalled: {m.memory.recalled}
                            </span>
                          )}
                          {m.memory && !m.memory.recalled && m.memory.count > 0 && (
                            <span className="flex items-center gap-1 rounded-md bg-white/[0.04] px-1.5 py-0.5 text-[9px] text-text-muted">
                              <MemoryStick className="h-2.5 w-2.5" />
                              {m.memory.count} messages in context
                            </span>
                          )}
                        </div>
                      )}
                    </>
                  ) : (
                    <p className="whitespace-pre-wrap text-xs text-text-primary">{m.content}</p>
                  )}
                </div>
              </motion.div>
            ))}

            {thinking && messages[messages.length - 1]?.role !== "assistant" && (
              <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="flex items-start gap-2">
                <div className="mr-2 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg bg-accent/15">
                  <Bot className="h-3.5 w-3.5 text-accent-light" />
                </div>
                <div className="flex items-center gap-1.5 rounded-2xl rounded-bl-sm border border-border-default bg-white/[0.02] px-4 py-3">
                  <motion.span animate={{ opacity: [0.3, 1, 0.3] }} transition={{ duration: 1, repeat: Infinity }} className="h-1.5 w-1.5 rounded-full bg-accent-light" />
                  <motion.span animate={{ opacity: [0.3, 1, 0.3] }} transition={{ duration: 1, repeat: Infinity, delay: 0.2 }} className="h-1.5 w-1.5 rounded-full bg-accent-light" />
                  <motion.span animate={{ opacity: [0.3, 1, 0.3] }} transition={{ duration: 1, repeat: Infinity, delay: 0.4 }} className="h-1.5 w-1.5 rounded-full bg-accent-light" />
                </div>
              </motion.div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="border-t border-border-subtle p-4">
            <div className="flex items-center gap-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                aria-label="Ask the copilot"
                placeholder="Ask about your security posture…"
                className="max-h-32 flex-1 resize-none rounded-xl border border-border-default bg-bg-secondary/60 px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted outline-none transition-all focus:border-accent focus:shadow-glow"
              />
              <button
                onClick={() => send()}
                disabled={!input.trim() || thinking}
                className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-accent text-white shadow-glow transition-all hover:bg-accent-light disabled:cursor-not-allowed disabled:opacity-40"
                aria-label="Send message"
              >
                {thinking ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              </button>
            </div>
            <p className="mt-2 text-center text-[10px] text-text-muted">
              Enter to send · Shift+Enter for newline · Answers are grounded in live audit data{llmStatus?.defaultProvider ? ` · ${llmStatus.defaultProvider}` : ""}
            </p>
          </div>
        </div>

        {/* Side Panel */}
        <div className="space-y-4">
          <div className="glass-card card-glow border-accent/20 p-5">
            <div className="mb-3 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-accent-light" />
              <h2 className="text-sm font-semibold">AI Engine</h2>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between rounded-lg border border-border-default bg-white/[0.02] p-3">
                <span className="text-[11px] text-text-secondary">Mode</span>
                <Badge variant={llmStatus?.defaultProvider ? "success" : "info"}>
                  {llmStatus?.defaultProvider ? `AI · ${llmStatus.defaultProvider}` : "Rule-based fallback"}
                </Badge>
              </div>
              {(llmStatus?.providers ?? []).map((p) => (
                <div key={p.id} className="flex items-center justify-between rounded-lg border border-border-default bg-white/[0.02] px-3 py-2">
                  <span className="text-[11px] capitalize text-text-secondary">{p.id}</span>
                  <span className={cn("mono text-[10px]", p.configured ? "text-status-low" : "text-text-muted")}>
                    {p.configured ? "configured" : "not set"}
                  </span>
                </div>
              ))}
              <p className="text-[10px] leading-relaxed text-text-muted">
                Set an API key (e.g. OPENROUTER_API_KEY) in apps/api/.env to enable live AI answers. Without a key, the copilot answers from the deterministic rule engine.
              </p>
            </div>
          </div>

          <div className="glass-card card-glow p-5">
            <div className="mb-3 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-accent-light" />
              <h2 className="text-sm font-semibold">Capabilities</h2>
            </div>
            <div className="space-y-2">
              {[
                { icon: Shield, label: "Block reasoning", desc: "Why a prompt was blocked, rewritten or flagged" },
                { icon: Brain, label: "Risk triage", desc: "Highest-risk prompts and threat classification" },
                { icon: ArrowRight, label: "Policy insights", desc: "Which policies trigger most violations" },
                { icon: Lightbulb, label: "Recommendations", desc: "Concrete actions to strengthen posture" },
                { icon: Sparkles, label: "Department analytics", desc: "Risk exposure by org unit" },
              ].map((c, i) => (
                <motion.div key={c.label} initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className="flex items-start gap-3 rounded-lg border border-border-default bg-white/[0.02] p-3">
                  <c.icon className="mt-0.5 h-4 w-4 flex-shrink-0 text-accent-light" />
                  <div>
                    <p className="text-xs font-medium text-text-primary">{c.label}</p>
                    <p className="mt-0.5 text-[10px] leading-relaxed text-text-muted">{c.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          <div className="glass-card card-glow border-accent/20 p-5">
            <div className="mb-3 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-accent-light" />
              <h2 className="text-sm font-semibold">Executive Copilot</h2>
              <Badge variant="info">NEW</Badge>
            </div>
            <p className="mb-3 text-[10px] leading-relaxed text-text-muted">
              Telemetry-grounded answers for leadership — threats, posture, compliance and trends.
            </p>
            <div className="space-y-2">
              {[
                "Why did threats increase?",
                "Which department is highest risk?",
                "Show GDPR violations",
                "Compare today vs yesterday",
                "Generate an executive summary",
              ].map((q, i) => (
                <motion.button
                  key={q}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.04 }}
                  onClick={() => send(q)}
                  className="flex w-full items-center gap-2 rounded-lg border border-border-default bg-white/[0.02] px-3 py-2 text-left text-[11px] text-text-secondary transition-all hover:border-accent/50 hover:bg-accent/5 hover:text-text-primary"
                >
                  <span className="mono text-[9px] text-accent-light">{String(i + 1).padStart(2, "0")}</span>
                  <span className="flex-1">{q}</span>
                  <ArrowRight className="h-3 w-3 flex-shrink-0 text-text-muted" />
                </motion.button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}