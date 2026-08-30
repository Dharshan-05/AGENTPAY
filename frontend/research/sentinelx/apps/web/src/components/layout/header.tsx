"use client"

import { useEffect, useState } from "react"
import { Activity, Search, ShieldCheck, Wifi, Lock, Command, ChevronDown, UserCog, LogOut, User } from "lucide-react"
import { cn } from "@/lib/utils"
import { NotificationCenter } from "./notifications"
import { CommandPalette } from "./command-palette"
import { useRole } from "./role-context"
import { useAuth } from "@/lib/auth"
import { ROLES } from "@/lib/rbac"
import { useRouter } from "next/navigation"

export function Header() {
  const [now, setNow] = useState<Date | null>(null)
  const [online, setOnline] = useState(true)
  const [paletteOpen, setPaletteOpen] = useState(false)
  const [roleMenuOpen, setRoleMenuOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const { role, setRole, roleLabel } = useRole()
  const { user, logout } = useAuth()
  const router = useRouter()

  useEffect(() => {
    setNow(new Date())
    const t = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(t)
  }, [])

  useEffect(() => {
    let cancelled = false
    const check = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3001"}/api/health`,
          { cache: "no-store" },
        )
        const data = await res.json()
        if (!cancelled) setOnline(data.status === "ok")
      } catch {
        if (!cancelled) setOnline(false)
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
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault()
        setPaletteOpen((o) => !o)
      }
    }
    window.addEventListener("keydown", handler)
    return () => window.removeEventListener("keydown", handler)
  }, [])

  const handleLogout = async () => {
    await logout()
    router.push("/login")
  }

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border-subtle bg-bg-primary/80 px-6 backdrop-blur-xl">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-status-low opacity-60" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-status-low" />
          </span>
          <span className="text-xs font-medium text-text-secondary">All systems operational</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={() => setPaletteOpen(true)}
          aria-label="Open search and command palette (Cmd+K)"
          className="hidden items-center gap-2 rounded-lg border border-border-default bg-white/[0.02] px-3 py-1.5 text-[11px] text-text-muted transition-colors hover:border-border-strong hover:text-text-secondary md:flex"
        >
          <Search className="h-3.5 w-3.5" />
          Search…
          <kbd className="flex items-center gap-0.5 rounded border border-border-default px-1.5 py-0.5 text-[9px]">
            <Command className="h-2.5 w-2.5" />K
          </kbd>
        </button>

        <div className="relative">
          <button
            onClick={() => setRoleMenuOpen((o) => !o)}
            aria-label="Switch role"
            aria-expanded={roleMenuOpen}
            aria-haspopup="menu"
            className="flex items-center gap-2 rounded-lg border border-border-default bg-white/[0.02] px-3 py-1.5 text-[11px] text-text-secondary transition-colors hover:border-border-strong hover:text-text-primary"
          >
            <UserCog className="h-3.5 w-3.5 text-accent-light" />
            <span className="hidden sm:inline">{roleLabel}</span>
            <ChevronDown className={cn("h-3 w-3 text-text-muted transition-transform", roleMenuOpen && "rotate-180")} />
          </button>
          {roleMenuOpen && (
            <>
              <div className="fixed inset-0 z-40" onClick={() => setRoleMenuOpen(false)} />
              <div className="absolute right-0 z-50 mt-2 w-72 overflow-hidden rounded-xl border border-border-default bg-bg-elevated shadow-2xl">
                <div className="border-b border-border-subtle px-4 py-3">
                  <p className="text-[10px] uppercase tracking-widest text-text-muted">Demo · Switch identity</p>
                  <p className="mt-0.5 text-xs text-text-secondary">Each role sees a role-specific workspace.</p>
                </div>
                <div className="max-h-80 overflow-y-auto p-1.5">
                  {ROLES.map((r) => {
                    const active = role === r.id
                    return (
                      <button
                        key={r.id}
                        onClick={() => {
                          setRole(r.id)
                          setRoleMenuOpen(false)
                        }}
                        className={cn(
                          "flex w-full items-start gap-3 rounded-lg px-3 py-2.5 text-left transition-colors hover:bg-white/[0.04]",
                          active && "bg-accent/[0.08]",
                        )}
                      >
                        <span className={cn("mt-0.5 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-white/[0.04] text-[10px] font-bold", r.color)}>
                          {r.initials}
                        </span>
                        <span className="min-w-0">
                          <span className="flex items-center gap-2 text-xs font-medium text-text-primary">
                            {r.label}
                            {active && <span className="h-1.5 w-1.5 rounded-full bg-accent-light" />}
                          </span>
                          <span className="mt-0.5 block text-[10px] leading-snug text-text-muted">{r.tagline}</span>
                        </span>
                      </button>
                    )
                  })}
                </div>
              </div>
            </>
          )}
        </div>

        <div className="hidden items-center gap-2 rounded-lg border border-border-subtle bg-white/[0.02] px-3 py-1.5 lg:flex">
          <ShieldCheck className="h-3.5 w-3.5 text-accent-light" />
          <span className="text-[11px] text-text-muted">SOC 2 · GDPR · HIPAA · PCI DSS</span>
        </div>
        <div className="hidden items-center gap-2 text-xs text-text-muted sm:flex">
          <Activity className="h-3.5 w-3.5" />
          <span className="mono">
            {now?.toLocaleTimeString([], { hour12: false }) ?? ""}
          </span>
        </div>
        <NotificationCenter />
        <div
          role="status"
          aria-label={online ? "Live — all systems operational" : "Encrypted — degraded connection"}
          className={cn(
            "flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10px] font-medium",
            online
              ? "border-status-low/30 text-status-low"
              : "border-status-critical/30 text-status-critical",
          )}
        >
          {online ? <Wifi className="h-3 w-3" /> : <Lock className="h-3 w-3" />}
          {online ? "LIVE" : "ENCRYPTED"}
        </div>

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setUserMenuOpen((o) => !o)}
            aria-label="User menu"
            aria-expanded={userMenuOpen}
            aria-haspopup="menu"
            className="flex items-center gap-2 rounded-lg border border-border-default bg-white/[0.02] px-3 py-1.5 text-sm text-text-secondary transition-colors hover:border-border-strong hover:text-text-primary"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/15">
              <User className="h-4 w-4 text-accent-light" />
            </div>
            <span className="hidden sm:inline-block max-w-[120px] truncate">{user?.name ?? "User"}</span>
            <ChevronDown className={cn("h-3.5 w-3.5 text-text-muted transition-transform", userMenuOpen && "rotate-180")} />
          </button>
          {userMenuOpen && (
            <>
              <div className="fixed inset-0 z-40" onClick={() => setUserMenuOpen(false)} />
              <div className="absolute right-0 z-50 mt-2 w-56 overflow-hidden rounded-xl border border-border-default bg-bg-elevated shadow-2xl">
                <div className="border-b border-border-subtle px-4 py-3">
                  <p className="text-sm font-medium text-text-primary">{user?.name ?? "User"}</p>
                  <p className="mt-0.5 text-xs text-text-muted">{user?.email ?? ""}</p>
                </div>
                <div className="p-1.5">
                  <button
                    onClick={handleLogout}
                    className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm text-text-secondary transition-colors hover:bg-white/[0.04]"
                  >
                    <LogOut className="h-4 w-4" />
                    Sign out
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      <CommandPalette open={paletteOpen} onClose={() => setPaletteOpen(false)} />
    </header>
  )
}