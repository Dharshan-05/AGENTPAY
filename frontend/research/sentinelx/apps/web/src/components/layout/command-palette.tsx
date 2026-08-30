"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import { AnimatePresence, motion } from "framer-motion"
import { useRouter } from "next/navigation"
import {
  Brain,
  Clapperboard,
  Command,
  FileBarChart,
  FileText,
  LayoutDashboard,
  MessageSquareText,
  Scale,
  Search,
  Settings,
  ShieldAlert,
  ClipboardCheck,
  ArrowRight,
  Bot,
  Activity,
  Landmark,
  Radar,
  Building2,
  ChartPie,
  Cpu,
  BrainCircuit,
} from "lucide-react"
import { cn } from "@/lib/utils"

const COMMANDS = [
  { group: "Navigate", items: [
    { label: "Executive Command Center", href: "/executive", icon: Landmark, keys: "G X" },
    { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard, keys: "G D" },
    { label: "Mission Control (SOC)", href: "/soc", icon: Radar, keys: "G O" },
    { label: "Prompt Scanner", href: "/scanner", icon: Search, keys: "G S" },
    { label: "Digital Twin", href: "/twin", icon: Building2, keys: "G W" },
    { label: "Security Intelligence", href: "/intelligence", icon: Brain, keys: "G I" },
    { label: "AI Explainability Center", href: "/explain", icon: BrainCircuit, keys: "G Q" },
    { label: "Enterprise Analytics", href: "/analytics", icon: ChartPie, keys: "G Y" },
    { label: "AI Copilot", href: "/copilot", icon: MessageSquareText, keys: "G C" },
    { label: "Presentation Mode", href: "/demo", icon: Clapperboard, keys: "G P" },
    { label: "Threat Timeline", href: "/threats", icon: ShieldAlert, keys: "G T" },
    { label: "Live Activity", href: "/activity", icon: Activity, keys: "G A" },
    { label: "Policies", href: "/policies", icon: FileText, keys: "G L" },
    { label: "Agents", href: "/agents", icon: Bot, keys: "G E" },
    { label: "Audit Logs", href: "/audit", icon: ClipboardCheck, keys: "G U" },
    { label: "Reports", href: "/reports", icon: FileBarChart, keys: "G R" },
    { label: "Compliance", href: "/compliance", icon: Scale, keys: "G M" },
    { label: "System", href: "/system", icon: Cpu, keys: "G N" },
    { label: "Settings", href: "/settings", icon: Settings, keys: "G K" },
  ]},
]

export function CommandPalette({ open, onClose }: { open: boolean; onClose: () => void }) {
  const router = useRouter()
  const [query, setQuery] = useState("")
  const [selected, setSelected] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (open) {
      setQuery("")
      setSelected(0)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [open])

  const flatItems = COMMANDS.flatMap((c) => c.items)
  const filtered = query
    ? flatItems.filter((i) => i.label.toLowerCase().includes(query.toLowerCase()))
    : flatItems

  useEffect(() => setSelected(0), [query])

  const go = useCallback((href: string) => {
    router.push(href)
    onClose()
  }, [router, onClose])

  const handleKey = useCallback((e: KeyboardEvent) => {
    if (!open) return
    if (e.key === "Escape") onClose()
    if (e.key === "ArrowDown") { e.preventDefault(); setSelected((s) => (filtered.length === 0 ? 0 : Math.min(s + 1, filtered.length - 1))) }
    if (e.key === "ArrowUp") { e.preventDefault(); setSelected((s) => Math.max(s - 1, 0)) }
    if (e.key === "Enter" && filtered[selected]) { e.preventDefault(); go(filtered[selected].href) }
  }, [open, filtered, selected, go, onClose])

  useEffect(() => {
    window.addEventListener("keydown", handleKey)
    return () => window.removeEventListener("keydown", handleKey)
  }, [handleKey])

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          role="dialog"
          aria-modal="true"
          aria-label="Command palette"
          className="fixed inset-0 z-[60] flex items-start justify-center bg-black/60 pt-[15vh] backdrop-blur-sm"
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: -8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: -8 }}
            transition={{ type: "spring", stiffness: 400, damping: 30 }}
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-lg overflow-hidden rounded-2xl border border-border-default bg-bg-secondary shadow-modal"
          >
            <div className="flex items-center gap-3 border-b border-border-subtle px-4 py-3">
              <Command className="h-4 w-4 text-accent-light" />
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                aria-label="Search pages"
                placeholder="Search pages and actions…"
                className="flex-1 bg-transparent text-sm text-text-primary outline-none placeholder:text-text-muted"
              />
              <kbd className="rounded border border-border-default px-1.5 py-0.5 text-[10px] text-text-muted">esc</kbd>
            </div>

            <div className="max-h-[45vh] overflow-y-auto p-2">
              {COMMANDS.map((group) => (
                <div key={group.group}>
                  <p className="px-3 pb-1.5 pt-2 text-[10px] font-semibold uppercase tracking-wider text-text-muted">{group.group}</p>
                  {filtered.map((item, i) => (
                    <button
                      key={item.href}
                      onClick={() => go(item.href)}
                      onMouseEnter={() => setSelected(i)}
                      className={cn(
                        "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition-colors",
                        i === selected ? "bg-accent/15 text-accent-light" : "text-text-secondary",
                      )}
                    >
                      <item.icon className={cn("h-4 w-4", i === selected ? "text-accent-light" : "text-text-muted")} />
                      <span className="flex-1">{item.label}</span>
                      {item.keys && (
                        <span className="flex items-center gap-0.5">
                          {item.keys.split(" ").map((k) => (
                            <kbd key={k} className="rounded border border-border-default px-1 text-[9px] text-text-muted">{k}</kbd>
                          ))}
                        </span>
                      )}
                      <ArrowRight className={cn("h-3 w-3", i === selected ? "opacity-100" : "opacity-0")} />
                    </button>
                  ))}
                </div>
              ))}
              {filtered.length === 0 && (
                <p className="px-3 py-8 text-center text-sm text-text-muted">No results for &quot;{query}&quot;</p>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}