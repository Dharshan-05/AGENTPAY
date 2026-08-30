"use client"

import { cn } from "@/lib/utils"
import {
  LayoutDashboard,
  Search,
  ShieldAlert,
  Shield,
  Activity,
  FileText,
  ClipboardCheck,
  FileBarChart,
  Scale,
  Bot,
  Settings,
  ChevronLeft,
  ChevronRight,
  Brain,
  MessageSquareText,
  Clapperboard,
  Landmark,
  Radar,
  Building2,
  ChartPie,
  Cpu,
  BrainCircuit,
  Flame,
  Users,
  Key,
} from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState, useEffect } from "react"
import { navAllowed, ROLE_BY_ID } from "@/lib/rbac"
import { useRole } from "./role-context"

const navigation = [
  { key: "executive", name: "Executive", href: "/executive", icon: Landmark },
  { key: "dashboard", name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { key: "soc", name: "Mission Control", href: "/soc", icon: Radar },
  { key: "incidents", name: "Incidents", href: "/incidents", icon: ShieldAlert },
  { key: "scanner", name: "Scanner", href: "/scanner", icon: Search },
  { key: "twin", name: "Digital Twin", href: "/twin", icon: Building2 },
  { key: "intelligence", name: "Intelligence", href: "/intelligence", icon: Brain },
  { key: "explain", name: "Explainability", href: "/explain", icon: BrainCircuit },
  { key: "analytics", name: "Analytics", href: "/analytics", icon: ChartPie },
  { key: "copilot", name: "Copilot", href: "/copilot", icon: MessageSquareText },
  { key: "demo", name: "Demo Mode", href: "/demo", icon: Clapperboard },
  { key: "threats", name: "Threats", href: "/threats", icon: Flame },
  { key: "activity", name: "Activity", href: "/activity", icon: Activity },
  { key: "policies", name: "Policies", href: "/policies", icon: FileText },
  { key: "agents", name: "Agents", href: "/agents", icon: Bot },
  { key: "audit", name: "Audit Logs", href: "/audit", icon: ClipboardCheck },
  { key: "reports", name: "Reports", href: "/reports", icon: FileBarChart },
  { key: "compliance", name: "Compliance", href: "/compliance", icon: Scale },
  { key: "admin", name: "Admin Control Center", href: "/admin", icon: Users },
  { key: "developer", name: "Developer Portal", href: "/developer", icon: Key },
  { key: "system", name: "System", href: "/system", icon: Cpu },
  { key: "settings", name: "Settings", href: "/settings", icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)
  const { role } = useRole()

  useEffect(() => {
    const stored = localStorage.getItem("sentinelx-sidebar")
    if (stored !== null) setCollapsed(stored === "true")
  }, [])

  const toggleCollapsed = () => {
    const next = !collapsed
    setCollapsed(next)
    localStorage.setItem("sentinelx-sidebar", String(next))
    window.dispatchEvent(new Event("sentinelx-sidebar-change"))
  }

  const visible = navigation.filter((item) => navAllowed(role, item.key))
  const roleDefObj = role ? ROLE_BY_ID.get(role) : undefined

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 flex h-screen flex-col border-r border-border-subtle bg-bg-primary/90 backdrop-blur-xl transition-all duration-300",
        collapsed ? "w-[72px]" : "w-[260px]",
      )}
    >
      <div className="flex h-16 items-center border-b border-border-subtle px-4">
        {!collapsed ? (
          <Link href="/dashboard" className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent shadow-glow">
              <Shield className="h-5 w-5 text-white" />
            </div>
            <div className="flex flex-col leading-tight">
              <span className="text-sm font-semibold tracking-tight text-text-primary">
                Sentinel<span className="text-accent-light">X</span>
              </span>
              <span className="text-[10px] uppercase tracking-widest text-text-muted">
                AI Governance Firewall
              </span>
            </div>
          </Link>
        ) : (
          <div className="mx-auto flex h-9 w-9 items-center justify-center rounded-lg bg-accent shadow-glow">
            <Shield className="h-5 w-5 text-white" />
          </div>
        )}
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {visible.map((item) => {
          const isActive =
            pathname === item.href || pathname.startsWith(item.href + "/")
          return (
            <Link
              key={item.href}
              href={item.href}
              title={collapsed ? item.name : undefined}
              aria-current={isActive ? "page" : undefined}
              className={cn(
                "group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-accent text-white shadow-glow"
                  : "text-text-secondary hover:bg-white/[0.04] hover:text-text-primary",
                collapsed && "justify-center px-2",
              )}
            >
              <item.icon
                className={cn(
                  "h-5 w-5 flex-shrink-0",
                  !isActive && "text-text-muted group-hover:text-text-secondary",
                )}
              />
              {!collapsed && <span>{item.name}</span>}
            </Link>
          )
        })}
      </nav>

      <div className="border-t border-border-subtle p-3">
        <div className={cn("mb-3 flex items-center gap-3 rounded-lg bg-white/[0.02] p-3", collapsed && "justify-center p-2")}>
          <div className={cn("flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold", roleDefObj?.color ?? "text-accent-light", "bg-white/[0.04]")}>
            {roleDefObj?.initials ?? "AM"}
          </div>
          {!collapsed && (
            <div className="min-w-0 leading-tight">
              <p className="truncate text-xs font-medium text-text-primary">{roleDefObj?.persona ?? "Aarav Mehta"}</p>
              <p className="truncate text-[10px] text-text-muted">{roleDefObj?.label ?? "Security Admin"}</p>
            </div>
          )}
        </div>
        <button
          onClick={toggleCollapsed}
          className={cn(
            "flex h-9 w-full items-center justify-center rounded-lg text-text-muted transition-colors hover:bg-white/[0.04] hover:text-text-primary",
          )}
          aria-label="Toggle sidebar"
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>
    </aside>
  )
}
