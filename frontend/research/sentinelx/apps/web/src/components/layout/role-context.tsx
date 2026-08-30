"use client"

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react"
import type { RoleId } from "@/lib/rbac"
import { ROLES } from "@/lib/rbac"

interface RoleContextValue {
  role: RoleId | null
  setRole: (role: RoleId) => void
  roleLabel: string
  roleDef: (typeof ROLES)[number] | undefined
}

const RoleContext = createContext<RoleContextValue>({
  role: null,
  setRole: () => {},
  roleLabel: "Security Admin",
  roleDef: undefined,
});

export function RoleProvider({ children }: { children: React.ReactNode }) {
  const [role, setRoleState] = useState<RoleId | null>(null)

  useEffect(() => {
    const stored = localStorage.getItem("sentinelx-role")
    if (stored && ROLES.some((r) => r.id === stored)) setRoleState(stored as RoleId)
    const onStorage = () => {
      const next = localStorage.getItem("sentinelx-role")
      if (next && ROLES.some((r) => r.id === next)) setRoleState(next as RoleId)
    }
    window.addEventListener("sentinelx-role-change", onStorage)
    window.addEventListener("storage", onStorage)
    return () => {
      window.removeEventListener("sentinelx-role-change", onStorage)
      window.removeEventListener("storage", onStorage)
    }
  }, [])

  const setRole = useCallback((next: RoleId) => {
    localStorage.setItem("sentinelx-role", next)
    window.dispatchEvent(new Event("sentinelx-role-change"))
  }, [])

  const value = useMemo(() => {
    const roleDef = role ? ROLES.find((r) => r.id === role) : undefined
    return {
      role,
      setRole,
      roleLabel: roleDef?.label ?? "Security Admin",
      roleDef,
    }
  }, [role, setRole])

  return <RoleContext.Provider value={value}>{children}</RoleContext.Provider>
}

export function useRole(): RoleContextValue {
  return useContext(RoleContext)
}
